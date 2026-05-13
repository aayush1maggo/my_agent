"""Web browsing and crawling tools for SEO agents.

Provides single-page deep extraction, multi-page BFS crawling, and
concurrent HEAD-check utilities. Uses only requests, beautifulsoup4,
and aiohttp — no additional dependencies beyond what is already installed.

All functions return {"status": "success"|"error", ...} dicts and
never raise exceptions. List fields are capped at _MAX_LINKS_IN_RESPONSE
items with a companion _total count field.
"""
import asyncio
import json
import re
import time
import urllib.robotparser
from collections import deque
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse, urldefrag

import aiohttp
import requests
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------
_CRAWL_DELAY_SECONDS = 0.5
_MAX_PAGES_HARD_LIMIT = 200
_MAX_LINKS_IN_RESPONSE = 100
_REQUEST_TIMEOUT = 20
_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get(url: str) -> requests.Response:
    """Shared GET with timeout and default headers."""
    return requests.get(url, timeout=_REQUEST_TIMEOUT, headers=_DEFAULT_HEADERS)


def _head(url: str) -> requests.Response:
    """Shared HEAD with timeout and default headers."""
    return requests.head(
        url, timeout=_REQUEST_TIMEOUT, headers=_DEFAULT_HEADERS, allow_redirects=True
    )


def _same_domain(url: str, base: str) -> bool:
    """Return True if url is on the same registered domain as base."""
    return urlparse(url).netloc == urlparse(base).netloc


def _normalize(url: str) -> str:
    """Strip fragment component from a URL."""
    defragged, _ = urldefrag(url)
    return defragged


