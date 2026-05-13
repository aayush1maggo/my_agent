"""Competitor Content Analysis Tools for SEO content brief generation.

Fetches top SERP competitors for a keyword, scrapes their pages, extracts
heading-based topic signals, and produces a structured content brief.

All functions return {"status": "success"|"error", ...} dicts and never raise.
"""
import re
import json
import statistics
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from collections import defaultdict
from datetime import datetime

import base64

import requests

from ..config import DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD, DATAFORSEO_SERP_URL
from .browser_tools import fetch_page_content
from .serper_tools import _resolve_location


# ---------------------------------------------------------------------------
# Optional spaCy — graceful fallback if not installed
# ---------------------------------------------------------------------------
_SPACY_AVAILABLE = False
_nlp = None
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
    _SPACY_AVAILABLE = True
except (ImportError, OSError):
    pass


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _normalise_heading(text: str) -> str:
    """Lowercase, strip punctuation except hyphens, collapse whitespace."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s\-]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def _extract_entities(text: str) -> List[Dict[str, str]]:
    """spaCy NER on text — returns [] if spaCy unavailable."""
    if not _SPACY_AVAILABLE or not _nlp:
        return []
    doc = _nlp(text[:5000])
    TYPES = {"ORG", "PRODUCT", "PERSON", "GPE", "WORK_OF_ART", "EVENT"}
    seen, entities = set(), []
    for ent in doc.ents:
        if ent.label_ in TYPES:
            key = ent.text.strip().lower()
            if key not in seen and len(ent.text.strip()) > 2:
                seen.add(key)
                entities.append({"entity": ent.text.strip(), "type": ent.label_})
    return entities


def _aggregate_topics(
    competitor_pages: List[Dict[str, Any]],
    num_successful: int,
) -> Dict[str, List[Dict[str, Any]]]:
    """Count heading occurrences across pages (once per page) and return sorted lists."""
    h2_counts: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "sources": []})
    h3_counts: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "sources": []})

    for page in competitor_pages:
        if page.get("scrape_status") != "success":
            continue
        domain = page["domain"]

        # Deduplicate within this page then count
        seen_h2 = set()
        for h in page.get("h2_topics", []):
            if h not in seen_h2:
                seen_h2.add(h)
                h2_counts[h]["count"] += 1
                h2_counts[h]["sources"].append(domain)

        seen_h3 = set()
        for h in page.get("h3_topics", []):
            if h not in seen_h3:
                seen_h3.add(h)
                h3_counts[h]["count"] += 1
                h3_counts[h]["sources"].append(domain)

    def _build_list(counts: Dict) -> List[Dict[str, Any]]:
        items = []
        for topic, data in counts.items():
            freq = data["count"] / num_successful if num_successful > 0 else 0
            items.append({
                "topic": topic,
                "count": data["count"],
                "frequency": round(freq, 2),
                "sources": data["sources"],
            })
        return sorted(items, key=lambda x: x["count"], reverse=True)

    return {
        "h2": _build_list(h2_counts),
        "h3": _build_list(h3_counts),
    }


def _aggregate_entities(
    competitor_pages: List[Dict[str, Any]],
    num_successful: int,
) -> List[Dict[str, Any]]:
    """Aggregate entity counts across all successful pages."""
    entity_counts: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"type": "", "count": 0}
    )
    for page in competitor_pages:
        if page.get("scrape_status") != "success":
            continue
        for ent in page.get("entities", []):
            key = ent["entity"].lower()
            entity_counts[key]["type"] = ent["type"]
            entity_counts[key]["count"] += 1

    result = []
    for entity, data in entity_counts.items():
        freq = data["count"] / num_successful if num_successful > 0 else 0
        result.append({
            "entity": entity,
            "type": data["type"],
            "count": data["count"],
            "frequency": round(freq, 2),
        })
    return sorted(result, key=lambda x: x["count"], reverse=True)


def _aggregate_schema_types(
    competitor_pages: List[Dict[str, Any]],
    num_successful: int,
) -> List[Dict[str, Any]]:
    """Count schema type frequency across pages."""
    schema_counts: Dict[str, int] = defaultdict(int)
    for page in competitor_pages:
        if page.get("scrape_status") != "success":
            continue
        seen = set()
        for s in page.get("schema_types", []):
            if s not in seen:
                seen.add(s)
                schema_counts[s] += 1

    result = []
    for schema_type, count in schema_counts.items():
        freq = count / num_successful if num_successful > 0 else 0
        result.append({
            "schema_type": schema_type,
            "count": count,
            "frequency": round(freq, 2),
        })
    return sorted(result, key=lambda x: x["count"], reverse=True)


def _build_suggested_outline(competitor_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build suggested outline by grouping H3s under H2s using heading sequence across pages.

    For each H2 that appears in a page, the H3s that follow it (before the next H2)
    are candidate subtopics. We pick the most common H3 groupings per H2.
    """
    # Map: h2 -> list of h3s that appear under it across all pages
    h2_to_h3s: Dict[str, List[str]] = defaultdict(list)

    for page in competitor_pages:
        if page.get("scrape_status") != "success":
            continue
        headings = page.get("_raw_heading_sequence", [])
        current_h2 = None
        for level, text in headings:
            if level == "h2":
                current_h2 = text
            elif level == "h3" and current_h2:
                h2_to_h3s[current_h2].append(text)

    # Collect the most common H3s for each H2 (top 5)
    outline = []
    # Get H2s ordered by frequency (use first appearance order as tiebreaker)
    seen_h2s = []
    for page in competitor_pages:
        if page.get("scrape_status") != "success":
            continue
        for level, text in page.get("_raw_heading_sequence", []):
            if level == "h2" and text not in seen_h2s:
                seen_h2s.append(text)

    for h2 in seen_h2s:
        subtopic_counts: Dict[str, int] = defaultdict(int)
        for h3 in h2_to_h3s.get(h2, []):
            subtopic_counts[h3] += 1
        top_subtopics = sorted(subtopic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        outline.append({
            "heading": h2,
            "level": "h2",
            "subtopics": [{"heading": h3, "level": "h3", "count": cnt} for h3, cnt in top_subtopics],
        })

    return outline


# ---------------------------------------------------------------------------
# Public Tool Functions
# ---------------------------------------------------------------------------

def analyze_competitor_topics(
    keyword: str,
    num_competitors: int = 10,
    location: str = "United States",
    language_code: str = "en",
    min_word_count: int = 300,
) -> Dict[str, Any]:
    """Fetch top SERP competitors for a keyword and analyze their content topics.

    Uses the DataForSEO SERP API (Google organic, live/advanced) to get real
    competitor URLs, then scrapes headings (H2/H3) from each page to identify
    what topics and subtopics they cover. Returns heading frequency data, word
    count stats, entity analysis (if spaCy is available), and schema type usage.

    Args:
        keyword: The search keyword or topic to analyze (e.g. "best CRM software").
        num_competitors: Number of top organic results to analyze (default 10, max 20).
        location: Location name for geo-targeting (e.g. "United States", "London,England,United Kingdom").
        language_code: Language code for the search — simple 2-letter code only (e.g. "en", "fr", "de"). For Australia/UK/NZ use "en".
        min_word_count: Minimum word count to consider a page non-thin (default 300).

    Returns:
        Dict with status, keyword, competitor_pages list, topic_frequency (h2/h3),
        entity_frequency, word_count_stats, schema_type_frequency, and serp_features.
    """
    if not DATAFORSEO_LOGIN or not DATAFORSEO_PASSWORD:
        return {
            "status": "error",
            "keyword": keyword,
            "error": "DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD are not configured. Add them to your .env file.",
        }

    num_competitors = min(num_competitors, 20)

    # --- DataForSEO SERP fetch ---
    credentials = base64.b64encode(
        f"{DATAFORSEO_LOGIN}:{DATAFORSEO_PASSWORD}".encode()
    ).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }
    payload = [
        {
            "keyword": keyword,
            **_resolve_location(location, language_code),
            "depth": num_competitors,
            "device": "desktop",
            "os": "windows",
            "people_also_ask_click_depth": 1,
        }
    ]

    try:
        serp_resp = requests.post(
            DATAFORSEO_SERP_URL, headers=headers, json=payload, timeout=30
        )
        serp_resp.raise_for_status()
        serp_data = serp_resp.json()
    except requests.RequestException as exc:
        return {
            "status": "error",
            "keyword": keyword,
            "error": f"DataForSEO API request failed: {exc}",
        }

    # Validate DataForSEO response structure
    try:
        task = serp_data["tasks"][0]
        if task.get("status_code") != 20000:
            return {
                "status": "error",
                "keyword": keyword,
                "error": f"DataForSEO task error {task.get('status_code')}: {task.get('status_message', 'Unknown error')}",
            }
        all_items: List[Dict] = task["result"][0]["items"]
    except (KeyError, IndexError, TypeError) as exc:
        return {
            "status": "error",
            "keyword": keyword,
            "error": f"Unexpected DataForSEO response structure: {exc}",
        }

    # Separate organic results and SERP features from the unified items array
    organic: List[Dict] = [i for i in all_items if i.get("type") == "organic"]
    if not organic:
        return {
            "status": "error",
            "keyword": keyword,
            "error": "No organic results returned by DataForSEO. Check credentials or try a different keyword.",
        }

    # People Also Ask — one container item with nested items[]
    # items can be dicts {"title": "..."} or plain strings depending on DataForSEO version
    paa_container = next((i for i in all_items if i.get("type") == "people_also_ask"), None)
    paa = [
        q.get("title", "") if isinstance(q, dict) else str(q)
        for q in (paa_container or {}).get("items", [])
    ]

    # Related Searches — one container item with nested items[]
    related_container = next((i for i in all_items if i.get("type") == "related_searches"), None)
    related = [
        s.get("title", "") if isinstance(s, dict) else str(s)
        for s in (related_container or {}).get("items", [])
    ]

    # Featured Snippet — present if any item has type "featured_snippet"
    featured_snippet = next((i for i in all_items if i.get("type") == "featured_snippet"), None)

    serp_features = {
        "people_also_ask": [q for q in paa if q],
        "related_searches": [s for s in related if s],
        "featured_snippet_present": featured_snippet is not None,
        "featured_snippet_url": featured_snippet.get("url") if featured_snippet else None,
    }

    # --- Scrape each competitor ---
    competitor_pages: List[Dict[str, Any]] = []
    successful = 0
    failed = 0

    for result in organic[:num_competitors]:
        url = result.get("url", "")
        idx = result.get("rank_absolute", len(competitor_pages) + 1)
        if not url:
            continue

        domain = result.get("domain") or urlparse(url).netloc

        page_data = fetch_page_content(url, include_links=False, max_text_chars=5000)

        if page_data.get("status") != "success":
            http_status = page_data.get("http_status")
            if http_status and 400 <= http_status < 500:
                scrape_status = "blocked"
            else:
                scrape_status = "error"
            failed += 1
            competitor_pages.append({
                "position": idx,
                "url": url,
                "domain": domain,
                "title": result.get("title", ""),
                "word_count": 0,
                "schema_types": [],
                "h2_topics": [],
                "h3_topics": [],
                "entities": [],
                "scrape_status": scrape_status,
                "error": page_data.get("error", ""),
                "_raw_heading_sequence": [],
            })
            continue

        word_count = page_data.get("word_count", 0)
        if word_count < min_word_count:
            scrape_status = "thin"
            failed += 1
        else:
            scrape_status = "success"
            successful += 1

        headings = page_data.get("headings", {})
        h2_raw = headings.get("h2", [])
        h3_raw = headings.get("h3", [])
        h2_topics = [_normalise_heading(h) for h in h2_raw if h.strip()]
        h3_topics = [_normalise_heading(h) for h in h3_raw if h.strip()]

        # Build raw heading sequence for outline construction
        # We interleave h2/h3 in document order by using BeautifulSoup order
        # (fetch_page_content preserves per-level order; we reconstruct approximate sequence)
        raw_sequence = []
        # Use h2 as the primary structure; h3s are assumed to follow their nearest h2
        for level in ["h1", "h2", "h3", "h4"]:
            for h in headings.get(level, []):
                raw_sequence.append((level, _normalise_heading(h)))
        # Sort by level only — we can't recover true DOM order from fetch_page_content
        # Use per-page list order which is already document order within each level
        # Rebuild: interleave h2/h3 in their raw document order by alternating
        raw_sequence_ordered = []
        h2_iter = iter([(h, "h2") for h in h2_raw])
        h3_iter = iter([(h, "h3") for h in h3_raw])
        # Simple ordered merge: h2s then attach following h3s heuristically
        _h2_list = [("h2", _normalise_heading(h)) for h in h2_raw if h.strip()]
        _h3_list = [("h3", _normalise_heading(h)) for h in h3_raw if h.strip()]
        # Distribute h3s evenly under h2s (approximation when DOM order is unavailable)
        if _h2_list:
            h3_per_h2 = max(1, len(_h3_list) // len(_h2_list))
            h3_idx = 0
            for h2_entry in _h2_list:
                raw_sequence_ordered.append(h2_entry)
                for _ in range(h3_per_h2):
                    if h3_idx < len(_h3_list):
                        raw_sequence_ordered.append(_h3_list[h3_idx])
                        h3_idx += 1
            # Remaining h3s under last h2
            while h3_idx < len(_h3_list):
                raw_sequence_ordered.append(_h3_list[h3_idx])
                h3_idx += 1
        else:
            raw_sequence_ordered = _h3_list

        # Entity extraction
        text_content = page_data.get("text_content", "")
        entities = _extract_entities(text_content) if scrape_status == "success" else []

        competitor_pages.append({
            "position": idx,
            "url": url,
            "domain": domain,
            "title": result.get("title", page_data.get("title", "")),
            "word_count": word_count,
            "schema_types": page_data.get("schema_types", []),
            "h2_topics": h2_topics,
            "h3_topics": h3_topics,
            "entities": entities,
            "scrape_status": scrape_status,
            "_raw_heading_sequence": raw_sequence_ordered,
        })

    # --- Aggregation ---
    topic_frequency = _aggregate_topics(competitor_pages, successful)
    entity_frequency = _aggregate_entities(competitor_pages, successful)
    schema_type_frequency = _aggregate_schema_types(competitor_pages, successful)

    # Word count stats
    word_counts = [p["word_count"] for p in competitor_pages if p["scrape_status"] == "success"]
    word_count_stats: Dict[str, Any] = {
        "min": min(word_counts) if word_counts else 0,
        "max": max(word_counts) if word_counts else 0,
        "median": int(statistics.median(word_counts)) if word_counts else 0,
        "average": int(sum(word_counts) / len(word_counts)) if word_counts else 0,
    }

    # Strip internal helper field from output
    clean_pages = []
    for p in competitor_pages:
        clean = {k: v for k, v in p.items() if k != "_raw_heading_sequence"}
        clean_pages.append(clean)

    result: Dict[str, Any] = {
        "status": "success",
        "keyword": keyword,
        "competitors_attempted": len(competitor_pages),
        "competitors_successful": successful,
        "competitors_failed": failed,
        "serp_features": serp_features,
        "competitor_pages": clean_pages,
        "topic_frequency": topic_frequency,
        "entity_frequency": entity_frequency[:30],
        "word_count_stats": word_count_stats,
        "schema_type_frequency": schema_type_frequency,
        "spacy_available": _SPACY_AVAILABLE,
    }

    if successful == 0:
        result["warning"] = (
            "All competitor pages failed to scrape. Topic analysis is empty. "
            "Sites may be blocking automated requests."
        )

    return result


def generate_content_brief(
    keyword: str,
    competitor_analysis: Optional[Dict[str, Any]] = None,
    num_competitors: int = 10,
    location: str = "United States",
    language_code: str = "en",
) -> Dict[str, Any]:
    """Generate a complete SEO content brief for a keyword based on competitor analysis.

    Uses DataForSEO SERP API to identify top-ranking competitors, scrapes their pages,
    and produces a structured brief: required/recommended/optional topics, a suggested
    H2 outline, target word count, key entities to mention, and schema recommendations.

    Use this when a user asks to:
    - "Create a content brief for [keyword]"
    - "What should I cover to rank for [keyword]?"
    - "Analyse competitors for [topic]"
    - "What topics do my competitors cover for [keyword]?"

    Args:
        keyword: The target keyword or topic (e.g. "best project management software").
        competitor_analysis: Pre-computed result from analyze_competitor_topics().
                             If None, the analysis is run automatically.
        num_competitors: Number of competitors to analyze if running fresh (default 10).
        location: Location name for geo-targeting (e.g. "United States", "Australia").
        language_code: Language code for the search — simple 2-letter code only (e.g. "en", "fr", "de"). For Australia/UK/NZ use "en".

    Returns:
        Dict with status, keyword, content_brief (required/recommended/optional topics,
        suggested outline, target word count, key entities, schema recommendations,
        serp insights), and per_competitor_breakdown.
    """
    # Run analysis if not provided
    if competitor_analysis is None:
        competitor_analysis = analyze_competitor_topics(
            keyword=keyword,
            num_competitors=num_competitors,
            location=location,
            language_code=language_code,
        )

    if competitor_analysis.get("status") == "error":
        return {
            "status": "error",
            "keyword": keyword,
            "error": competitor_analysis.get("error", "Competitor analysis failed."),
        }

    num_successful = competitor_analysis.get("competitors_successful", 0)
    topic_frequency = competitor_analysis.get("topic_frequency", {"h2": [], "h3": []})
    entity_frequency = competitor_analysis.get("entity_frequency", [])
    schema_type_frequency = competitor_analysis.get("schema_type_frequency", [])
    serp_features = competitor_analysis.get("serp_features", {})
    word_count_stats = competitor_analysis.get("word_count_stats", {})
    competitor_pages = competitor_analysis.get("competitor_pages", [])

    # --- Topic tiering ---
    REQUIRED_THRESHOLD = 0.60
    RECOMMENDED_THRESHOLD = 0.40
    OPTIONAL_THRESHOLD = 0.20

    def _tier_topics(topics: List[Dict]) -> Dict[str, List]:
        required, recommended, optional_, unique = [], [], [], []
        for t in topics:
            freq = t["frequency"]
            entry = {
                "topic": t["topic"],
                "heading_level": "h2" if t in topic_frequency.get("h2", []) else "h3",
                "competitor_coverage": f"{int(freq * 100)}%",
                "appears_in": t["count"],
            }
            if freq >= REQUIRED_THRESHOLD:
                required.append(entry)
            elif freq >= RECOMMENDED_THRESHOLD:
                recommended.append(entry)
            elif freq >= OPTIONAL_THRESHOLD:
                optional_.append(entry)
            elif t["count"] == 1:
                unique.append({
                    "topic": t["topic"],
                    "heading_level": entry["heading_level"],
                    "source_domain": t["sources"][0] if t["sources"] else "",
                    "rationale": "Unique angle — only 1 competitor covers this; could differentiate your content",
                })
        return {
            "required": required,
            "recommended": recommended,
            "optional": optional_,
            "unique": unique,
        }

    h2_tiers = _tier_topics(topic_frequency.get("h2", []))
    h3_tiers = _tier_topics(topic_frequency.get("h3", []))

    required_topics = h2_tiers["required"] + h3_tiers["required"]
    recommended_topics = h2_tiers["recommended"] + h3_tiers["recommended"]
    optional_topics = h2_tiers["optional"] + h3_tiers["optional"]
    unique_angles = h2_tiers["unique"][:5] + h3_tiers["unique"][:5]

    # Fix heading_level labels (topic tiering helper above doesn't know the level)
    def _fix_level(topics: List[Dict], level: str) -> List[Dict]:
        for t in topics:
            t["heading_level"] = level
        return topics

    required_topics = (
        _fix_level(h2_tiers["required"], "h2") +
        _fix_level(h3_tiers["required"], "h3")
    )
    recommended_topics = (
        _fix_level(h2_tiers["recommended"], "h2") +
        _fix_level(h3_tiers["recommended"], "h3")
    )
    optional_topics = (
        _fix_level(h2_tiers["optional"], "h2") +
        _fix_level(h3_tiers["optional"], "h3")
    )

    # --- Target word count ---
    median_wc = word_count_stats.get("median", 0)
    avg_wc = word_count_stats.get("average", 0)
    if median_wc > 0:
        recommended_wc = int((median_wc + avg_wc) / 2 / 100) * 100  # round to nearest 100
        wc_min = max(500, int(recommended_wc * 0.8))
        wc_max = int(recommended_wc * 1.3)
    else:
        recommended_wc = 1500
        wc_min = 1000
        wc_max = 2500

    # --- Key entities ---
    key_entities = []
    for ent in entity_frequency[:15]:
        key_entities.append({
            "entity": ent["entity"],
            "entity_type": ent["type"],
            "competitor_coverage": f"{int(ent['frequency'] * 100)}%",
        })

    # --- Schema recommendations ---
    schema_recommendations = []
    for schema in schema_type_frequency[:8]:
        priority = "high" if schema["frequency"] >= 0.5 else ("medium" if schema["frequency"] >= 0.3 else "low")
        schema_recommendations.append({
            "schema_type": schema["schema_type"],
            "competitor_coverage": f"{int(schema['frequency'] * 100)}%",
            "priority": priority,
        })

    # --- SERP insights ---
    snippet_note = ""
    if serp_features.get("featured_snippet_present"):
        snippet_note = (
            "A featured snippet exists for this keyword. "
            "Structure your answer concisely near the top of the page (40–60 words) "
            "and use clear H2/H3 headings to target the snippet."
        )

    serp_insights = {
        "people_also_ask": serp_features.get("people_also_ask", []),
        "related_searches": serp_features.get("related_searches", []),
        "featured_snippet_present": serp_features.get("featured_snippet_present", False),
        "featured_snippet_note": snippet_note,
    }

    # --- Suggested outline ---
    suggested_outline = _build_suggested_outline(competitor_pages)

    # --- Per-competitor breakdown ---
    per_competitor = []
    for p in competitor_pages:
        per_competitor.append({
            "position": p["position"],
            "url": p["url"],
            "domain": p["domain"],
            "word_count": p["word_count"],
            "schema_types": p["schema_types"],
            "h2_topics": p["h2_topics"],
            "h3_topics": p["h3_topics"],
        })

    return {
        "status": "success",
        "keyword": keyword,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_quality": {
            "competitors_analyzed": num_successful,
            "competitors_failed": competitor_analysis.get("competitors_failed", 0),
            "spacy_entities_available": competitor_analysis.get("spacy_available", False),
        },
        "content_brief": {
            "target_word_count": {
                "recommended": recommended_wc,
                "range": [wc_min, wc_max],
            },
            "required_topics": required_topics,
            "recommended_topics": recommended_topics,
            "optional_topics": optional_topics,
            "unique_angle_opportunities": unique_angles,
            "key_entities": key_entities,
            "schema_recommendations": schema_recommendations,
            "serp_insights": serp_insights,
            "suggested_outline": suggested_outline,
        },
        "per_competitor_breakdown": per_competitor,
    }
