"""Sitemap Analyzer Tool for SEO Optimization"""
from typing import Dict, Any, List, Optional
import asyncio
import aiohttp
from usp.tree import sitemap_tree_for_homepage
from datetime import datetime
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import requests


def analyze_sitemap(sitemap_url: str, check_urls: bool = True, max_urls_to_check: int = 100) -> Dict[str, Any]:
    """Analyze sitemap for SEO errors

    Args:
        sitemap_url: Sitemap URL (https://example.com/sitemap.xml)
        check_urls: Check for 404s (default True)
        max_urls_to_check: Max URLs to check (default 100)

    Returns: Dict with summary, errors, warnings, recommendations, url_status
    """
    try:
        result = {
            'status': 'success',
            'sitemap_url': sitemap_url,
            'analyzed_at': datetime.now().isoformat(),
            'summary': {},
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'url_status': {}
        }

        # Try to parse the sitemap with fallback methods
        all_urls = []

        try:
            # Method 1: Try ultimate-sitemap-parser
            tree = sitemap_tree_for_homepage(sitemap_url)
            for page in tree.all_pages():
                all_urls.append({
                    'url': page.url,
                    'lastmod': page.last_modified,
                    'priority': page.priority,
                    'changefreq': page.change_frequency
                })
        except Exception as parse_error:
            # Method 2: Fallback to direct XML parsing
            try:
                response = requests.get(sitemap_url, timeout=30)
                response.raise_for_status()

                # Parse XML directly
                root = ET.fromstring(response.content)

                # Handle different sitemap namespaces
                namespaces = {
                    'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                    'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'
                }

                # Try to find URL entries
                urls = root.findall('.//sm:url', namespaces) or root.findall('.//ns:url', namespaces) or root.findall('.//url')

                if not urls:
                    # Check if it's a sitemap index
                    sitemaps = root.findall('.//sm:sitemap', namespaces) or root.findall('.//ns:sitemap', namespaces) or root.findall('.//sitemap')

                    if sitemaps:
                        result['is_sitemap_index'] = True
                        result['sub_sitemaps'] = []

                        for sitemap in sitemaps[:10]:  # Limit to first 10 sub-sitemaps
                            loc = sitemap.find('.//sm:loc', namespaces) or sitemap.find('.//ns:loc', namespaces) or sitemap.find('.//loc')
                            if loc is not None and loc.text:
                                result['sub_sitemaps'].append(loc.text)

                        result['summary']['sitemap_type'] = 'sitemap_index'
                        result['summary']['sub_sitemap_count'] = len(sitemaps)
                        result['recommendations'].append(
                            f"This is a sitemap index with {len(sitemaps)} sub-sitemaps. "
                            "Analyze individual sitemaps for detailed results."
                        )
                        return result

                # Extract URL data
                for url_elem in urls:
                    loc = url_elem.find('.//sm:loc', namespaces) or url_elem.find('.//ns:loc', namespaces) or url_elem.find('.//loc')
                    lastmod = url_elem.find('.//sm:lastmod', namespaces) or url_elem.find('.//ns:lastmod', namespaces) or url_elem.find('.//lastmod')
                    priority = url_elem.find('.//sm:priority', namespaces) or url_elem.find('.//ns:priority', namespaces) or url_elem.find('.//priority')
                    changefreq = url_elem.find('.//sm:changefreq', namespaces) or url_elem.find('.//ns:changefreq', namespaces) or url_elem.find('.//changefreq')

                    if loc is not None and loc.text:
                        all_urls.append({
                            'url': loc.text,
                            'lastmod': lastmod.text if lastmod is not None else None,
                            'priority': priority.text if priority is not None else None,
                            'changefreq': changefreq.text if changefreq is not None else None
                        })

            except Exception as fallback_error:
                return {
                    'status': 'error',
                    'error': f"Failed to parse sitemap. Primary error: {str(parse_error)}. Fallback error: {str(fallback_error)}",
                    'sitemap_url': sitemap_url,
                    'message': 'Could not parse the sitemap. Please check the URL and ensure it contains valid XML.'
                }

        # Summary statistics
        result['summary'] = {
            'total_urls': len(all_urls),
            'has_lastmod': sum(1 for u in all_urls if u['lastmod']),
            'has_priority': sum(1 for u in all_urls if u['priority']),
            'has_changefreq': sum(1 for u in all_urls if u['changefreq']),
        }

        # Check sitemap size limits
        if result['summary']['total_urls'] > 50000:
            result['errors'].append(
                f"Sitemap exceeds maximum URL limit: {result['summary']['total_urls']} URLs "
                f"(maximum: 50,000). Split into multiple sitemaps."
            )

        # Check for protocol consistency
        http_urls = [u for u in all_urls if u['url'].startswith('http://')]
        https_urls = [u for u in all_urls if u['url'].startswith('https://')]

        if http_urls and https_urls:
            result['warnings'].append(
                f"Mixed protocols detected: {len(http_urls)} HTTP and {len(https_urls)} HTTPS URLs. "
                "Use HTTPS consistently for better SEO."
            )
        elif http_urls:
            result['warnings'].append(
                f"All {len(http_urls)} URLs use HTTP. Consider migrating to HTTPS for better security and SEO."
            )

        # Check for duplicate URLs
        url_list = [u['url'] for u in all_urls]
        duplicates = set([url for url in url_list if url_list.count(url) > 1])
        if duplicates:
            result['errors'].append(
                f"Found {len(duplicates)} duplicate URLs in sitemap. Each URL should appear only once."
            )
            result['duplicate_urls'] = list(duplicates)[:10]  # Show first 10

        # Check for relative URLs
        relative_urls = [u for u in all_urls if not u['url'].startswith(('http://', 'https://'))]
        if relative_urls:
            result['errors'].append(
                f"Found {len(relative_urls)} relative URLs. All URLs must be absolute (include protocol and domain)."
            )

        # Check if changefreq or priority are used (Google ignores these)
        if result['summary']['has_changefreq'] > 0:
            result['recommendations'].append(
                f"Remove <changefreq> tags ({result['summary']['has_changefreq']} URLs). "
                "Google ignores this tag. It adds unnecessary bloat to your sitemap."
            )

        if result['summary']['has_priority'] > 0:
            result['recommendations'].append(
                f"Remove <priority> tags ({result['summary']['has_priority']} URLs). "
                "Google ignores this tag. It adds unnecessary bloat to your sitemap."
            )

        # Check lastmod dates
        if result['summary']['has_lastmod'] == 0:
            result['recommendations'].append(
                "Add <lastmod> tags to help search engines understand when content was updated. "
                "This is one of the few tags Google actually uses."
            )
        elif result['summary']['has_lastmod'] < result['summary']['total_urls']:
            missing = result['summary']['total_urls'] - result['summary']['has_lastmod']
            result['recommendations'].append(
                f"Add <lastmod> tags to {missing} URLs that are missing them."
            )

        # Validate lastmod dates
        future_dates = []
        invalid_dates = []
        for u in all_urls:
            if u['lastmod']:
                try:
                    lastmod_date = datetime.fromisoformat(u['lastmod'].replace('Z', '+00:00'))
                    # Compare with current time (handle both timezone-aware and naive datetimes)
                    current_time = datetime.now(lastmod_date.tzinfo) if lastmod_date.tzinfo else datetime.now()
                    if lastmod_date > current_time:
                        future_dates.append(u['url'])
                except (ValueError, AttributeError, TypeError):
                    invalid_dates.append(u['url'])

        if future_dates:
            result['errors'].append(
                f"Found {len(future_dates)} URLs with future dates in <lastmod>. Dates cannot be in the future."
            )

        if invalid_dates:
            result['errors'].append(
                f"Found {len(invalid_dates)} URLs with invalid date formats in <lastmod>. "
                "Use W3C Datetime format (ISO 8601)."
            )

        # Check URL status codes (if enabled)
        if check_urls and all_urls:
            urls_to_check = [u['url'] for u in all_urls[:max_urls_to_check]]
            print(f"Checking HTTP status for {len(urls_to_check)} URLs...")

            url_status = asyncio.run(_check_urls_async(urls_to_check))

            # Categorize status codes
            status_404 = [url for url, status in url_status.items() if status == 404]
            status_3xx = [url for url, status in url_status.items() if 300 <= status < 400]
            status_5xx = [url for url, status in url_status.items() if status and status >= 500]
            status_error = [url for url, status in url_status.items() if status is None]

            result['url_status'] = {
                'checked': len(url_status),
                'status_200': len([s for s in url_status.values() if s == 200]),
                'status_404': len(status_404),
                'status_3xx_redirects': len(status_3xx),
                'status_5xx_errors': len(status_5xx),
                'connection_errors': len(status_error)
            }

            if status_404:
                result['errors'].append(
                    f"Found {len(status_404)} URLs returning 404 (Not Found). Remove these from your sitemap."
                )
                result['urls_404'] = status_404[:20]  # Show first 20

            if status_3xx:
                result['warnings'].append(
                    f"Found {len(status_3xx)} URLs with redirects. Use final destination URLs in sitemap."
                )
                result['urls_redirects'] = status_3xx[:10]

            if status_5xx:
                result['errors'].append(
                    f"Found {len(status_5xx)} URLs returning server errors (5xx). Fix server issues."
                )
                result['urls_5xx'] = status_5xx[:10]

            if status_error:
                result['warnings'].append(
                    f"Could not connect to {len(status_error)} URLs. Check if they're accessible."
                )

            if len(all_urls) > max_urls_to_check:
                result['url_status']['note'] = (
                    f"Only checked first {max_urls_to_check} URLs out of {len(all_urls)} total. "
                    f"Increase max_urls_to_check parameter to check more."
                )

        # Domain consistency check
        parsed_sitemap = urlparse(sitemap_url)
        sitemap_domain = parsed_sitemap.netloc

        different_domains = set()
        for u in all_urls[:100]:  # Check first 100
            parsed_url = urlparse(u['url'])
            if parsed_url.netloc != sitemap_domain:
                different_domains.add(parsed_url.netloc)

        if different_domains:
            result['warnings'].append(
                f"Found URLs from different domains: {', '.join(list(different_domains)[:5])}. "
                "Ensure all domains are verified in Google Search Console."
            )

        # Add general recommendations
        if result['summary']['total_urls'] < 50:
            result['recommendations'].append(
                f"Sitemap has only {result['summary']['total_urls']} URLs. "
                "Ensure all important pages are included."
            )

        if result['summary']['total_urls'] > 10000:
            result['recommendations'].append(
                "Consider splitting large sitemap into multiple smaller sitemaps organized by content type "
                "(e.g., blog posts, products, categories) for better tracking."
            )

        # Overall assessment
        error_count = len(result['errors'])
        warning_count = len(result['warnings'])

        if error_count == 0 and warning_count == 0:
            result['assessment'] = "Excellent! Your sitemap follows SEO best practices."
        elif error_count == 0:
            result['assessment'] = f"Good! No critical errors, but {warning_count} warnings to review."
        else:
            result['assessment'] = f"Action needed: {error_count} errors and {warning_count} warnings found."

        return result

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'sitemap_url': sitemap_url,
            'message': 'Failed to analyze sitemap. Ensure the URL is correct and accessible.'
        }


