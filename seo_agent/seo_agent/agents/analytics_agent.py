"""Analytics Agent - DataInsight
Specialized in GA4 analytics, Search Console data, and reporting via Google Sheets
"""
import pathlib
from datetime import datetime

from google.adk.agents.llm_agent import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from ..tools.ga4_tools import (
    get_ga4_metrics,
    get_ga4_page_performance,
    get_ga4_traffic_sources,
    analyze_ga4_trends
)
from ..tools.ga4_visualization_tools import (
    plot_ga4_event_yoy_bar,
    plot_ga4_event_page_conversions,
)
from ..tools.exploratory_analysis_tools import (
    summarize_tabular_data,
    compute_correlation_matrix,
    plot_tabular_data,
)
from ..tools.search_console_tools import (
    get_search_console_raw,
    get_search_console_queries,
    get_search_console_pages,
    get_search_console_performance,
    analyze_search_opportunities,
    get_keyword_landing_pages,
    compare_periods
)
from ..tools.content_extraction_tools import (
    extract_page_metadata,
    extract_batch_page_metadata,
    extract_page_faqs,
    extract_batch_page_faqs,
)
from ..tools.google_sheets_tools import (
    read_sheet,
    write_to_sheet,
    append_to_sheet,
    create_spreadsheet,
    clear_sheet,
    update_cell,
    batch_update_cells,
    list_spreadsheets,
    get_spreadsheet_metadata,
    add_sheet_tab
)
from ..tools.utility_tools import get_current_datetime
from ..config import DEFAULT_MODEL


TODAY = datetime.now().strftime('%Y-%m-%d')

# Load analytics-reporting skill
_SKILLS_DIR = pathlib.Path(__file__).parent.parent / "skills"
analytics_skill_toolset = SkillToolset(
    skills=[load_skill_from_dir(_SKILLS_DIR / "analytics-reporting")]
)

# Create the Analytics Agent
analytics_agent = Agent(
    model=DEFAULT_MODEL,
    name='data_insight',
    description='DataInsight - Expert in Google Analytics 4 (GA4), Search Console data analysis, and Google Sheets reporting. Can analyze traffic patterns, search performance, user behavior, and create data-driven dashboards for SEO tracking.',
    instruction=f"""Today is {TODAY}. You are DataInsight, expert in GA4, Search Console, and data reporting.

Always use the get_current_datetime tool when you need today's date, the current time, or relative date ranges instead of assuming the date.

**Capabilities:**

1. **Google Analytics 4** (6 tools - TRAFFIC ANALYTICS & VISUALIZATION):
   - Access via GA4 property ID: 'properties/123456789' or '123456789'
   - Traffic metrics: users, sessions, pageviews, engagement
   - Page performance analysis, traffic source breakdown
   - Trend analysis and period-over-period comparisons
   - Visualization tools for event-level comparisons and pages driving key events

2. **Google Search Console** (7 tools - SEARCH PERFORMANCE):
   - Access via site URL: 'https://example.com' (exact format required)
   - Query performance: clicks, impressions, CTR, average position
   - Page-level search performance analysis
   - Opportunity identification: high impressions + low CTR, positions 11-20, good position + low clicks
   - Period comparisons for trend analysis

3. **Google Sheets** (10 tools - DATA REPORTING):
   - Access sheets via URL pattern: docs.google.com/spreadsheets/d/SPREADSHEET_ID
   - Create tracking dashboards and SEO reports
   - Read/write/update cells, batch operations
   - Append data for ongoing tracking
   - Add sheet tabs for organized reporting

4. **Web Content Extraction** (4 tools - ON-PAGE CONTEXT):
   - Fetch single URLs or batches
   - Extract meta titles, descriptions, canonical URLs, robots tags, H1s, and text excerpts for content alignment analysis
   - Extract FAQ questions/answers from JSON-LD FAQPage markup or basic schema.org patterns

5. **Exploratory Data Analysis** (3 tools - ANY TABULAR DATA):
   - You can analyze any tabular data that appears in the current session (for example, results from GA4, Search Console, or spreadsheet tools) using your exploratory analysis tools.
   - Default workflow:
     1) If you already have suitable data in the session history, reuse it instead of calling GA4 or other APIs again.
     2) Use summarize_tabular_data to compute numeric summaries (overall and, if needed, grouped by dimensions such as channel, device, or landing page).
     3) Use compute_correlation_matrix to understand relationships between numeric metrics (for example, sessions, conversions, bounce rate, engagement time).
     4) When the user explicitly asks for a chart, use plot_tabular_data to build seaborn/matplotlib charts (line, bar, scatter, box) for the data you already have.
   - Focus on:
     - Single-variable analysis (distributions, top/bottom performers)
     - Multivariable analysis (correlations, grouped comparisons)
     - Trends and outliers that have clear SEO implications.
   - Always explain what you analyzed, what the key findings are, and why they matter for SEO.

**Date Formats:**
- Absolute: YYYY-MM-DD (e.g., '2025-01-15')
- Relative: 'NdaysAgo' (e.g., '30daysAgo', 'yesterday', 'today')

Provide insights with actionable recommendations. Focus on trends, anomalies, and opportunities.""",
    tools=[
        # Skills (1) - analytics-reporting workflow
        analytics_skill_toolset,
        # Date/Time Utility (1)
        get_current_datetime,
        # GA4 Tools (6)
        get_ga4_metrics,
        get_ga4_page_performance,
        get_ga4_traffic_sources,
        analyze_ga4_trends,
        plot_ga4_event_yoy_bar,
        plot_ga4_event_page_conversions,
        # Exploratory Analysis Tools (3)
        summarize_tabular_data,
        compute_correlation_matrix,
        plot_tabular_data,
        # Search Console Tools (7)
        get_search_console_raw,
        get_search_console_queries,
        get_search_console_pages,
        get_search_console_performance,
        analyze_search_opportunities,
        get_keyword_landing_pages,
        compare_periods,
        # Google Sheets Tools (10)
        read_sheet,
        write_to_sheet,
        append_to_sheet,
        create_spreadsheet,
        clear_sheet,
        update_cell,
        batch_update_cells,
        list_spreadsheets,
        get_spreadsheet_metadata,
        add_sheet_tab,
        # Web Content Extraction (4)
        extract_page_metadata,
        extract_batch_page_metadata,
        extract_page_faqs,
        extract_batch_page_faqs,
    ]
)
