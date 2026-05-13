"""SEMrush Analytics API v3 - Direct API Tools for Keywords and Backlinks"""
from typing import Dict, Any, Optional, List
import requests
from ..config import SEMRUSH_API_KEY


# Base API URLs
SEMRUSH_API_BASE = "https://api.semrush.com/"
SEMRUSH_BACKLINKS_API_BASE = "https://api.semrush.com/analytics/v1/"

# Regional database codes (most common)
DATABASES = {
    'us': 'United States',
    'uk': 'United Kingdom',
    'ca': 'Canada',
    'au': 'Australia',
    'de': 'Germany',
    'fr': 'France',
    'es': 'Spain',
    'it': 'Italy',
    'br': 'Brazil',
    'in': 'India'
}


def _make_semrush_request(params: Dict[str, Any], base_url: str = SEMRUSH_API_BASE) -> Dict[str, Any]:
    """Make SEMrush API request

    Args:
        params: API parameters
        base_url: Base URL (keywords/backlinks)

    Returns: Dict with API response
    """
    try:
        # Add API key
        if not SEMRUSH_API_KEY:
            return {
                'status': 'error',
                'error': 'SEMrush API key not configured. Set SEMRUSH_API_KEY in .env file'
            }

        params['key'] = SEMRUSH_API_KEY

        # Make request
        response = requests.get(base_url, params=params, timeout=30)

        if response.status_code != 200:
            return {
                'status': 'error',
                'error': f'API returned status {response.status_code}',
                'response': response.text[:500]
            }

        # Parse response (semicolon-delimited format)
        lines = response.text.strip().split('\n')

        if not lines:
            return {
                'status': 'success',
                'data': [],
                'message': 'No data returned'
            }

        # First line is headers
        headers = lines[0].split(';')

        # Parse data rows
        data = []
        for line in lines[1:]:
            if line.strip():
                values = line.split(';')
                row = dict(zip(headers, values))
                data.append(row)

        return {
            'status': 'success',
            'data': data,
            'row_count': len(data),
            'columns': headers
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


# ============================================================================
# KEYWORD REPORTS
# ============================================================================


def get_keyword_overview(
    keyword: str,
    database: str = 'au'
) -> Dict[str, Any]:
    """Get keyword metrics overview

    Args:
        keyword: Keyword to analyze (seo tools)
        database: Region code (default au)

    Returns: Dict with search volume, CPC, competition, difficulty, trends
    """
    params = {
        'type': 'phrase_this',
        'phrase': keyword,
        'database': database,
        'export_columns': 'Ph,Nq,Cp,Co,Nr,Td,In,Kd'
    }

    result = _make_semrush_request(params)

    if result['status'] == 'success':
        result['keyword'] = keyword
        result['database'] = database
        result['database_name'] = DATABASES.get(database, database.upper())

    return result


def get_keyword_overview_batch(
    keywords: List[str],
    database: str = 'au'
) -> Dict[str, Any]:
    """Batch helper to fetch keyword metrics for multiple keywords.

    Args:
        keywords: List of keywords to analyze (duplicates removed)
        database: Region code (default au)

    Returns: Dict with combined keyword metrics
    """
    if not keywords:
        return {
            'status': 'error',
            'error': 'No keywords provided'
        }

    normalized_keywords = []
    for keyword in keywords:
        if isinstance(keyword, str):
            cleaned = keyword.strip()
            if cleaned:
                normalized_keywords.append(cleaned)

    # Remove duplicates while preserving order
    seen = set()
    ordered_keywords = []
    for keyword in normalized_keywords:
        key = keyword.lower()
        if key not in seen:
            seen.add(key)
            ordered_keywords.append(keyword)

    if not ordered_keywords:
        return {
            'status': 'error',
            'error': 'No valid keywords provided'
        }

    combined_data = []
    combined_columns: List[str] = []
    failures = []
    success_count = 0

    for keyword in ordered_keywords:
        overview = get_keyword_overview(keyword, database=database)

        if overview['status'] != 'success':
            failures.append({
                'keyword': keyword,
                'error': overview.get('error', 'Unknown error')
            })
            continue

        success_count += 1
        combined_data.extend(overview.get('data', []))

        for column in overview.get('columns', []):
            if column not in combined_columns:
                combined_columns.append(column)

    if not combined_data:
        return {
            'status': 'error',
            'error': 'Unable to retrieve keyword data',
            'failures': failures
        }

    result = {
        'status': 'success',
        'database': database,
        'database_name': DATABASES.get(database, database.upper()),
        'keywords_requested': len(ordered_keywords),
        'keywords_successful': success_count,
        'row_count': len(combined_data),
        'columns': combined_columns,
        'data': combined_data
    }

    if failures:
        result['partial_failures'] = failures

    return result


def get_keyword_organic_results(
    keyword: str,
    database: str = 'au',
    limit: int = 20
) -> Dict[str, Any]:
    """Get top ranking domains for keyword

    Args:
        keyword: Keyword to analyze
        database: Region code (default au)
        limit: Number of results (default 20, max 100)

    Returns: Dict with domains, URLs, positions, traffic estimates
    """
    params = {
        'type': 'phrase_organic',
        'phrase': keyword,
        'database': database,
        'display_limit': min(limit, 100),
        'export_columns': 'Dn,Ur,Rk,Po,Tr,Tc,Tg'
    }

    result = _make_semrush_request(params)

    if result['status'] == 'success':
        result['keyword'] = keyword
        result['database'] = database

    return result


def get_related_keywords(
    keyword: str,
    database: str = 'au',
    limit: int = 50
) -> Dict[str, Any]:
    """Get related keywords and variations

    Args:
        keyword: Seed keyword
        database: Region code (default au)
        limit: Number of keywords (default 50, max 10000)

    Returns: Dict with related keywords, volume, CPC, difficulty, relevance
    """
    params = {
        'type': 'phrase_related',
        'phrase': keyword,
        'database': database,
        'display_limit': min(limit, 10000),
        'export_columns': 'Ph,Nq,Cp,Co,Nr,Td,In,Kd,Rr'
    }

    result = _make_semrush_request(params)

    if result['status'] == 'success':
        result['seed_keyword'] = keyword
        result['database'] = database

    return result


def get_broad_match_keywords(
    keyword: str,
    database: str = 'au',
    limit: int = 50
) -> Dict[str, Any]:
    """Get broad match keyword variations

    Args:
        keyword: Seed keyword
        database: Region code (default au)
        limit: Number of results (default 50)

    Returns: Dict with broad match keywords and metrics
    """
    params = {
        'type': 'phrase_fullsearch',
        'phrase': keyword,
        'database': database,
        'display_limit': min(limit, 10000),
        'export_columns': 'Ph,Nq,Cp,Co,Nr,Td,In,Kd'
    }

    result = _make_semrush_request(params)

    if result['status'] == 'success':
        result['seed_keyword'] = keyword
        result['database'] = database

    return result


def get_question_keywords(
    keyword: str,
    database: str = 'au',
    limit: int = 30
) -> Dict[str, Any]:
    """Get question-based keyword variations

    Args:
        keyword: Seed keyword
        database: Region code (default au)
        limit: Number of questions (default 30)

    Returns: Dict with question keywords (who/what/when/where/why/how)
    """
    params = {
        'type': 'phrase_questions',
        'phrase': keyword,
        'database': database,
        'display_limit': min(limit, 10000),
        'export_columns': 'Ph,Nq,Cp,Co,Nr,Td,In,Kd'
    }

    result = _make_semrush_request(params)

    if result['status'] == 'success':
        result['seed_keyword'] = keyword
        result['database'] = database

    return result


# ============================================================================
# BACKLINKS REPORTS
# ============================================================================

def get_backlinks_overview(
    domain: str,
    target_type: str = 'root_domain'
) -> Dict[str, Any]:
    """Get backlinks overview for domain

    Args:
        domain: Domain (example.com)
        target_type: root_domain/domain/url

    Returns: Dict with authority score, total backlinks, referring domains, IPs
    """
    params = {
        'type': 'backlinks_overview',
        'target': domain,
        'target_type': target_type,
        'export_columns': 'ascore,total,domains_num,urls_num,ips_num,ipclassc_num,follows_num,nofollows_num,sponsored_num,ugc_num,texts_num,images_num,forms_num,frames_num'
    }

    result = _make_semrush_request(params, SEMRUSH_BACKLINKS_API_BASE)

    if result['status'] == 'success':
        result['domain'] = domain
        result['target_type'] = target_type

    return result


def get_backlinks_list(
    domain: str,
    target_type: str = 'root_domain',
    limit: int = 100
) -> Dict[str, Any]:
    """Get detailed backlinks list

    Args:
        domain: Domain to analyze
        target_type: root_domain/domain/url
        limit: Number of backlinks (default 100, max 1000000)

    Returns: Dict with source/target URLs, anchors, link types, dates
    """
    params = {
        'type': 'backlinks',
        'target': domain,
        'target_type': target_type,
        'display_limit': min(limit, 1000000),
        'export_columns': 'page_ascore,source_url,source_title,target_url,anchor,external_num,internal_num,image,nofollow,redirect,form,frame,first_seen,last_seen'
    }

    result = _make_semrush_request(params, SEMRUSH_BACKLINKS_API_BASE)

    if result['status'] == 'success':
        result['domain'] = domain
        result['target_type'] = target_type

    return result


def get_referring_domains(
    domain: str,
    target_type: str = 'root_domain',
    limit: int = 100
) -> Dict[str, Any]:
    """Get referring domains list

    Args:
        domain: Domain to analyze
        target_type: root_domain/domain/url
        limit: Number of domains (default 100)

    Returns: Dict with referring domains, authority scores, backlink counts
    """
    params = {
        'type': 'backlinks_refdomains',
        'target': domain,
        'target_type': target_type,
        'display_limit': min(limit, 1000000),
        'export_columns': 'domain,domain_ascore,backlinks_num,ip,first_seen,last_seen'
    }

    result = _make_semrush_request(params, SEMRUSH_BACKLINKS_API_BASE)

    if result['status'] == 'success':
        result['domain'] = domain
        result['target_type'] = target_type

    return result


def get_backlink_anchors(
    domain: str,
    target_type: str = 'root_domain',
    limit: int = 100
) -> Dict[str, Any]:
    """Get anchor text analysis

    Args:
        domain: Domain to analyze
        target_type: root_domain/domain/url
        limit: Number of anchors (default 100)

    Returns: Dict with anchor texts, backlink counts, domain counts
    """
    params = {
        'type': 'backlinks_anchors',
        'target': domain,
        'target_type': target_type,
        'display_limit': min(limit, 1000000),
        'export_columns': 'anchor,backlinks_num,domains_num,first_seen,last_seen'
    }

    result = _make_semrush_request(params, SEMRUSH_BACKLINKS_API_BASE)

    if result['status'] == 'success':
        result['domain'] = domain
        result['target_type'] = target_type

    return result


def get_indexed_pages(
    domain: str,
    target_type: str = 'root_domain',
    limit: int = 100
) -> Dict[str, Any]:
    """Get pages receiving backlinks

    Args:
        domain: Domain to analyze
        target_type: root_domain/domain/url
        limit: Number of pages (default 100)

    Returns: Dict with pages, authority scores, backlink counts
    """
    params = {
        'type': 'backlinks_pages',
        'target': domain,
        'target_type': target_type,
        'display_limit': min(limit, 1000000),
        'export_columns': 'url,page_ascore,backlinks_num,domains_num,external_num,internal_num'
    }

    result = _make_semrush_request(params, SEMRUSH_BACKLINKS_API_BASE)

    if result['status'] == 'success':
        result['domain'] = domain
        result['target_type'] = target_type

    return result


def get_backlink_competitors(
    domain: str,
    limit: int = 20
) -> Dict[str, Any]:
    """Get competitors with similar backlink profiles

    Args:
        domain: Domain (root_domain only)
        limit: Number of competitors (default 20)

    Returns: Dict with competitor domains, authority, common/total backlinks
    """
    params = {
        'type': 'backlinks_competitors',
        'target': domain,
        'target_type': 'root_domain',
        'display_limit': min(limit, 1000000),
        'export_columns': 'domain,ascore,common,total'
    }

    result = _make_semrush_request(params, SEMRUSH_BACKLINKS_API_BASE)

    if result['status'] == 'success':
        result['domain'] = domain

    return result


def get_authority_score(
    domain: str
) -> Dict[str, Any]:
    """Get Authority Score profile

    Args:
        domain: Domain (root_domain only)

    Returns: Dict with authority score and distribution by range
    """
    params = {
        'type': 'backlinks_ascore_profile',
        'target': domain,
        'target_type': 'root_domain',
        'export_columns': 'ascore,backlinks_0_9,backlinks_10_19,backlinks_20_29,backlinks_30_39,backlinks_40_49,backlinks_50_59,backlinks_60_69,backlinks_70_79,backlinks_80_89,backlinks_90_100'
    }

    result = _make_semrush_request(params, SEMRUSH_BACKLINKS_API_BASE)

    if result['status'] == 'success':
        result['domain'] = domain

    return result
