"""Utility Tools for SEO Agent"""
from datetime import datetime, timedelta
from typing import Dict, Optional


def get_current_datetime(timezone: Optional[str] = None) -> Dict:
    """Get current date/time

    Args:
        timezone: Optional (US/Eastern, Europe/London), defaults to system time

    Returns: Dict with datetime, date, time, relative dates, API formats
    """
    now = datetime.now()

    # If timezone is specified, try to use it
    if timezone:
        try:
            import pytz
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
        except ImportError:
            # pytz not available, use system time
            pass
        except Exception:
            # Invalid timezone, use system time
            pass

    return {
        'datetime': now.isoformat(),
        'date': now.strftime('%Y-%m-%d'),
        'time': now.strftime('%H:%M:%S'),
        'day_of_week': now.strftime('%A'),
        'month': now.strftime('%B'),
        'year': now.year,
        'timestamp': int(now.timestamp()),
        'formatted': {
            'full': now.strftime('%Y-%m-%d %H:%M:%S'),
            'date_long': now.strftime('%B %d, %Y'),
            'time_12hr': now.strftime('%I:%M:%S %p'),
        },
        'relative_dates': {
            'today': now.strftime('%Y-%m-%d'),
            'yesterday': (now - timedelta(days=1)).strftime('%Y-%m-%d'),
            'week_ago': (now - timedelta(days=7)).strftime('%Y-%m-%d'),
            'month_ago': (now - timedelta(days=30)).strftime('%Y-%m-%d'),
            'year_ago': (now - timedelta(days=365)).strftime('%Y-%m-%d'),
        },
        'for_apis': {
            'ga4_format': {
                'today': 'today',
                'yesterday': 'yesterday',
                '7_days_ago': '7daysAgo',
                '30_days_ago': '30daysAgo',
                '90_days_ago': '90daysAgo',
            },
            'iso_format': now.strftime('%Y-%m-%d'),
        }
    }


def calculate_date_range(
    days: int = 30,
    end_date: Optional[str] = None
) -> Dict:
    """Calculate date range for analytics

    Args:
        days: Days to look back (default 30)
        end_date: End date YYYY-MM-DD (defaults to today)

    Returns: Dict with start_date, end_date, GA4 format
    """
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            end = datetime.now()
    else:
        end = datetime.now()

    start = end - timedelta(days=days)

    return {
        'start_date': start.strftime('%Y-%m-%d'),
        'end_date': end.strftime('%Y-%m-%d'),
        'days': days,
        'ga4_format': {
            'start_date': f'{days}daysAgo',
            'end_date': 'today' if not end_date else end.strftime('%Y-%m-%d'),
        }
    }


def parse_relative_date(relative_date: str) -> str:
    """Convert relative date to absolute

    Args:
        relative_date: today/yesterday/7daysAgo/30daysAgo

    Returns: Date in YYYY-MM-DD format
    """
    now = datetime.now()

    relative_date = relative_date.lower().strip()

    if relative_date == 'today':
        return now.strftime('%Y-%m-%d')
    elif relative_date == 'yesterday':
        return (now - timedelta(days=1)).strftime('%Y-%m-%d')
    elif 'daysago' in relative_date or 'days ago' in relative_date:
        # Extract number
        import re
        match = re.search(r'(\d+)', relative_date)
        if match:
            days = int(match.group(1))
            return (now - timedelta(days=days)).strftime('%Y-%m-%d')
    elif 'weeksago' in relative_date or 'weeks ago' in relative_date:
        import re
        match = re.search(r'(\d+)', relative_date)
        if match:
            weeks = int(match.group(1))
            return (now - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
    elif 'monthsago' in relative_date or 'months ago' in relative_date:
        import re
        match = re.search(r'(\d+)', relative_date)
        if match:
            months = int(match.group(1))
            return (now - timedelta(days=months*30)).strftime('%Y-%m-%d')

    # If can't parse, return as-is
    return relative_date


def get_time_period_comparison_dates(period_days: int = 30) -> Dict:
    """Get dates for period comparison

    Args:
        period_days: Days per period (default 30)

    Returns: Dict with current/previous period dates
    """
    end_current = datetime.now()
    start_current = end_current - timedelta(days=period_days)

    end_previous = start_current - timedelta(days=1)
    start_previous = end_previous - timedelta(days=period_days)

    return {
        'current_period': {
            'start_date': start_current.strftime('%Y-%m-%d'),
            'end_date': end_current.strftime('%Y-%m-%d'),
            'label': f'Last {period_days} days',
        },
        'previous_period': {
            'start_date': start_previous.strftime('%Y-%m-%d'),
            'end_date': end_previous.strftime('%Y-%m-%d'),
            'label': f'Previous {period_days} days',
        },
        'period_days': period_days,
    }
