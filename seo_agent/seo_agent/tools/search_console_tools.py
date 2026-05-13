"""Google Search Console Tools for SEO Agent"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Literal
from googleapiclient.discovery import build
from ..auth import get_credentials


def get_search_console_service():
    """Get authenticated Search Console service"""
    credentials = get_credentials()
    return build('searchconsole', 'v1', credentials=credentials)


def get_search_console_raw(
    site_url: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    dimensions: Optional[List[str]] = None,
    limit: int = 25000,
) -> Dict:
    """Fetch raw Search Console performance rows for given dimensions.

    Args:
        site_url: Website URL (https://example.com)
        start_date, end_date: YYYY-MM-DD (defaults to last 30 days)
        dimensions: List of dimensions (e.g., ['query', 'page'])
        limit: Max rows (default 25000)

    Returns: Dict with raw rows and metadata.
    """
    service = get_search_console_service()

    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    if not dimensions:
        dimensions = ['query']

    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': dimensions,
        'rowLimit': limit,
    }

    response = service.searchanalytics().query(
        siteUrl=site_url,
        body=request
    ).execute()

    rows = []
    for row in response.get('rows', []):
        keys = {}
        for idx, dim in enumerate(dimensions):
            if idx < len(row.get('keys', [])):
                keys[dim] = row['keys'][idx]

        rows.append({
            'keys': keys,
            'clicks': row['clicks'],
            'impressions': row['impressions'],
            'ctr': round(row['ctr'] * 100, 2),  # percentage
            'position': round(row['position'], 1),
        })

    return {
        'rows': rows,
        'metadata': {
            'site_url': site_url,
            'date_range': f'{start_date} to {end_date}',
            'dimensions': dimensions,
        },
    }


def get_search_console_queries(
    site_url: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 25000,
    dimension: str = 'query'
) -> Dict:
    """Fetch search queries from Search Console

    Args:
        site_url: Website URL (https://example.com)
        start_date, end_date: YYYY-MM-DD (defaults to last 30 days)
        limit: Max rows (default 25000)
        dimension: query/page/country/device

    Returns: Dict with queries, summary, metadata
    """
    raw_data = get_search_console_raw(
        site_url=site_url,
        start_date=start_date,
        end_date=end_date,
        dimensions=[dimension],
        limit=limit,
    )

    queries = []
    for row in raw_data.get('rows', []):
        query_data = {
            dimension: row['keys'].get(dimension),
            'clicks': row['clicks'],
            'impressions': row['impressions'],
            'ctr': row['ctr'],
            'position': row['position'],
        }
        queries.append(query_data)

    # Calculate aggregated metrics
    total_clicks = sum(q['clicks'] for q in queries)
    total_impressions = sum(q['impressions'] for q in queries)
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_position = sum(q['position'] for q in queries) / len(queries) if queries else 0

    return {
        'queries': queries,
        'summary': {
            'total_clicks': total_clicks,
            'total_impressions': total_impressions,
            'average_ctr': round(avg_ctr, 2),
            'average_position': round(avg_position, 1),
            'query_count': len(queries),
        },
        'metadata': {
            'site_url': site_url,
            'date_range': raw_data['metadata']['date_range'],
            'dimension': dimension,
        }
    }


def get_search_console_pages(
    site_url: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 25000
) -> Dict:
    """Fetch page performance from Search Console

    Args:
        site_url: Website URL
        start_date, end_date: YYYY-MM-DD
        limit: Max pages (default 25000)

    Returns: Dict with page performance data
    """
    return get_search_console_queries(
        site_url=site_url,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        dimension='page'
    )


def get_search_console_performance(
    site_url: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    dimensions: Optional[List[str]] = None
) -> Dict:
    """Get comprehensive Search Console performance

    Args:
        site_url: Website URL
        start_date, end_date: YYYY-MM-DD
        dimensions: List of dimensions (default: query/page/country/device)

    Returns: Dict with performance by dimension
    """
    if dimensions is None:
        dimensions = ['query', 'page', 'country', 'device']

    results = {}
    last_metadata = None

    for dimension in dimensions:
        raw_data = get_search_console_raw(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=[dimension],
            limit=25000,
        )

        dimension_data = []
        for row in raw_data.get('rows', []):
            dimension_data.append({
                dimension: row['keys'].get(dimension),
                'clicks': row['clicks'],
                'impressions': row['impressions'],
                'ctr': row['ctr'],
                'position': row['position'],
            })

        results[dimension] = dimension_data
        last_metadata = raw_data.get('metadata')

    return {
        'performance_by_dimension': results,
        'metadata': last_metadata or {
            'site_url': site_url,
            'date_range': None,
            'dimensions': dimensions,
        },
    }


MatchType = Literal['exact', 'contains']


def get_keyword_landing_pages(
    site_url: str,
    keywords: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    match_type: MatchType = 'exact',
    limit: int = 25000,
) -> Dict:
    """Map keywords to landing pages with performance metrics.

    Args:
        site_url: Website URL (https://example.com)
        keywords: List of search queries/keywords to match
        start_date, end_date: YYYY-MM-DD (defaults to last 30 days)
        match_type: 'exact' or 'contains' match on query
        limit: Max rows from Search Console (default 25000)

    Returns: Dict with mappings, summary, metadata
    """
    # Normalize keywords
    normalized_keywords = [k.strip().lower() for k in keywords if k and k.strip()]
    keyword_set = set(normalized_keywords)

    if not normalized_keywords:
        return {
            'mappings': [],
            'summary': {
                'total_clicks': 0,
                'total_impressions': 0,
                'average_ctr': 0.0,
                'mapping_count': 0,
                'unique_queries': 0,
                'unique_pages': 0,
            },
            'metadata': {
                'site_url': site_url,
                'date_range': None,
                'match_type': match_type,
                'keyword_count': 0,
            },
        }

    if match_type not in ('exact', 'contains'):
        match_type = 'exact'

    raw_data = get_search_console_raw(
        site_url=site_url,
        start_date=start_date,
        end_date=end_date,
        dimensions=['query', 'page'],
        limit=limit,
    )

    aggregated: Dict[tuple, Dict] = {}

    for row in raw_data.get('rows', []):
        query = row['keys'].get('query', '')
        page = row['keys'].get('page', '')
        query_norm = query.lower()

        if match_type == 'exact':
            matched = query_norm in keyword_set
        else:  # contains
            matched = any(k in query_norm for k in normalized_keywords)

        if not matched:
            continue

        key = (query, page)
        if key not in aggregated:
            aggregated[key] = {
                'query': query,
                'page': page,
                'clicks': 0,
                'impressions': 0,
                'position_sum': 0.0,
                'row_count': 0,
            }

        entry = aggregated[key]
        entry['clicks'] += row['clicks']
        entry['impressions'] += row['impressions']
        entry['position_sum'] += row['position']
        entry['row_count'] += 1

    mappings = []
    total_clicks = 0
    total_impressions = 0
    queries_seen = set()
    pages_seen = set()

    for entry in aggregated.values():
        impressions = entry['impressions']
        clicks = entry['clicks']
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        avg_position = entry['position_sum'] / entry['row_count'] if entry['row_count'] else 0.0

        queries_seen.add(entry['query'])
        pages_seen.add(entry['page'])

        mappings.append({
            'query': entry['query'],
            'page': entry['page'],
            'clicks': clicks,
            'impressions': impressions,
            'ctr': round(ctr, 2),
            'position': round(avg_position, 1),
        })

        total_clicks += clicks
        total_impressions += impressions

    mappings.sort(key=lambda m: m['clicks'], reverse=True)

    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0

    return {
        'mappings': mappings,
        'summary': {
            'total_clicks': total_clicks,
            'total_impressions': total_impressions,
            'average_ctr': round(avg_ctr, 2),
            'mapping_count': len(mappings),
            'unique_queries': len(queries_seen),
            'unique_pages': len(pages_seen),
        },
        'metadata': {
            'site_url': site_url,
            'date_range': raw_data['metadata']['date_range'],
            'match_type': match_type,
            'keyword_count': len(normalized_keywords),
        },
    }


def analyze_search_opportunities(
    site_url: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_impressions: int = 100
) -> Dict:
    """Identify SEO opportunities from Search Console

    Args:
        site_url: Website URL
        start_date, end_date: YYYY-MM-DD
        min_impressions: Min impressions threshold (default 100)

    Returns: Dict with opportunities, summary, recommendations
    """
    # Get query data (using maximum limit to analyze all opportunities)
    query_data = get_search_console_queries(
        site_url=site_url,
        start_date=start_date,
        end_date=end_date,
        limit=25000
    )

    queries = query_data['queries']

    # Identify opportunities
    opportunities = {
        'high_impressions_low_ctr': [],
        'good_position_low_clicks': [],
        'near_page_one': [],
        'trending_queries': [],
    }

    for q in queries:
        # High impressions but low CTR (below 2%)
        if q['impressions'] >= min_impressions and q['ctr'] < 2.0:
            opportunities['high_impressions_low_ctr'].append({
                'query': q['query'],
                'impressions': q['impressions'],
                'ctr': q['ctr'],
                'position': q['position'],
                'potential': 'Optimize title and meta description to improve CTR'
            })

        # Good position (top 5) but few clicks
        if q['position'] <= 5 and q['clicks'] < 10:
            opportunities['good_position_low_clicks'].append({
                'query': q['query'],
                'position': q['position'],
                'clicks': q['clicks'],
                'impressions': q['impressions'],
                'potential': 'Already ranking well, improve CTR with better snippets'
            })

        # Near page one (positions 11-20)
        if 11 <= q['position'] <= 20 and q['impressions'] >= min_impressions:
            opportunities['near_page_one'].append({
                'query': q['query'],
                'position': q['position'],
                'impressions': q['impressions'],
                'potential': 'Small improvements could move to page one'
            })

    # Sort opportunities by potential impact
    for key in opportunities:
        opportunities[key] = sorted(
            opportunities[key],
            key=lambda x: x.get('impressions', 0),
            reverse=True
        )[:20]  # Top 20 for each category

    return {
        'opportunities': opportunities,
        'summary': {
            'high_impressions_low_ctr_count': len(opportunities['high_impressions_low_ctr']),
            'good_position_low_clicks_count': len(opportunities['good_position_low_clicks']),
            'near_page_one_count': len(opportunities['near_page_one']),
        },
        'recommendations': [
            'Focus on optimizing title tags and meta descriptions for high-impression, low-CTR queries',
            'Improve content quality and relevance for queries ranking on page 2',
            'Consider adding structured data to improve rich snippet appearance',
            'Analyze top-performing competitors for near-page-one queries',
        ],
        'metadata': {
            'site_url': site_url,
            'date_range': f'{start_date} to {end_date}',
        }
    }


def compare_periods(
    site_url: str,
    current_start: str,
    current_end: str,
    previous_start: str,
    previous_end: str
) -> Dict:
    """Compare Search Console performance between periods

    Args:
        site_url: Website URL
        current_start, current_end: Current period dates (YYYY-MM-DD)
        previous_start, previous_end: Previous period dates (YYYY-MM-DD)

    Returns: Dict with current/previous data, changes, insights
    """
    current_data = get_search_console_queries(
        site_url=site_url,
        start_date=current_start,
        end_date=current_end,
        limit=25000
    )

    previous_data = get_search_console_queries(
        site_url=site_url,
        start_date=previous_start,
        end_date=previous_end,
        limit=25000
    )

    current_summary = current_data['summary']
    previous_summary = previous_data['summary']

    # Calculate changes
    changes = {}
    for metric in ['total_clicks', 'total_impressions', 'average_ctr', 'average_position']:
        current_val = current_summary[metric]
        previous_val = previous_summary[metric]

        if previous_val != 0:
            change_pct = ((current_val - previous_val) / previous_val) * 100
        else:
            change_pct = 0

        changes[metric] = {
            'current': current_val,
            'previous': previous_val,
            'change': current_val - previous_val,
            'change_percentage': round(change_pct, 2),
        }

    return {
        'current_period': current_data,
        'previous_period': previous_data,
        'changes': changes,
        'insights': {
            'clicks_trend': 'increased' if changes['total_clicks']['change'] > 0 else 'decreased',
            'position_trend': 'improved' if changes['average_position']['change'] < 0 else 'declined',
        }
    }
