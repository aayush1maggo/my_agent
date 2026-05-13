"""Google Analytics 4 Tools for SEO Agent"""
import csv
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict, List
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from ..auth import get_credentials
from ..config import GA4_DIMENSION_METRIC_SHEET


class GA4FieldValidationError(ValueError):
    """Raised when an invalid GA4 metric or dimension is requested."""


@lru_cache(maxsize=1)
def _load_ga4_field_catalog():
    """Load the GA4 dimension/metric catalog from the provided CSV."""
    sheet_path = Path(GA4_DIMENSION_METRIC_SHEET)
    if not sheet_path.exists():
        return None, None

    dimensions = set()
    metrics = set()

    with sheet_path.open("r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not row:
                continue
            api_name = (
                row.get("API Name")
                or row.get("API name")
                or row.get("API_Name")
                or ""
            ).strip()
            scope = (row.get("Scope") or "").strip().lower()
            if not api_name or not scope:
                continue

            if scope == "dimension":
                dimensions.add(api_name)
            elif scope == "metric":
                metrics.add(api_name)

    return frozenset(dimensions), frozenset(metrics)


def validate_ga4_fields(
    metrics: Optional[List[str]] = None,
    dimensions: Optional[List[str]] = None,
) -> None:
    """Validate GA4 metrics and dimensions against the catalog sheet."""
    dimensions = list(dimensions or [])
    metrics = list(metrics or [])

    valid_dimensions, valid_metrics = _load_ga4_field_catalog()
    if valid_dimensions is None or valid_metrics is None:
        # Catalog not available; skip validation gracefully.
        return

    invalid_dims = sorted({name for name in dimensions if name not in valid_dimensions})
    invalid_metrics = sorted({name for name in metrics if name not in valid_metrics})

    if invalid_dims or invalid_metrics:
        parts = []
        if invalid_dims:
            parts.append(f"dimensions: {', '.join(invalid_dims)}")
        if invalid_metrics:
            parts.append(f"metrics: {', '.join(invalid_metrics)}")
        joined = "; ".join(parts)
        raise GA4FieldValidationError(
            f"Invalid GA4 field(s) requested ({joined}). "
            f"Reference sheet: {GA4_DIMENSION_METRIC_SHEET}"
        )


def get_ga4_client():
    """Get authenticated GA4 client"""
    credentials = get_credentials()
    return BetaAnalyticsDataClient(credentials=credentials)


def get_ga4_metrics(
    property_id: str,
    start_date: str = "30daysAgo",
    end_date: str = "today",
    metrics: Optional[List[str]] = None,
    dimensions: Optional[List[str]] = None
) -> Dict:
    """Fetch GA4 metrics

    Args:
        property_id: Property ID (properties/123456789)
        start_date, end_date: YYYY-MM-DD or NdaysAgo
        metrics, dimensions: Metric/dimension names

    Returns: Dict with rows, totals, metadata
    """
    client = get_ga4_client()

    # Default metrics if none provided
    if metrics is None:
        metrics = [
            'activeUsers',
            'sessions',
            'screenPageViews',
            'bounceRate',
            'averageSessionDuration'
        ]
    else:
        metrics = list(metrics)

    # Default dimensions if none provided
    if dimensions is None:
        dimensions = ['date']
    else:
        dimensions = list(dimensions)

    validate_ga4_fields(metrics=metrics, dimensions=dimensions)

    # Ensure property_id is in correct format
    if not property_id.startswith('properties/'):
        property_id = f'properties/{property_id}'

    request = RunReportRequest(
        property=property_id,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        metrics=[Metric(name=m) for m in metrics],
        dimensions=[Dimension(name=d) for d in dimensions],
    )

    response = client.run_report(request)

    # Parse response
    results = {
        'rows': [],
        'totals': {},
        'metadata': {
            'property_id': property_id,
            'date_range': f'{start_date} to {end_date}',
            'metrics': metrics,
            'dimensions': dimensions,
        }
    }

    # Extract row data
    for row in response.rows:
        row_data = {}
        for i, dimension_value in enumerate(row.dimension_values):
            row_data[dimensions[i]] = dimension_value.value
        for i, metric_value in enumerate(row.metric_values):
            row_data[metrics[i]] = metric_value.value
        results['rows'].append(row_data)

    # Extract totals
    if response.totals:
        for i, metric_value in enumerate(response.totals[0].metric_values):
            results['totals'][metrics[i]] = metric_value.value

    return results


def get_ga4_page_performance(
    property_id: str,
    start_date: str = "30daysAgo",
    end_date: str = "today",
    limit: int = 100
) -> Dict:
    """Analyze page performance

    Args:
        property_id: Property ID
        start_date, end_date: Date range
        limit: Max pages

    Returns: Dict with pages, insights
    """
    client = get_ga4_client()

    if not property_id.startswith('properties/'):
        property_id = f'properties/{property_id}'

    metric_names = [
        'screenPageViews',
        'averageSessionDuration',
        'bounceRate',
        'conversions',
    ]
    dimension_names = ['pagePathPlusQueryString']
    validate_ga4_fields(metrics=metric_names, dimensions=dimension_names)

    request = RunReportRequest(
        property=property_id,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        metrics=[Metric(name=name) for name in metric_names],
        dimensions=[Dimension(name=name) for name in dimension_names],
        limit=limit,
    )

    response = client.run_report(request)

    pages = []
    for row in response.rows:
        page_data = {
            'page_path': row.dimension_values[0].value,
            'page_views': int(row.metric_values[0].value),
            'avg_session_duration': float(row.metric_values[1].value),
            'bounce_rate': float(row.metric_values[2].value),
            'conversions': float(row.metric_values[3].value),
        }
        pages.append(page_data)

    # Sort by page views
    pages.sort(key=lambda x: x['page_views'], reverse=True)

    return {
        'pages': pages,
        'insights': {
            'top_page': pages[0]['page_path'] if pages else None,
            'total_pages_analyzed': len(pages),
            'high_bounce_rate_pages': [p for p in pages if p['bounce_rate'] > 0.7],
        }
    }


def get_ga4_traffic_sources(
    property_id: str,
    start_date: str = "30daysAgo",
    end_date: str = "today"
) -> Dict:
    """Analyze traffic sources

    Args:
        property_id: Property ID
        start_date, end_date: Date range

    Returns: Dict with traffic_sources, channel_summary, insights
    """
    client = get_ga4_client()

    if not property_id.startswith('properties/'):
        property_id = f'properties/{property_id}'

    metric_names = ['sessions', 'activeUsers', 'conversions']
    dimension_names = [
        'sessionDefaultChannelGroup',
        'sessionSource',
        'sessionMedium',
    ]
    validate_ga4_fields(metrics=metric_names, dimensions=dimension_names)

    request = RunReportRequest(
        property=property_id,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        metrics=[Metric(name=name) for name in metric_names],
        dimensions=[Dimension(name=name) for name in dimension_names],
    )

    response = client.run_report(request)

    sources = []
    for row in response.rows:
        source_data = {
            'channel_group': row.dimension_values[0].value,
            'source': row.dimension_values[1].value,
            'medium': row.dimension_values[2].value,
            'sessions': int(row.metric_values[0].value),
            'users': int(row.metric_values[1].value),
            'conversions': float(row.metric_values[2].value),
        }
        sources.append(source_data)

    # Aggregate by channel
    channel_summary = {}
    for source in sources:
        channel = source['channel_group']
        if channel not in channel_summary:
            channel_summary[channel] = {
                'sessions': 0,
                'users': 0,
                'conversions': 0
            }
        channel_summary[channel]['sessions'] += source['sessions']
        channel_summary[channel]['users'] += source['users']
        channel_summary[channel]['conversions'] += source['conversions']

    return {
        'traffic_sources': sources,
        'channel_summary': channel_summary,
        'insights': {
            'top_channel': max(channel_summary.items(), key=lambda x: x[1]['sessions'])[0] if channel_summary else None,
            'organic_search_sessions': channel_summary.get('Organic Search', {}).get('sessions', 0),
        }
    }


def analyze_ga4_trends(
    property_id: str,
    metric: str = 'sessions',
    days: int = 30
) -> Dict:
    """Analyze metric trends over time

    Args:
        property_id: Property ID
        metric: Metric name
        days: Days to analyze

    Returns: Dict with trend data, insights
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    data = get_ga4_metrics(
        property_id=property_id,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        metrics=[metric],
        dimensions=['date']
    )

    if not data['rows']:
        return {'error': 'No data available for trend analysis'}

    # Calculate trend
    values = [float(row[metric]) for row in data['rows']]
    dates = [row['date'] for row in data['rows']]

    avg_value = sum(values) / len(values)
    max_value = max(values)
    min_value = min(values)

    # Simple trend detection (comparing first half to second half)
    mid_point = len(values) // 2
    first_half_avg = sum(values[:mid_point]) / mid_point if mid_point > 0 else 0
    second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point) if mid_point > 0 else 0

    trend_direction = 'increasing' if second_half_avg > first_half_avg else 'decreasing'
    trend_percentage = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0

    return {
        'metric': metric,
        'period': f'{days} days',
        'data_points': list(zip(dates, values)),
        'statistics': {
            'average': avg_value,
            'maximum': max_value,
            'minimum': min_value,
        },
        'trend': {
            'direction': trend_direction,
            'change_percentage': round(trend_percentage, 2),
        },
        'insights': f'The {metric} is {trend_direction} by {abs(round(trend_percentage, 2))}% over the last {days} days.'
    }
