"""SERP Ranking Tools — powered by DataForSEO Google Organic SERP API.

Provides live Google ranking checks, SERP feature analysis, and multi-domain
comparisons. Uses DataForSEO /serp/google/organic/live/advanced endpoint with
Basic auth (login + password).

All functions return {"status": "success"|"error", ...} dicts and never raise.
"""
import base64
import csv
from typing import Dict, List, Optional, Any

import requests

from ..config import (
    DATAFORSEO_LOGIN,
    DATAFORSEO_PASSWORD,
    DATAFORSEO_SERP_URL,
    DATAFORSEO_LOCATION_CODES_CSV,
)


_DFS_TIMEOUT = 30  # seconds

# ---------------------------------------------------------------------------
# Location code lookup — loaded once at import time from the reference CSV
# ---------------------------------------------------------------------------
# Maps lowercase location_name and country_iso_code → {location_code, default_language_code}
# Prefers English rows when a country has multiple language entries.
_LOCATION_LOOKUP: Dict[str, Dict] = {}

def _load_location_lookup() -> None:
    try:
        with open(DATAFORSEO_LOCATION_CODES_CSV, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                code = int(row['location_code'])
                name_key = row['location_name'].strip().lower()
                iso_key = row['country_iso_code'].strip().lower()
                lang = row['language_code'].strip()
                entry = {'location_code': code, 'default_language_code': lang}
                # Store by name and ISO; prefer English entries when a country
                # has multiple language rows (e.g. India: en + hi)
                if name_key not in _LOCATION_LOOKUP or lang == 'en':
                    _LOCATION_LOOKUP[name_key] = entry
                if iso_key not in _LOCATION_LOOKUP or lang == 'en':
                    _LOCATION_LOOKUP[iso_key] = entry
    except Exception:
        pass  # Graceful fallback — tools still work using location_name strings

_load_location_lookup()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _auth_headers() -> Dict[str, str]:
    credentials = base64.b64encode(
        f"{DATAFORSEO_LOGIN}:{DATAFORSEO_PASSWORD}".encode()
    ).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }


def _check_credentials() -> Optional[str]:
    """Return an error message string if credentials are missing, else None."""
    if not DATAFORSEO_LOGIN or not DATAFORSEO_PASSWORD:
        return (
            "DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD are not configured. "
            "Add them to seo_agent/.env."
        )
    return None


def _normalise_language_code(language_code: str) -> str:
    """DataForSEO only accepts simple 2-letter codes (e.g. 'en', 'fr').
    Strip any locale suffix so 'en_AU', 'en-AU', 'en_GB' all become 'en'.
    """
    return language_code.replace("-", "_").split("_")[0].lower()


def _resolve_location(location: str, language_code: str) -> Dict[str, Any]:
    """Return the correct DataForSEO location + language payload fields.

    Looks up the location in the reference CSV to use an integer location_code
    (more reliable than location_name strings). Falls back to location_name if
    the location isn't in the CSV.

    Examples:
      "Australia"     → {location_code: 2036, language_code: "en"}
      "AU"            → {location_code: 2036, language_code: "en"}
      "United States" → {location_code: 2840, language_code: "en"}
      "somewhere new" → {location_name: "somewhere new", language_code: "en"}
    """
    lang = _normalise_language_code(language_code)
    entry = _LOCATION_LOOKUP.get(location.strip().lower())
    if entry:
        return {"location_code": entry["location_code"], "language_code": lang}
    return {"location_name": location, "language_code": lang}


def _serp_request(tasks: List[Dict]) -> Dict[str, Any]:
    """POST a batch of tasks to DataForSEO and return the parsed JSON or error dict."""
    try:
        resp = requests.post(
            DATAFORSEO_SERP_URL,
            headers=_auth_headers(),
            json=tasks,
            timeout=_DFS_TIMEOUT,
        )
        if not resp.ok:
            return {"error": f"DataForSEO API error {resp.status_code}: {resp.text[:300]}"}
        return resp.json()
    except requests.RequestException as exc:
        return {"error": f"DataForSEO request failed: {exc}"}


def _task_items(data: Dict, task_index: int = 0) -> Optional[List[Dict]]:
    """Extract the items[] list for a given task index. Returns None on failure."""
    try:
        task = data["tasks"][task_index]
        if task.get("status_code") != 20000:
            return None
        return task["result"][0]["items"]
    except (KeyError, IndexError, TypeError):
        return None


