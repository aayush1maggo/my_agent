"""Robots.txt analysis tools for technical SEO.

These tools fetch and analyze a site's robots.txt file and return
structured data plus machine-detectable issues and recommendations
so the Technical SEO agent (TechAuditor) can suggest optimizations.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse

import requests


def _normalize_site_url(site_url: str) -> Optional[str]:
    """Normalize an input URL or hostname to a robots.txt URL.

    Accepts:
    - Full URLs like https://example.com/page
    - Bare domains like example.com
    - URLs with paths or query strings

    Returns:
    - robots.txt URL (e.g., https://example.com/robots.txt) or None if invalid.
    """
    if not site_url:
        return None

    site_url = site_url.strip()

    # Add scheme for bare domains
    if "://" not in site_url:
        site_url = f"https://{site_url}"

    parsed = urlparse(site_url)
    if not parsed.netloc:
        return None

    scheme = parsed.scheme or "https"
    netloc = parsed.netloc
    return f"{scheme}://{netloc}/robots.txt"


def _parse_robots(content: str) -> Dict[str, Any]:
    """Parse robots.txt content into structured groups.

    The parser is intentionally simple and conservative – it does not
    try to fully implement precedence rules. Instead, it exposes the
    structure so the LLM can reason using Google's documentation.
    """
    groups: List[Dict[str, Any]] = []
    global_sitemaps: List[str] = []

    current_group: Optional[Dict[str, Any]] = None

    def start_new_group() -> Dict[str, Any]:
        return {
            "user_agents": [],
            "allow": [],
            "disallow": [],
            "crawl_delay": None,
            "sitemaps": [],
            "other_directives": [],
        }

    for raw_line in content.splitlines():
        # Strip comments and whitespace
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Remove inline comments (# ...)
        if "#" in line:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue

        if ":" not in line:
            continue

        directive, value = line.split(":", 1)
        directive = directive.strip().lower()
        value = value.strip()

        if directive == "user-agent":
            # Start a new group if the current group already has directives
            if current_group is None:
                current_group = start_new_group()
            elif (
                current_group["allow"]
                or current_group["disallow"]
                or current_group["crawl_delay"] is not None
                or current_group["sitemaps"]
                or current_group["other_directives"]
            ):
                groups.append(current_group)
                current_group = start_new_group()

            if value:
                current_group["user_agents"].append(value)
            continue

        # For any directive other than user-agent, ensure we have a group
        if current_group is None:
            current_group = start_new_group()

        if directive == "allow":
            if value:
                current_group["allow"].append(value)
        elif directive == "disallow":
            # Disallow with empty value means "allow all" – still record it
            current_group["disallow"].append(value)
        elif directive in ("crawl-delay", "crawl_delay"):
            current_group["crawl_delay"] = value
        elif directive == "sitemap":
            if value:
                current_group["sitemaps"].append(value)
                global_sitemaps.append(value)
        else:
            current_group["other_directives"].append(
                {"name": directive, "value": value}
            )

    if current_group is not None:
        groups.append(current_group)

    has_wildcard_group = any(
        "*" in [ua.lower() for ua in group["user_agents"]]
        for group in groups
    )

    return {
        "groups": groups,
        "has_wildcard_group": has_wildcard_group,
        "sitemaps": list(dict.fromkeys(global_sitemaps)),  # de-duplicate
    }


def _detect_issues(parsed: Dict[str, Any]) -> Tuple[List[str], List[str], List[str], Dict[str, Any]]:
    """Detect issues, warnings, and recommendations from parsed robots.txt."""
    issues: List[str] = []
    warnings: List[str] = []
    recommendations: List[str] = []

    groups: List[Dict[str, Any]] = parsed.get("groups", [])

    # Summary flags
    has_wildcard_group = parsed.get("has_wildcard_group", False)
    sitemap_count = len(parsed.get("sitemaps", []))

    uses_crawl_delay = any(
        bool(group.get("crawl_delay")) for group in groups
    )

    # Check for wildcard group and disallow-all patterns
    disallow_all_for_all_agents = False
    disallow_all_for_googlebot = False

    for group in groups:
        user_agents = [ua.lower() for ua in group.get("user_agents", [])]
        disallows = group.get("disallow", [])

        # Disallow: / means block all paths
        if any(rule.strip() == "/" for rule in disallows):
            if "*" in user_agents:
                disallow_all_for_all_agents = True
            if any("googlebot" == ua or ua.startswith("googlebot-") for ua in user_agents):
                disallow_all_for_googlebot = True

        # Warn about patterns that likely block important resources
        resource_block_patterns = [".css", ".js", "/static", "/assets", "/wp-includes"]
        for rule in disallows:
            lower_rule = rule.lower()
            if any(p in lower_rule for p in resource_block_patterns):
                warnings.append(
                    f"Disallow rule '{rule}' may block important resources (CSS/JS/static assets) needed for rendering."
                )

        # Note non-standard directives
        for directive in group.get("other_directives", []):
            name = directive.get("name", "").lower()
            if name == "host":
                warnings.append(
                    "Found 'Host' directive. Some search engines ignore this; rely on canonical URLs and redirects instead."
                )
            else:
                recommendations.append(
                    f"Robots.txt includes non-standard directive '{directive.get('name')}'. "
                    "Ensure it is needed and supported by your target crawlers."
                )

    if not has_wildcard_group:
        warnings.append(
            "No 'User-agent: *' group found. Consider adding a default group to define baseline crawl rules."
        )

    if disallow_all_for_all_agents:
        issues.append(
            "Robots.txt blocks all crawling for all user agents (Disallow: / under User-agent: *). "
            "This prevents search engines from accessing any page."
        )

    if disallow_all_for_googlebot:
        issues.append(
            "Robots.txt blocks all crawling for Googlebot (Disallow: /). "
            "This prevents Google from accessing your content."
        )

    if uses_crawl_delay:
        recommendations.append(
            "Robots.txt uses Crawl-delay. Google does not support this directive; "
            "use Search Console crawl rate settings instead if you need to adjust crawl frequency."
        )

    if sitemap_count == 0:
        recommendations.append(
            "No Sitemap URLs declared in robots.txt. If you have an XML sitemap, "
            "add 'Sitemap: https://example.com/sitemap.xml' to help crawlers discover it."
        )

    summary = {
        "has_wildcard_group": has_wildcard_group,
        "group_count": len(groups),
        "sitemap_count": sitemap_count,
        "uses_crawl_delay": uses_crawl_delay,
        "disallow_all_for_all_agents": disallow_all_for_all_agents,
        "disallow_all_for_googlebot": disallow_all_for_googlebot,
    }

    return issues, warnings, recommendations, summary


def analyze_robots_txt(site_url: str) -> Dict[str, Any]:
    """Fetch and analyze a site's robots.txt file.

    Args:
        site_url: Any URL or hostname for the site (e.g., 'https://example.com',
                  'example.com', 'https://example.com/page').

    Returns:
        Dict with status, summary, parsed groups, issues, warnings, and
        recommendations suitable for LLM-driven technical SEO analysis.
    """
    robots_url = _normalize_site_url(site_url)
    if not robots_url:
        return {
            "status": "error",
            "site_url": site_url,
            "robots_url": None,
            "message": "Could not derive robots.txt URL from the provided site URL.",
        }

    result: Dict[str, Any] = {
        "status": "success",
        "site_url": site_url,
        "robots_url": robots_url,
        "analyzed_at": datetime.now().isoformat(),
        "http_status": None,
        "summary": {},
        "parsed": {},
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    try:
        response = requests.get(robots_url, timeout=15)
        result["http_status"] = response.status_code

        if response.status_code == 404:
            result["status"] = "missing"
            result["message"] = (
                "robots.txt not found (404). Without a robots.txt file, crawlers will usually "
                "assume they are allowed to crawl all URLs. Consider adding a robots.txt file "
                "to document crawl rules explicitly."
            )
            return result

        if response.status_code >= 400:
            result["status"] = "error"
            result["message"] = (
                f"Failed to fetch robots.txt (HTTP {response.status_code}). "
                "Check server availability and permissions."
            )
            return result

        content = response.text or ""

        parsed = _parse_robots(content)
        issues, warnings, recommendations, summary = _detect_issues(parsed)

        result["parsed"] = parsed
        result["summary"] = summary
        result["issues"] = issues
        result["warnings"] = warnings
        result["recommendations"] = recommendations

        if not content.strip():
            result["warnings"].append(
                "robots.txt is empty. Crawlers will generally treat this as 'allow all', "
                "but you may want to add explicit rules."
            )

        return result

    except Exception as exc:
        result["status"] = "error"
        result["message"] = f"Error fetching or analyzing robots.txt: {exc}"
        return result


def get_robots_txt_summary(site_url: str) -> Dict[str, Any]:
    """Get a lightweight summary of robots.txt for a site.

    This is a cheaper alternative to full analysis and is useful for
    quick routing or sanity checks.
    """
    robots_url = _normalize_site_url(site_url)
    if not robots_url:
        return {
            "status": "error",
            "site_url": site_url,
            "robots_url": None,
            "message": "Could not derive robots.txt URL from the provided site URL.",
        }

    try:
        response = requests.get(robots_url, timeout=15)
        http_status = response.status_code

        if http_status == 404:
            return {
                "status": "missing",
                "site_url": site_url,
                "robots_url": robots_url,
                "http_status": http_status,
                "message": "robots.txt not found (404).",
            }

        if http_status >= 400:
            return {
                "status": "error",
                "site_url": site_url,
                "robots_url": robots_url,
                "http_status": http_status,
                "message": f"Failed to fetch robots.txt (HTTP {http_status}).",
            }

        content = response.text or ""
        parsed = _parse_robots(content)

        agents_covered: List[str] = []
        for group in parsed.get("groups", []):
            for ua in group.get("user_agents", []):
                if ua not in agents_covered:
                    agents_covered.append(ua)

        sample_disallow: List[str] = []
        for group in parsed.get("groups", []):
            for rule in group.get("disallow", []):
                if rule and rule not in sample_disallow:
                    sample_disallow.append(rule)
                if len(sample_disallow) >= 5:
                    break
            if len(sample_disallow) >= 5:
                break

        return {
            "status": "success",
            "site_url": site_url,
            "robots_url": robots_url,
            "http_status": http_status,
            "has_wildcard_group": parsed.get("has_wildcard_group", False),
            "group_count": len(parsed.get("groups", [])),
            "agents_covered": agents_covered,
            "sitemaps": parsed.get("sitemaps", []),
            "sample_disallow": sample_disallow,
        }

    except Exception as exc:
        return {
            "status": "error",
            "site_url": site_url,
            "robots_url": robots_url,
            "message": f"Error fetching or summarizing robots.txt: {exc}",
        }

