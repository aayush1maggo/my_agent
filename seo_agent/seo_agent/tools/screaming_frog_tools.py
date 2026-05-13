"""Utilities for running Screaming Frog SEO Spider via CLI."""
import csv
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from ..config import SCREAMING_FROG_CLI_PATH, SCREAMING_FROG_OUTPUT_DIR


def _ensure_output_dir(base_dir: Optional[str] = None) -> Path:
    """Create/return the folder where Screaming Frog exports will be stored."""
    if base_dir:
        target_dir = Path(base_dir).expanduser().resolve()
    else:
        target_dir = SCREAMING_FROG_OUTPUT_DIR

    target_dir.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="sf_crawl_", dir=target_dir))


def _find_response_codes_export(folder: Path) -> Optional[Path]:
    """Locate the response codes CSV exported by Screaming Frog."""
    patterns = [
        "response_codes.csv",
        "*response_codes*.csv",
        "internal_all.csv",  # fallback if response codes not requested
    ]

    for pattern in patterns:
        matches = list(folder.glob(pattern))
        if matches:
            return matches[0]

    # Deep search as a last resort
    for file in folder.rglob("*.csv"):
        if "response" in file.name.lower():
            return file

    return None


def _parse_4xx_entries(csv_path: Path) -> List[Dict[str, Any]]:
    """Return rows that have a 4xx status code."""
    results: List[Dict[str, Any]] = []

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get("Status Code") or row.get("Status")
            if not status:
                continue
            try:
                status_code = int(status)
            except ValueError:
                continue
            if 400 <= status_code < 500:
                results.append({
                    "url": row.get("Address") or row.get("URL"),
                    "status_code": status_code,
                    "status_text": row.get("Status") or "",
                    "inlinks": row.get("Inlinks") or row.get("Inlinks Count"),
                })
    return results


def run_screaming_frog_404_report(
    target_url: str,
    output_dir: Optional[str] = None,
    timeout_seconds: int = 900
) -> Dict[str, Any]:
    """Run Screaming Frog CLI and return the list of 4xx URLs.

    Args:
        target_url: The domain or URL to crawl (e.g., https://example.com).
        output_dir: Optional folder for crawl exports.
        timeout_seconds: CLI timeout (default 15 minutes).

    Returns:
        Dict containing crawl metadata, CSV file path, and filtered 4xx results.
    """
    cli_path = Path(SCREAMING_FROG_CLI_PATH) if SCREAMING_FROG_CLI_PATH else None
    if not cli_path or not cli_path.exists():
        return {
            "status": "error",
            "error": (
                "Screaming Frog CLI not found. Set SCREAMING_FROG_CLI_PATH in .env "
                "to the ScreamingFrogSEOSpiderCli executable."
            ),
        }

    if not target_url:
        return {
            "status": "error",
            "error": "target_url is required."
        }

    crawl_dir = _ensure_output_dir(output_dir)
    command = [
        str(cli_path),
        "--crawl", target_url,
        "--headless",
        "--output-folder", str(crawl_dir),
        "--export-tabs", "Response Codes:All",
        "--export-format", "csv",
        "--overwrite"
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError:
        return {
            "status": "error",
            "error": f"Unable to execute Screaming Frog CLI at {cli_path}",
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": f"Screaming Frog crawl timed out after {timeout_seconds} seconds.",
            "output_folder": str(crawl_dir),
        }

    if result.returncode != 0:
        return {
            "status": "error",
            "error": "Screaming Frog CLI exited with errors.",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    csv_path = _find_response_codes_export(crawl_dir)
    if not csv_path:
        return {
            "status": "error",
            "error": "Unable to locate Response Codes export.",
            "output_folder": str(crawl_dir),
            "stdout": result.stdout,
        }

    errors = _parse_4xx_entries(csv_path)

    return {
        "status": "success",
        "target": target_url,
        "output_folder": str(crawl_dir),
        "response_codes_csv": str(csv_path),
        "total_4xx": len(errors),
        "sample_4xx": errors[:20],
        "errors": errors,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def _collect_csv_exports(folder: Path) -> List[Dict[str, Any]]:
    """Return a list of {tab, file, row_count} for every CSV in folder."""
    exports = []
    for csv_file in sorted(folder.rglob("*.csv")):
        try:
            with csv_file.open(newline="", encoding="utf-8-sig") as f:
                row_count = sum(1 for _ in csv.reader(f)) - 1  # subtract header
        except Exception:
            row_count = -1
        exports.append({
            "tab": csv_file.stem,
            "file": str(csv_file),
            "row_count": max(row_count, 0),
        })
    return exports


def run_screaming_frog_full_audit(
    target_url: str,
    export_tabs: str = "Internal:All,Response Codes:All,Titles:Missing,Meta Description:Missing",
    output_dir: Optional[str] = None,
    timeout_seconds: int = 1800,
) -> Dict[str, Any]:
    """Run Screaming Frog CLI with arbitrary export tabs and return structured results.

    Generalises run_screaming_frog_404_report to accept any export-tabs value,
    making it suitable for full site audits on large sites (> 200 pages) where
    the Python crawler would be too slow.

    Args:
        target_url: Domain or URL to crawl (e.g., https://example.com).
        export_tabs: Comma-separated Screaming Frog tab/filter pairs, e.g.
            "Internal:All,Response Codes:4xx,Titles:Missing,Meta Description:Missing".
        output_dir: Optional folder for crawl exports; uses configured default if None.
        timeout_seconds: CLI timeout in seconds (default 30 minutes).

    Returns:
        Dict with status, target, output_folder, exports (list of CSV files with
        row counts), total_urls_found (sum of all internal rows), and CLI output.
    """
    cli_path = Path(SCREAMING_FROG_CLI_PATH) if SCREAMING_FROG_CLI_PATH else None
    if not cli_path or not cli_path.exists():
        return {
            "status": "error",
            "error": (
                "Screaming Frog CLI not found. Set SCREAMING_FROG_CLI_PATH in .env "
                "to the ScreamingFrogSEOSpiderCli executable."
            ),
        }

    if not target_url:
        return {"status": "error", "error": "target_url is required."}

    crawl_dir = _ensure_output_dir(output_dir)
    command = [
        str(cli_path),
        "--crawl", target_url,
        "--headless",
        "--output-folder", str(crawl_dir),
        "--export-tabs", export_tabs,
        "--export-format", "csv",
        "--overwrite",
    ]

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError:
        return {
            "status": "error",
            "error": f"Unable to execute Screaming Frog CLI at {cli_path}",
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": f"Screaming Frog crawl timed out after {timeout_seconds} seconds.",
            "output_folder": str(crawl_dir),
        }

    if proc.returncode != 0:
        return {
            "status": "error",
            "error": "Screaming Frog CLI exited with errors.",
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    exports = _collect_csv_exports(crawl_dir)
    total_rows = sum(e["row_count"] for e in exports)

    # Surface a quick 4xx summary if the response codes export is present
    four_xx_summary: List[Dict[str, Any]] = []
    rc_export = next(
        (e for e in exports if "response_code" in e["tab"].lower()),
        None,
    )
    if rc_export:
        try:
            four_xx_summary = _parse_4xx_entries(Path(rc_export["file"]))[:20]
        except Exception:
            pass

    return {
        "status": "success",
        "target": target_url,
        "output_folder": str(crawl_dir),
        "export_tabs_requested": export_tabs,
        "exports": exports,
        "total_rows_across_exports": total_rows,
        "sample_4xx": four_xx_summary,
        "total_4xx": len(four_xx_summary),
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }
