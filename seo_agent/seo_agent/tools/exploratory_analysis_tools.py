"""Generic exploratory data analysis and visualization tools.

These tools operate on arbitrary tabular data provided as a list of
row dictionaries. They do not fetch data themselves; instead, they
are intended to analyze data that has already been retrieved in the
current session (for example, GA4 results, Search Console outputs,
or spreadsheet rows).
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


DEFAULT_ANALYSIS_CHART_DIR = Path("analysis_charts")


def _ensure_output_path(filename: Optional[str]) -> Path:
    """Ensure the output directory exists and return a full path."""
    DEFAULT_ANALYSIS_CHART_DIR.mkdir(parents=True, exist_ok=True)

    if filename:
        return DEFAULT_ANALYSIS_CHART_DIR / filename

    # Keep filenames simple; callers can provide explicit names when needed.
    return DEFAULT_ANALYSIS_CHART_DIR / "analysis_chart.png"


def _rows_to_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert a list of row dicts into a pandas DataFrame."""
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def summarize_tabular_data(
    rows: List[Dict[str, Any]],
    numeric_columns: Optional[List[str]] = None,
    group_by: Optional[List[str]] = None,
    top_n: int = 20,
) -> Dict[str, Any]:
    """Summarize numeric columns in tabular data.

    Args:
        rows: List of row dictionaries (e.g., from a previous tool result).
        numeric_columns: Optional list of numeric column names to focus on.
        group_by: Optional list of columns to group by before summarizing.
        top_n: Maximum number of groups to include in the grouped summary.

    Returns:
        Dict with summary statistics that is JSON-serializable.
    """
    df = _rows_to_dataframe(rows)
    if df.empty:
        return {"error": "No data provided for summarization.", "summary": {}}

    if numeric_columns:
        numeric_cols = [col for col in numeric_columns if col in df.columns]
    else:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if not numeric_cols:
        return {
            "error": "No numeric columns found for summarization.",
            "summary": {},
        }

    summary: Dict[str, Any] = {}

    if group_by:
        group_cols = [col for col in group_by if col in df.columns]
        if group_cols:
            grouped = df.groupby(group_cols)[numeric_cols]
            agg_df = grouped.agg(["count", "mean", "sum", "min", "max", "std"])
            # Limit the number of groups for readability
            if len(agg_df) > top_n:
                agg_df = agg_df.head(top_n)
            summary["grouped_summary"] = agg_df.reset_index().to_dict(
                orient="records"
            )

    # Overall summary (no grouping)
    describe_df = df[numeric_cols].describe(include="all")
    summary["overall_summary"] = describe_df.to_dict()

    return {
        "summary": summary,
        "numeric_columns": numeric_cols,
        "group_by": group_by or [],
        "row_count": int(len(df)),
    }


def compute_correlation_matrix(
    rows: List[Dict[str, Any]],
    numeric_columns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Compute a correlation matrix for numeric columns.

    Args:
        rows: List of row dictionaries with numeric values.
        numeric_columns: Optional list of numeric column names to include.

    Returns:
        Dict with a correlation matrix suitable for downstream analysis.
    """
    df = _rows_to_dataframe(rows)
    if df.empty:
        return {"error": "No data provided for correlation matrix.", "correlations": {}}

    if numeric_columns:
        numeric_cols = [col for col in numeric_columns if col in df.columns]
    else:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if not numeric_cols:
        return {
            "error": "No numeric columns found for correlation matrix.",
            "correlations": {},
        }

    corr_df = df[numeric_cols].corr()

    return {
        "correlations": corr_df.to_dict(),
        "numeric_columns": numeric_cols,
    }


def plot_tabular_data(
    rows: List[Dict[str, Any]],
    x: str,
    y: str,
    kind: str = "line",
    hue: Optional[str] = None,
    output_filename: Optional[str] = None,
) -> Dict[str, Any]:
    """Plot tabular data using seaborn/matplotlib.

    Args:
        rows: List of row dictionaries representing tabular data.
        x: Name of the column to use for the x-axis.
        y: Name of the column to use for the y-axis.
        kind: Type of chart ('line', 'bar', 'scatter', or 'box').
        hue: Optional column to use for grouping/coloring.
        output_filename: Optional filename; saved under analysis_charts/.

    Returns:
        Dict with chart_path and basic metadata, or error details.
    """
    df = _rows_to_dataframe(rows)
    if df.empty:
        return {"error": "No data provided for plotting."}

    if x not in df.columns or y not in df.columns:
        return {
            "error": "Missing required columns for plotting.",
            "missing_columns": [
                col for col in (x, y) if col not in df.columns
            ],
        }

    if hue and hue not in df.columns:
        hue = None

    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 6))

    kind = kind.lower()
    if kind == "line":
        ax = sns.lineplot(data=df, x=x, y=y, hue=hue)
    elif kind == "bar":
        ax = sns.barplot(data=df, x=x, y=y, hue=hue)
    elif kind == "scatter":
        ax = sns.scatterplot(data=df, x=x, y=y, hue=hue)
    elif kind == "box":
        ax = sns.boxplot(data=df, x=x, y=y, hue=hue)
    else:
        return {"error": f"Unsupported chart type: {kind}"}

    ax.set_xlabel(x)
    ax.set_ylabel(y)
    title_parts = [f"{kind.title()} plot of {y} vs {x}"]
    if hue:
        title_parts.append(f"(grouped by {hue})")
    ax.set_title(" ".join(title_parts))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_path = _ensure_output_path(output_filename)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    return {
        "chart_path": str(output_path),
        "x": x,
        "y": y,
        "kind": kind,
        "hue": hue,
        "row_count": int(len(df)),
    }

