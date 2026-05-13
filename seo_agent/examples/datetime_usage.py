"""Examples of using datetime utility tools"""
import json
from seo_agent.tools.utility_tools import (
    get_current_datetime,
    calculate_date_range,
    parse_relative_date,
    get_time_period_comparison_dates
)


def print_json(data, title=""):
    """Pretty print JSON data"""
    if title:
        print(f"\n{'='*60}")
        print(f"{title}")
        print('='*60)
    print(json.dumps(data, indent=2))


# Example 1: Get current date and time
print_json(
    get_current_datetime(),
    "Current Date and Time"
)

# Example 2: Get current date and time with timezone
print_json(
    get_current_datetime(timezone='US/Eastern'),
    "Current Date/Time (US/Eastern)"
)

# Example 3: Calculate date range for last 30 days
print_json(
    calculate_date_range(days=30),
    "Last 30 Days Date Range"
)

# Example 4: Calculate date range for last 7 days
print_json(
    calculate_date_range(days=7),
    "Last 7 Days Date Range"
)

# Example 5: Calculate custom date range
print_json(
    calculate_date_range(days=90, end_date='2024-01-31'),
    "90 Days Before Jan 31, 2024"
)

# Example 6: Parse relative dates
print("\n" + "="*60)
print("Parsing Relative Dates")
print("="*60)
print(f"'today' -> {parse_relative_date('today')}")
print(f"'yesterday' -> {parse_relative_date('yesterday')}")
print(f"'7daysAgo' -> {parse_relative_date('7daysAgo')}")
print(f"'30daysAgo' -> {parse_relative_date('30daysAgo')}")
print(f"'2 weeks ago' -> {parse_relative_date('2 weeks ago')}")

# Example 7: Get period comparison dates
print_json(
    get_time_period_comparison_dates(period_days=30),
    "Period Comparison (30 days)"
)

# Example 8: Get period comparison dates for weekly comparison
print_json(
    get_time_period_comparison_dates(period_days=7),
    "Period Comparison (7 days)"
)

# Example 9: Using with agent for SEO analysis
print("\n" + "="*60)
print("Example Queries for Agent")
print("="*60)

current = get_current_datetime()
print(f"""
Agent Query Examples:

1. "What is today's date?"
   - Agent will use: get_current_datetime()
   - Response: Today is {current['formatted']['date_long']}

2. "Show me GA4 data for the last 30 days"
   - Agent will use: calculate_date_range(days=30)
   - Then: get_ga4_metrics(property_id='...', start_date='...', end_date='...')

3. "Compare this month vs last month"
   - Agent will use: get_time_period_comparison_dates(period_days=30)
   - Then: compare_periods(site_url='...', current_start='...', ...)

4. "Analyze trends from last week"
   - Agent will use: calculate_date_range(days=7)
   - Then: appropriate analysis tools
""")

# Example 10: Practical date calculations
date_range = calculate_date_range(days=30)
print("\n" + "="*60)
print("Using Date Range for API Calls")
print("="*60)
print(f"""
For GA4 API:
  start_date: '{date_range['ga4_format']['start_date']}'
  end_date: '{date_range['ga4_format']['end_date']}'

For Search Console API:
  startDate: '{date_range['start_date']}'
  endDate: '{date_range['end_date']}'
""")

# Example 11: Multiple time periods
print("="*60)
print("Common Time Periods for SEO Analysis")
print("="*60)

periods = {
    'Last 7 days': calculate_date_range(days=7),
    'Last 30 days': calculate_date_range(days=30),
    'Last 90 days': calculate_date_range(days=90),
    'Last year': calculate_date_range(days=365),
}

for period_name, dates in periods.items():
    print(f"\n{period_name}:")
    print(f"  From: {dates['start_date']}")
    print(f"  To: {dates['end_date']}")
    print(f"  GA4 format: {dates['ga4_format']['start_date']} to {dates['ga4_format']['end_date']}")
