"""Generic web content extraction tools for SEO agents.

These tools fetch one or more URLs and extract SEO-relevant
metadata such as title, meta description, canonical URL, robots
directives, FAQ content, and basic on-page text snippets.

They are designed to be lightweight (requests + BeautifulSoup),
without running JavaScript. Use them for meta/title checks,
on-page alignment reviews, FAQ extraction, and quick content audits.
"""
import json
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup


def extract_page_metadata(url: str) -> Dict[str, Any]:
    """Fetch a single URL and extract basic SEO metadata and content.

    Args:
        url: Absolute page URL (e.g., 'https://example.com/page').

    Returns:
        Dict containing status, http_status, title, meta_description,
        meta_robots, canonical_url, h1 tags, and a short text excerpt.
    """
    try:
        resp = requests.get(url, timeout=20)
        http_status = resp.status_code
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # <title>
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None

        # <meta name="description">
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_desc_tag.get("content", "").strip() if meta_desc_tag else None

        # <meta name="robots">
        meta_robots_tag = soup.find("meta", attrs={"name": "robots"})
        meta_robots = meta_robots_tag.get("content", "").strip() if meta_robots_tag else None

        # <link rel="canonical">
        canonical_tag = soup.find("link", rel=lambda v: v and "canonical" in v.lower())
        canonical_url = canonical_tag.get("href", "").strip() if canonical_tag else None

        # All H1 tags
        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]

        # Basic visible text excerpt (first ~1000 chars)
        # This is intentionally simple and does not attempt full boilerplate removal.
        full_text = soup.get_text(" ", strip=True)
        text_excerpt = full_text[:1000] if full_text else ""

        return {
            "status": "success",
            "url": url,
            "http_status": http_status,
            "title": title,
            "meta_description": meta_description,
            "meta_robots": meta_robots,
            "canonical_url": canonical_url,
            "h1": h1_tags,
            "text_excerpt": text_excerpt,
            "note": (
                "Content extracted from static HTML only. "
                "JavaScript-rendered content may not appear."
            ),
        }

    except requests.RequestException as exc:
        return {
            "status": "error",
            "url": url,
            "http_status": getattr(exc.response, "status_code", None) if hasattr(exc, "response") else None,
            "error": f"HTTP error: {str(exc)}",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "url": url,
            "http_status": None,
            "error": str(exc),
        }


def extract_batch_page_metadata(urls: List[str]) -> Dict[str, Any]:
    """Fetch and extract metadata for a batch of URLs.

    Args:
        urls: List of absolute URLs.

    Returns:
        Dict with per-URL results and a summary (success/error counts).
    """
    results: List[Dict[str, Any]] = []
    success_count = 0
    error_count = 0

    for url in urls:
        result = extract_page_metadata(url)
        results.append(result)
        if result.get("status") == "success":
            success_count += 1
        else:
            error_count += 1

    return {
        "status": "completed",
        "total_urls": len(urls),
        "success_count": success_count,
        "error_count": error_count,
        "results": results,
    }


def _extract_faq_from_json_ld(script_text: str) -> List[Dict[str, Any]]:
    """Parse JSON-LD blocks and extract FAQPage questions/answers."""
    faqs: List[Dict[str, Any]] = []

    try:
        data = json.loads(script_text)
    except json.JSONDecodeError:
        return faqs

    def normalize_to_list(obj):
        if isinstance(obj, list):
            return obj
        return [obj]

    def extract_from_obj(obj):
        nonlocal faqs
        if not isinstance(obj, dict):
            return

        obj_type = obj.get("@type")
        if isinstance(obj_type, list):
            obj_type = obj_type[0] if obj_type else None

        if obj_type == "FAQPage":
            entities = normalize_to_list(obj.get("mainEntity", []))
            for entity in entities:
                if not isinstance(entity, dict):
                    continue
                if entity.get("@type") != "Question":
                    continue
                question = entity.get("name") or entity.get("headline")
                accepted_answers = normalize_to_list(entity.get("acceptedAnswer", []))
                answers = []
                for ans in accepted_answers:
                    if not isinstance(ans, dict):
                        continue
                    if ans.get("@type") not in ("Answer", "Question"):
                        continue
                    text = ans.get("text") or ans.get("name") or ""
                    if text:
                        answers.append(text.strip())
                if question and answers:
                    faqs.append(
                        {
                            "question": question.strip(),
                            "answers": answers,
                            "source": "json_ld",
                        }
                    )

    if isinstance(data, list):
        for entry in data:
            extract_from_obj(entry)
    else:
        extract_from_obj(data)

    return faqs


def extract_page_faqs(url: str) -> Dict[str, Any]:
    """Fetch a URL and extract FAQ content where possible.

    This looks for:
    - JSON-LD with @type "FAQPage" and Question/Answer entities.
    - Basic HTML patterns (elements with itemtype Question/Answer).

    Args:
        url: Absolute page URL.

    Returns:
        Dict with status, url, http_status, faqs (list of {question, answers, source}),
        and a note about limitations.
    """
    try:
        resp = requests.get(url, timeout=20)
        http_status = resp.status_code
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        faqs: List[Dict[str, Any]] = []

        # 1) JSON-LD FAQPage
        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string:
                continue
            faqs.extend(_extract_faq_from_json_ld(script.string))

        # 2) Microdata-style Question/Answer markup
        for question_el in soup.find_all(attrs={"itemtype": "https://schema.org/Question"}):
            question_text = None
            name_el = question_el.find(attrs={"itemprop": "name"})
            if name_el and name_el.get_text(strip=True):
                question_text = name_el.get_text(strip=True)

            answers: List[str] = []
            for answer_el in question_el.find_all(attrs={"itemtype": "https://schema.org/Answer"}):
                text_el = answer_el.find(attrs={"itemprop": "text"})
                if text_el and text_el.get_text(strip=True):
                    answers.append(text_el.get_text(strip=True))

            if question_text and answers:
                faqs.append(
                    {
                        "question": question_text,
                        "answers": answers,
                        "source": "microdata",
                    }
                )

        return {
            "status": "success",
            "url": url,
            "http_status": http_status,
            "faq_count": len(faqs),
            "faqs": faqs,
            "note": (
                "FAQ extraction relies on JSON-LD FAQPage and basic schema.org patterns. "
                "Custom accordion HTML without structured data may not be detected."
            ),
        }

    except requests.RequestException as exc:
        return {
            "status": "error",
            "url": url,
            "http_status": getattr(exc.response, "status_code", None) if hasattr(exc, "response") else None,
            "faq_count": 0,
            "faqs": [],
            "error": f"HTTP error: {str(exc)}",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "url": url,
            "http_status": None,
            "faq_count": 0,
            "faqs": [],
            "error": str(exc),
        }


def extract_batch_page_faqs(urls: List[str]) -> Dict[str, Any]:
    """Fetch and extract FAQs for a batch of URLs.

    Args:
        urls: List of absolute URLs.

    Returns:
        Dict with per-URL results and a summary (success/error counts).
    """
    results: List[Dict[str, Any]] = []
    success_count = 0
    error_count = 0
    total_faqs = 0

    for url in urls:
        result = extract_page_faqs(url)
        results.append(result)
        if result.get("status") == "success":
            success_count += 1
            total_faqs += int(result.get("faq_count", 0))
        else:
            error_count += 1

    return {
        "status": "completed",
        "total_urls": len(urls),
        "success_count": success_count,
        "error_count": error_count,
        "total_faqs": total_faqs,
        "results": results,
    }
