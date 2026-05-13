"""SEO Agent Tools"""
from .browser_tools import (
    fetch_page_content,
    extract_all_links,
    extract_structured_data,
    check_page_status,
    search_page_text,
    batch_check_page_status,
    crawl_site_links,
    find_broken_links,
)
from .ga4_tools import (
    get_ga4_metrics,
    get_ga4_page_performance,
    get_ga4_traffic_sources,
    analyze_ga4_trends
)
from .content_extraction_tools import (
    extract_page_metadata,
    extract_batch_page_metadata,
    extract_page_faqs,
    extract_batch_page_faqs,
)
from .search_console_tools import (
    get_search_console_raw,
    get_search_console_queries,
    get_search_console_pages,
    get_search_console_performance,
    analyze_search_opportunities,
    get_keyword_landing_pages,
)
from .serper_tools import (
    get_keyword_ranking,
    batch_keyword_rankings,
    analyze_serp_features
)
from .utility_tools import (
    get_current_datetime,
    calculate_date_range,
    parse_relative_date,
    get_time_period_comparison_dates
)
from .competitor_content_tools import (
    analyze_competitor_topics,
    generate_content_brief,
)
from .everhour_tools import (
    get_everhour_projects,
    search_everhour_tasks,
    get_everhour_task,
    add_time_to_task,
    get_my_time_records,
    update_time_record,
    delete_time_record,
    get_current_timer,
    start_timer,
    stop_current_timer,
)

__all__ = [
    # Browser Tools
    'fetch_page_content',
    'extract_all_links',
    'extract_structured_data',
    'check_page_status',
    'search_page_text',
    'batch_check_page_status',
    'crawl_site_links',
    'find_broken_links',
    # GA4 Tools
    'get_ga4_metrics',
    'get_ga4_page_performance',
    'get_ga4_traffic_sources',
    'analyze_ga4_trends',
    # Content Extraction Tools
    'extract_page_metadata',
    'extract_batch_page_metadata',
    'extract_page_faqs',
    'extract_batch_page_faqs',
    # Search Console Tools
    'get_search_console_raw',
    'get_search_console_queries',
    'get_search_console_pages',
    'get_search_console_performance',
    'analyze_search_opportunities',
    'get_keyword_landing_pages',
    # Serper Tools
    'get_keyword_ranking',
    'batch_keyword_rankings',
    'analyze_serp_features',
    # Utility Tools
    'get_current_datetime',
    'calculate_date_range',
    'parse_relative_date',
    'get_time_period_comparison_dates',
    # Competitor Content Brief Tools
    'analyze_competitor_topics',
    'generate_content_brief',
    # Everhour Timesheet Tools
    'get_everhour_projects',
    'search_everhour_tasks',
    'get_everhour_task',
    'add_time_to_task',
    'get_my_time_records',
    'update_time_record',
    'delete_time_record',
    'get_current_timer',
    'start_timer',
    'stop_current_timer',
]