def _robots_parser(start_url: str) -> Optional[urllib.robotparser.RobotFileParser]:
    """Fetch and parse robots.txt for start_url's domain. Return None on failure."""
    parsed = urlparse(start_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp
    except Exception:
        return None


def _cap_list(items: List[Any], label: str) -> Dict[str, Any]:
    """Return dict with capped list and total count."""
    return {
        label: items[:_MAX_LINKS_IN_RESPONSE],
        f"{label}_total": len(items),
    }


# ---------------------------------------------------------------------------
# Single-page tools
# ---------------------------------------------------------------------------

def fetch_page_content(
    url: str,
    include_links: bool = True,
    max_text_chars: int = 3000,
) -> Dict[str, Any]:
    """Fetch a page and return comprehensive SEO-relevant content.

    Extracts all headings (H1-H6), Open Graph tags, schema.org types,
    word count, link counts, and full visible text up to max_text_chars.

    Args:
        url: Absolute page URL.
        include_links: Whether to include internal/external link counts.
        max_text_chars: Maximum characters of visible text to return.

    Returns:
        Dict with status, title, meta_description, canonical_url, headings
        (H1-H6 lists), open_graph, schema_types, word_count, link_counts,
        text_content, and http_status.
    """
    try:
        resp = _get(url)
        http_status = resp.status_code
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_desc.get("content", "").strip() if meta_desc else None

        # Meta robots
        meta_robots_tag = soup.find("meta", attrs={"name": "robots"})
        meta_robots = meta_robots_tag.get("content", "").strip() if meta_robots_tag else None

        # Canonical
        canonical_tag = soup.find("link", rel=lambda v: v and "canonical" in v)
        canonical_url = canonical_tag.get("href", "").strip() if canonical_tag else None

        # Headings H1-H6
        headings: Dict[str, List[str]] = {}
        for level in range(1, 7):
            tag = f"h{level}"
            texts = [h.get_text(strip=True) for h in soup.find_all(tag) if h.get_text(strip=True)]
            if texts:
                headings[tag] = texts

        # Open Graph tags
        open_graph: Dict[str, str] = {}
        for og_tag in soup.find_all("meta", property=re.compile(r"^og:")):
            prop = og_tag.get("property", "")
            content = og_tag.get("content", "")
            if prop and content:
                open_graph[prop] = content

        # schema.org types from JSON-LD
        schema_types: List[str] = []
        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        t = item.get("@type") if isinstance(item, dict) else None
                        if t:
                            schema_types.append(t if isinstance(t, str) else str(t))
                elif isinstance(data, dict):
                    t = data.get("@type")
                    if t:
                        schema_types.append(t if isinstance(t, str) else str(t))
            except (json.JSONDecodeError, Exception):
                pass

        # Visible text and word count
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        full_text = soup.get_text(" ", strip=True)
        word_count = len(full_text.split())
        text_content = full_text[:max_text_chars]

        # Link counts
        link_counts: Dict[str, int] = {}
        if include_links:
            base_domain = urlparse(url).netloc
            all_links = soup.find_all("a", href=True)
            internal = 0
            external = 0
            nofollow = 0
            for a in all_links:
                href = urljoin(url, a["href"])
                rel = a.get("rel", [])
                if isinstance(rel, str):
                    rel = [rel]
                if "nofollow" in rel:
                    nofollow += 1
                if urlparse(href).netloc == base_domain:
                    internal += 1
                else:
                    external += 1
            link_counts = {
                "internal": internal,
                "external": external,
                "nofollow": nofollow,
                "total": internal + external,
            }

        return {
            "status": "success",
            "url": url,
            "http_status": http_status,
            "title": title,
            "meta_description": meta_description,
            "meta_robots": meta_robots,
            "canonical_url": canonical_url,
            "headings": headings,
            "open_graph": open_graph,
            "schema_types": schema_types,
            "word_count": word_count,
            "link_counts": link_counts,
            "text_content": text_content,
        }

    except requests.RequestException as exc:
        return {
            "status": "error",
            "url": url,
            "http_status": getattr(getattr(exc, "response", None), "status_code", None),
            "error": f"HTTP error: {exc}",
        }
    except Exception as exc:
        return {"status": "error", "url": url, "http_status": None, "error": str(exc)}


def extract_all_links(
    url: str,
    internal_only: bool = False,
    external_only: bool = False,
) -> Dict[str, Any]:
    """Extract all <a> href links from a page with anchor text and classification.

    Args:
        url: Absolute page URL.
        internal_only: Return only links to the same domain.
        external_only: Return only links to external domains.

    Returns:
        Dict with status, internal_links list (capped at 100), external_links list
        (capped at 100), and _total counts for each.
    """
    try:
        resp = _get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        base_domain = urlparse(url).netloc
        internal: List[Dict[str, str]] = []
        external: List[Dict[str, str]] = []

        for a in soup.find_all("a", href=True):
            href = _normalize(urljoin(url, a["href"]))
            parsed = urlparse(href)
            if parsed.scheme not in ("http", "https"):
                continue
            anchor = a.get_text(strip=True)[:200]
            rel = a.get("rel", [])
            if isinstance(rel, str):
                rel = [rel]
            is_nofollow = "nofollow" in rel

            entry = {"url": href, "anchor": anchor, "nofollow": is_nofollow}

            if parsed.netloc == base_domain:
                internal.append(entry)
            else:
                external.append(entry)

        result: Dict[str, Any] = {"status": "success", "url": url}

        if not external_only:
            result.update(_cap_list(internal, "internal_links"))
        if not internal_only:
            result.update(_cap_list(external, "external_links"))

        return result

    except requests.RequestException as exc:
        return {"status": "error", "url": url, "error": f"HTTP error: {exc}"}
    except Exception as exc:
        return {"status": "error", "url": url, "error": str(exc)}


def extract_structured_data(url: str) -> Dict[str, Any]:
    """Extract all structured data (JSON-LD and microdata) from a page.

    Covers Article, Product, LocalBusiness, BreadcrumbList, HowTo,
    FAQPage, and any other schema.org types found.

    Args:
        url: Absolute page URL.

    Returns:
        Dict with status, json_ld (list of parsed objects), microdata (list),
        schema_types found, and total counts.
    """
    try:
        resp = _get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # JSON-LD blocks
        json_ld_blocks: List[Any] = []
        schema_types: List[str] = []

        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
                json_ld_blocks.append(data)
                # Collect @type values
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict):
                        t = item.get("@type")
                        if t:
                            schema_types.append(t if isinstance(t, str) else str(t))
            except (json.JSONDecodeError, Exception):
                pass

        # Microdata items
        microdata: List[Dict[str, Any]] = []
        for el in soup.find_all(attrs={"itemscope": True}):
            item_type = el.get("itemtype", "")
            props: Dict[str, List[str]] = {}
            for prop_el in el.find_all(attrs={"itemprop": True}):
                prop_name = prop_el.get("itemprop", "")
                if not prop_name:
                    continue
                value = (
                    prop_el.get("content")
                    or prop_el.get("href")
                    or prop_el.get("src")
                    or prop_el.get_text(strip=True)
                )
                props.setdefault(prop_name, []).append(value)
            microdata.append({"itemtype": item_type, "properties": props})
            # Add microdata types
            if item_type:
                type_name = item_type.split("/")[-1]
                if type_name:
                    schema_types.append(type_name)

        return {
            "status": "success",
            "url": url,
            "json_ld_count": len(json_ld_blocks),
            "json_ld": json_ld_blocks[:_MAX_LINKS_IN_RESPONSE],
            "microdata_count": len(microdata),
            "microdata": microdata[:_MAX_LINKS_IN_RESPONSE],
            "schema_types": list(set(schema_types)),
        }

    except requests.RequestException as exc:
        return {"status": "error", "url": url, "error": f"HTTP error: {exc}"}
    except Exception as exc:
        return {"status": "error", "url": url, "error": str(exc)}