async def _check_urls_async(urls: List[str]) -> Dict[str, Optional[int]]:
    """Check HTTP status codes async

    Args:
        urls: List of URLs

    Returns: Dict mapping URL to status code (None if error)
    """
    async def check_url(session: aiohttp.ClientSession, url: str) -> tuple:
        try:
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True) as response:
                return url, response.status
        except asyncio.TimeoutError:
            return url, None
        except Exception:
            return url, None

    async with aiohttp.ClientSession() as session:
        tasks = [check_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return dict(results)


def get_sitemap_summary(sitemap_url: str) -> Dict[str, Any]:
    """Get quick sitemap summary

    Args:
        sitemap_url: Sitemap URL

    Returns: Dict with total URLs, sample URLs, sub-sitemap info
    """
    try:
        tree = sitemap_tree_for_homepage(sitemap_url)

        all_urls = list(tree.all_pages())

        return {
            'status': 'success',
            'sitemap_url': sitemap_url,
            'total_urls': len(all_urls),
            'sample_urls': [page.url for page in all_urls[:5]],
            'has_sub_sitemaps': len(tree.sub_sitemaps) > 0,
            'sub_sitemap_count': len(tree.sub_sitemaps) if hasattr(tree, 'sub_sitemaps') else 0
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'sitemap_url': sitemap_url
        }