def _task_error(data: Dict, task_index: int = 0) -> str:
    """Return a human-readable error for a failed task."""
    try:
        task = data["tasks"][task_index]
        return f"DataForSEO task error {task.get('status_code')}: {task.get('status_message', 'unknown')}"
    except (KeyError, IndexError):
        return "DataForSEO returned an unexpected response structure."


def _organic_items(items: List[Dict]) -> List[Dict]:
    return [i for i in items if i.get("type") == "organic"]


def _serp_features_summary(items: List[Dict]) -> Dict[str, bool]:
    types = {i.get("type") for i in items}
    return {
        "knowledge_graph": "knowledge_graph" in types,
        "featured_snippet": "featured_snippet" in types,
        "people_also_ask": "people_also_ask" in types,
        "related_searches": "related_searches" in types,
    }


def _domain_match(target_domain: str, item: Dict) -> bool:
    """Return True if item's URL or domain contains target_domain."""
    t = target_domain.lower()
    return t in item.get("url", "").lower() or t in item.get("domain", "").lower()


def _generate_serp_recommendations(features: Dict, competition_level: str) -> List[str]:
    recs = []
    if features["featured_snippet"]:
        recs.append(
            "Featured snippet present — structure a concise 40–60 word answer "
            "near the top of your page with clear H2/H3 headings to target it."
        )
    if features["knowledge_graph"]:
        recs.append(
            "Knowledge graph present — focus on brand authority and structured data "
            "to strengthen entity association."
        )
    if features["people_also_ask"] and len(features["people_also_ask"]) > 0:
        recs.append(
            f"Found {len(features['people_also_ask'])} PAA questions — "
            "add an FAQ section addressing these to capture PAA placements."
        )
    if competition_level == "high":
        recs.append(
            "High competition — target long-tail variations, build topical authority, "
            "and differentiate with unique data or perspective."
        )
    elif competition_level == "low":
        recs.append(
            "Low competition — good opportunity; comprehensive quality content "
            "should rank with moderate link building."
        )
    if features["related_searches"]:
        recs.append("Use related searches to expand content coverage and internal linking opportunities.")
    return recs


# ---------------------------------------------------------------------------
# Public Tool Functions
# ---------------------------------------------------------------------------

def get_keyword_ranking(
    keyword: str,
    target_domain: str,
    location: str = "United States",
    language_code: str = "en",
    num_results: int = 100,
) -> Dict:
    """Check where a domain ranks on Google for a specific keyword (live, real-time).

    Uses DataForSEO SERP API to fetch the top organic results and locate
    the target domain's position.

    Args:
        keyword: The search query to check (e.g. "best SEO tools").
        target_domain: The domain to find in results (e.g. "ahrefs.com"). No protocol needed.
        location: Full location name for geo-targeting (e.g. "United States",
                  "Melbourne,Victoria,Australia").
        language_code: Language of the search (e.g. "en", "fr", "de"). Always use simple 2-letter codes.
        num_results: How deep to search for the domain (default 100, max 100).

    Returns:
        Dict with position, found flag, target_result details, serp_features,
        and top_results list.
    """
    err = _check_credentials()
    if err:
        return {"error": err, "keyword": keyword, "target_domain": target_domain}

    data = _serp_request([{
        "keyword": keyword,
        "location_name": location,
        "language_code": language_code,
        "depth": min(num_results, 100),
        "device": "desktop",
        "os": "windows",
    }])

    if "error" in data:
        return {"error": data["error"], "keyword": keyword, "target_domain": target_domain}

    items = _task_items(data)
    if items is None:
        return {"error": _task_error(data), "keyword": keyword, "target_domain": target_domain}

    organic = _organic_items(items)

    position = None
    target_result = None
    for item in organic:
        if _domain_match(target_domain, item):
            position = item["rank_absolute"]
            target_result = item
            break

    return {
        "keyword": keyword,
        "target_domain": target_domain,
        "position": position,
        "found": position is not None,
        "target_result": {
            "title": target_result.get("title"),
            "url": target_result.get("url"),
            "description": target_result.get("description"),
            "rank_absolute": target_result.get("rank_absolute"),
        } if target_result else None,
        "serp_features": _serp_features_summary(items),
        "top_results": [
            {
                "position": i["rank_absolute"],
                "url": i.get("url"),
                "title": i.get("title"),
                "domain": i.get("domain"),
            }
            for i in organic[:10]
        ],
        "metadata": {
            "location": location,
            "language_code": _normalise_language_code(language_code),
        },
    }