def check_page_status(url: str) -> Dict[str, Any]:
    """Lightweight HEAD request to check a URL's HTTP status and headers.

    Args:
        url: Absolute URL to check.

    Returns:
        Dict with status, http_status, final_url (after redirects), redirect_count,
        x_robots_tag, content_type, and latency_ms.
    """
    try:
        start = time.monotonic()
        resp = requests.head(
            url,
            timeout=_REQUEST_TIMEOUT,
            headers=_DEFAULT_HEADERS,
            allow_redirects=True,
        )
        latency_ms = round((time.monotonic() - start) * 1000)

        redirect_count = len(resp.history)
        final_url = resp.url

        return {
            "status": "success",
            "url": url,
            "http_status": resp.status_code,
            "final_url": final_url,
            "redirect_count": redirect_count,
            "x_robots_tag": resp.headers.get("X-Robots-Tag"),
            "content_type": resp.headers.get("Content-Type"),
            "latency_ms": latency_ms,
        }

    except requests.RequestException as exc:
        return {
            "status": "error",
            "url": url,
            "http_status": getattr(getattr(exc, "response", None), "status_code", None),
            "error": f"HTTP error: {exc}",
        }
    except Exception as exc:
        return {"status": "error", "url": url, "error": str(exc)}


def search_page_text(
    url: str,
    query: str,
    context_chars: int = 200,
) -> Dict[str, Any]:
    """Fetch a page and find text snippets that contain the query string.

    Useful for checking whether a keyword appears on a page and in what context.

    Args:
        url: Absolute page URL.
        query: Text to search for (case-insensitive substring match).
        context_chars: Characters of surrounding context to include per match.

    Returns:
        Dict with status, match_count, and snippets list (capped at 10).
    """
    try:
        resp = _get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)

        query_lower = query.lower()
        text_lower = text.lower()

        snippets: List[str] = []
        start = 0
        while True:
            idx = text_lower.find(query_lower, start)
            if idx == -1:
                break
            snippet_start = max(0, idx - context_chars)
            snippet_end = min(len(text), idx + len(query) + context_chars)
            snippet = text[snippet_start:snippet_end].strip()
            snippets.append(snippet)
            start = idx + len(query)
            if len(snippets) >= 10:
                break

        return {
            "status": "success",
            "url": url,
            "query": query,
            "match_count": len(snippets),
            "snippets": snippets,
        }

    except requests.RequestException as exc:
        return {"status": "error", "url": url, "query": query, "error": f"HTTP error: {exc}"}
    except Exception as exc:
        return {"status": "error", "url": url, "query": query, "error": str(exc)}