def batch_keyword_rankings(
    keywords: List[str],
    target_domain: str,
    location: str = "United States",
    language_code: str = "en",
) -> Dict:
    """Check rankings for multiple keywords in a single batched DataForSEO request.

    More efficient than calling get_keyword_ranking repeatedly — sends all
    keywords in one API call.

    Args:
        keywords: List of search queries to check.
        target_domain: The domain to find in each SERP (e.g. "example.com").
        location: Full location name (e.g. "United States", "Australia").
        language_code: Language code — always simple 2-letter code (e.g. "en", "fr", "de").

    Returns:
        Dict with per-keyword results list and summary stats (found count,
        average position, top ranking keyword).
    """
    err = _check_credentials()
    if err:
        return {"error": err}

    tasks = [
        {
            "keyword": kw,
            **_resolve_location(location, language_code),
            "depth": 100,
            "device": "desktop",
            "os": "windows",
        }
        for kw in keywords
    ]

    data = _serp_request(tasks)
    if "error" in data:
        return {"error": data["error"]}

    results = []
    found_count = 0
    total_position = 0

    for task_idx, keyword in enumerate(keywords):
        items = _task_items(data, task_idx)
        if items is None:
            results.append({
                "keyword": keyword,
                "target_domain": target_domain,
                "position": None,
                "found": False,
                "error": _task_error(data, task_idx),
            })
            continue

        organic = _organic_items(items)
        position = None
        target_result = None
        for item in organic:
            if _domain_match(target_domain, item):
                position = item["rank_absolute"]
                target_result = item
                break

        if position is not None:
            found_count += 1
            total_position += position

        results.append({
            "keyword": keyword,
            "target_domain": target_domain,
            "position": position,
            "found": position is not None,
            "target_result": {
                "title": target_result.get("title"),
                "url": target_result.get("url"),
            } if target_result else None,
        })

    avg_position = (total_position / found_count) if found_count > 0 else None
    ranked = [r for r in results if r.get("found")]

    return {
        "results": results,
        "summary": {
            "total_keywords": len(keywords),
            "keywords_found": found_count,
            "keywords_not_found": len(keywords) - found_count,
            "average_position": round(avg_position, 1) if avg_position else None,
        },
        "insights": {
            "ranking_coverage": f"{found_count}/{len(keywords)} keywords",
            "top_ranking_keyword": min(ranked, key=lambda x: x["position"])["keyword"] if ranked else None,
        },
    }


def analyze_serp_features(
    keyword: str,
    location: str = "United States",
    language_code: str = "en",
) -> Dict:
    """Analyze Google SERP features and competition level for a keyword.

    Returns featured snippets, People Also Ask questions, related searches,
    knowledge graph presence, top stories, and competitive domain diversity.

    Args:
        keyword: The search query to analyze.
        location: Full location name (e.g. "United States", "London,England,United Kingdom").
        language_code: Language code (e.g. "en", "en_AU", "fr").

    Returns:
        Dict with serp_features, top_competing_domains, competition_analysis,
        insights, and recommendations.
    """
    err = _check_credentials()
    if err:
        return {"error": err, "keyword": keyword}

    data = _serp_request([{
        "keyword": keyword,
        "location_name": location,
        "language_code": language_code,
        "depth": 100,
        "device": "desktop",
        "os": "windows",
        "people_also_ask_click_depth": 1,
    }])

    if "error" in data:
        return {"error": data["error"], "keyword": keyword}

    items = _task_items(data)
    if items is None:
        return {"error": _task_error(data), "keyword": keyword}

    organic = _organic_items(items)

    # --- Extract SERP features ---
    features: Dict[str, Any] = {
        "knowledge_graph": None,
        "featured_snippet": None,
        "people_also_ask": [],
        "related_searches": [],
        "top_stories": [],
    }

    kg = next((i for i in items if i.get("type") == "knowledge_graph"), None)
    if kg:
        features["knowledge_graph"] = {
            "title": kg.get("title"),
            "description": kg.get("description"),
        }

    fs = next((i for i in items if i.get("type") == "featured_snippet"), None)
    if fs:
        features["featured_snippet"] = {
            "snippet": fs.get("description"),
            "title": fs.get("title"),
            "url": fs.get("url"),
        }

    paa = next((i for i in items if i.get("type") == "people_also_ask"), None)
    if paa:
        features["people_also_ask"] = [
            {"question": q.get("title"), "snippet": q.get("description")}
            if isinstance(q, dict) else {"question": str(q), "snippet": None}
            for q in paa.get("items", [])[:5]
        ]

    related = next((i for i in items if i.get("type") == "related_searches"), None)
    if related:
        features["related_searches"] = [
            s.get("title") if isinstance(s, dict) else str(s)
            for s in related.get("items", [])[:10]
            if s
        ]

    stories = next((i for i in items if i.get("type") == "top_stories"), None)
    if stories:
        features["top_stories"] = [
            {"title": s.get("title"), "url": s.get("url"), "source": s.get("source")}
            for s in stories.get("items", [])[:5]
        ]

    # --- Competitive domain analysis ---
    top_domains: Dict[str, int] = {}
    for item in organic[:20]:
        domain = item.get("domain", "")
        if domain:
            top_domains[domain] = top_domains.get(domain, 0) + 1

    competition_level = "low"
    if len(top_domains) >= 15:
        competition_level = "high"
    elif len(top_domains) >= 10:
        competition_level = "medium"

    return {
        "keyword": keyword,
        "serp_features": features,
        "organic_results_count": len(organic),
        "top_competing_domains": dict(
            sorted(top_domains.items(), key=lambda x: x[1], reverse=True)[:10]
        ),
        "competition_analysis": {
            "level": competition_level,
            "domain_diversity": len(top_domains),
            "featured_snippet_present": features["featured_snippet"] is not None,
        },
        "insights": {
            "has_featured_snippet": features["featured_snippet"] is not None,
            "has_knowledge_graph": features["knowledge_graph"] is not None,
            "paa_count": len(features["people_also_ask"]),
            "related_searches_count": len(features["related_searches"]),
        },
        "recommendations": _generate_serp_recommendations(features, competition_level),
    }


def compare_rankings(
    keywords: List[str],
    domains: List[str],
    location: str = "United States",
    language_code: str = "en",
) -> Dict:
    """Compare Google rankings for multiple domains across multiple keywords.

    Sends all keywords in a single batched DataForSEO request for efficiency,
    then shows each domain's position per keyword.

    Args:
        keywords: List of search queries to check.
        domains: List of domains to compare (e.g. ["ahrefs.com", "semrush.com"]).
        location: Full location name (e.g. "United States", "Australia").
        language_code: Language code — always simple 2-letter code (e.g. "en", "fr", "de").

    Returns:
        Dict with per-keyword rankings breakdown and per-domain summary stats
        (keywords found in top 100, average position).
    """
    err = _check_credentials()
    if err:
        return {"error": err}

    tasks = [
        {
            "keyword": kw,
            **_resolve_location(location, language_code),
            "depth": 100,
            "device": "desktop",
            "os": "windows",
        }
        for kw in keywords
    ]

    data = _serp_request(tasks)
    if "error" in data:
        return {"error": data["error"]}

    comparison: Dict[str, Any] = {
        "keywords": {},
        "domain_summary": {d: {"found": 0, "total_position": 0} for d in domains},
    }

    for task_idx, keyword in enumerate(keywords):
        keyword_data: Dict[str, Any] = {"keyword": keyword, "rankings": {}}

        items = _task_items(data, task_idx)
        if items is None:
            keyword_data["error"] = _task_error(data, task_idx)
            for domain in domains:
                keyword_data["rankings"][domain] = None
            comparison["keywords"][keyword] = keyword_data
            continue

        organic = _organic_items(items)

        for domain in domains:
            position = None
            for item in organic:
                if _domain_match(domain, item):
                    position = item["rank_absolute"]
                    comparison["domain_summary"][domain]["found"] += 1
                    comparison["domain_summary"][domain]["total_position"] += position
                    break
            keyword_data["rankings"][domain] = position

        comparison["keywords"][keyword] = keyword_data

    # Calculate average positions per domain
    for domain in domains:
        found = comparison["domain_summary"][domain]["found"]
        if found > 0:
            avg = comparison["domain_summary"][domain]["total_position"] / found
            comparison["domain_summary"][domain]["average_position"] = round(avg, 1)
        else:
            comparison["domain_summary"][domain]["average_position"] = None

    return comparison