def batch_check_page_status(urls: List[str]) -> Dict[str, Any]:
    """Concurrently check HTTP status for a list of URLs using async HEAD requests.

    Uses asyncio + aiohttp with a semaphore of 10 concurrent requests.

    Args:
        urls: List of absolute URLs to check.

    Returns:
        Dict with status, results list (url, http_status, error), summary counts.
    """
    async def _check_one(
        session: aiohttp.ClientSession,
        sem: asyncio.Semaphore,
        url: str,
    ) -> Dict[str, Any]:
        async with sem:
            try:
                async with session.head(
                    url,
                    timeout=aiohttp.ClientTimeout(total=_REQUEST_TIMEOUT),
                    allow_redirects=True,
                    headers=_DEFAULT_HEADERS,
                ) as resp:
                    return {"url": url, "http_status": resp.status, "error": None}
            except asyncio.TimeoutError:
                return {"url": url, "http_status": None, "error": "timeout"}
            except Exception as exc:
                return {"url": url, "http_status": None, "error": str(exc)}

    async def _run_all(urls: List[str]) -> List[Dict[str, Any]]:
        sem = asyncio.Semaphore(10)
        async with aiohttp.ClientSession() as session:
            tasks = [_check_one(session, sem, u) for u in urls]
            return await asyncio.gather(*tasks)

    try:
        capped_urls = urls[:_MAX_LINKS_IN_RESPONSE]
        results = asyncio.run(_run_all(capped_urls))

        success = sum(1 for r in results if r["http_status"] and r["http_status"] < 400)
        errors_4xx = sum(1 for r in results if r["http_status"] and 400 <= r["http_status"] < 500)
        errors_5xx = sum(1 for r in results if r["http_status"] and r["http_status"] >= 500)
        failed = sum(1 for r in results if r["http_status"] is None)

        return {
            "status": "success",
            "total_checked": len(results),
            "urls_skipped": max(0, len(urls) - len(capped_urls)),
            "summary": {
                "ok": success,
                "4xx": errors_4xx,
                "5xx": errors_5xx,
                "failed": failed,
            },
            "results": results,
        }

    except Exception as exc:
        return {"status": "error", "error": str(exc)}


# ---------------------------------------------------------------------------
# Crawl tools
# ---------------------------------------------------------------------------

def crawl_site_links(
    start_url: str,
    max_pages: int = 50,
    max_depth: int = 3,
    same_domain_only: bool = True,
    respect_robots: bool = True,
) -> Dict[str, Any]:
    """BFS crawler that follows internal links from start_url.

    Safety constraints:
    - Hard cap: max_pages is capped at _MAX_PAGES_HARD_LIMIT (200)
    - visited set prevents re-queuing
    - Fragments stripped before queuing
    - same_domain_only=True default (never crawls external sites)
    - Respects robots.txt when respect_robots=True
    - 0.5s politeness delay between fetches

    Args:
        start_url: URL to start crawling from.
        max_pages: Maximum pages to crawl (hard-capped at 200).
        max_depth: Maximum link depth from start_url.
        same_domain_only: Only follow links to same domain (recommended).
        respect_robots: Check robots.txt before fetching each URL.

    Returns:
        Dict with status, pages_crawled, broken_links (4xx/5xx), crawl_graph
        sample (capped at 100 entries), and blocked_by_robots count.
    """
    max_pages = min(max_pages, _MAX_PAGES_HARD_LIMIT)

    rp = _robots_parser(start_url) if respect_robots else None
    user_agent = "SEOAgent"

    visited: set = set()
    queue: deque = deque()
    queue.append((_normalize(start_url), 0))
    visited.add(_normalize(start_url))

    pages_crawled: List[Dict[str, Any]] = []
    broken_links: List[Dict[str, Any]] = []
    crawl_graph: List[Dict[str, Any]] = []
    blocked_by_robots = 0

    while queue and len(pages_crawled) < max_pages:
        current_url, depth = queue.popleft()

        # robots.txt check
        if rp and not rp.can_fetch(user_agent, current_url):
            blocked_by_robots += 1
            continue

        try:
            time.sleep(_CRAWL_DELAY_SECONDS)
            resp = _get(current_url)
            http_status = resp.status_code
        except requests.RequestException as exc:
            pages_crawled.append({
                "url": current_url,
                "depth": depth,
                "http_status": None,
                "error": str(exc),
            })
            broken_links.append({
                "url": current_url,
                "http_status": None,
                "linked_from": None,
                "error": str(exc),
            })
            continue
        except Exception as exc:
            pages_crawled.append({
                "url": current_url,
                "depth": depth,
                "http_status": None,
                "error": str(exc),
            })
            continue

        page_record = {
            "url": current_url,
            "depth": depth,
            "http_status": http_status,
        }

        if http_status >= 400:
            broken_links.append({
                "url": current_url,
                "http_status": http_status,
                "linked_from": None,
            })

        pages_crawled.append(page_record)

        # Only follow links from successful pages within depth limit
        if http_status < 300 and depth < max_depth:
            try:
                soup = BeautifulSoup(resp.text, "html.parser")
                found_links = []
                for a in soup.find_all("a", href=True):
                    href = _normalize(urljoin(current_url, a["href"]))
                    parsed = urlparse(href)
                    if parsed.scheme not in ("http", "https"):
                        continue
                    if same_domain_only and not _same_domain(href, start_url):
                        continue
                    if href not in visited:
                        visited.add(href)
                        queue.append((href, depth + 1))
                        found_links.append(href)

                if len(crawl_graph) < _MAX_LINKS_IN_RESPONSE:
                    crawl_graph.append({
                        "page": current_url,
                        "depth": depth,
                        "links_found": len(found_links),
                        "sample_links": found_links[:5],
                    })
            except Exception:
                pass

    return {
        "status": "success",
        "start_url": start_url,
        "pages_crawled": len(pages_crawled),
        "max_pages_limit": max_pages,
        "broken_links_total": len(broken_links),
        "broken_links": broken_links[:_MAX_LINKS_IN_RESPONSE],
        "blocked_by_robots": blocked_by_robots,
        "crawl_graph": crawl_graph,
        "crawl_graph_total": len(crawl_graph),
    }


def find_broken_links(
    domain_url: str,
    max_pages: int = 30,
) -> Dict[str, Any]:
    """Crawl a site focused on finding broken links (4xx/5xx responses).

    A focused version of crawl_site_links that returns only broken link data
    and which page linked to each broken URL.

    Args:
        domain_url: Root URL of the domain to crawl.
        max_pages: Maximum pages to crawl (hard-capped at 200).

    Returns:
        Dict with status, pages_checked, broken_links list with source page,
        broken_links_total.
    """
    max_pages = min(max_pages, _MAX_PAGES_HARD_LIMIT)

    rp = _robots_parser(domain_url)
    user_agent = "SEOAgent"

    visited: set = set()
    queue: deque = deque()
    start = _normalize(domain_url)
    queue.append((start, 0, None))  # (url, depth, source_page)
    visited.add(start)

    pages_checked = 0
    broken_links: List[Dict[str, Any]] = []

    while queue and pages_checked < max_pages:
        current_url, depth, source_page = queue.popleft()

        if rp and not rp.can_fetch(user_agent, current_url):
            continue

        try:
            time.sleep(_CRAWL_DELAY_SECONDS)
            resp = _get(current_url)
            http_status = resp.status_code
        except requests.RequestException as exc:
            broken_links.append({
                "url": current_url,
                "http_status": None,
                "linked_from": source_page,
                "error": str(exc),
            })
            pages_checked += 1
            continue
        except Exception:
            pages_checked += 1
            continue

        pages_checked += 1

        if http_status >= 400:
            broken_links.append({
                "url": current_url,
                "http_status": http_status,
                "linked_from": source_page,
            })

        # Follow links only from OK pages within domain
        if http_status < 300 and depth < 5:
            try:
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = _normalize(urljoin(current_url, a["href"]))
                    parsed = urlparse(href)
                    if parsed.scheme not in ("http", "https"):
                        continue
                    if not _same_domain(href, domain_url):
                        continue
                    if href not in visited:
                        visited.add(href)
                        queue.append((href, depth + 1, current_url))
            except Exception:
                pass

    return {
        "status": "success",
        "domain_url": domain_url,
        "pages_checked": pages_checked,
        "broken_links_total": len(broken_links),
        "broken_links": broken_links[:_MAX_LINKS_IN_RESPONSE],
    }
