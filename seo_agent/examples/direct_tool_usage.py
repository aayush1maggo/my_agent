"""Direct tool usage examples without the agent"""
import json
from seo_agent.tools import (
    get_ga4_metrics,
    get_ga4_page_performance,
    get_search_console_queries,
    analyze_search_opportunities,
    get_keyword_ranking,
    analyze_serp_features,
    batch_keyword_rankings
)


def print_json(data, title=""):
    """Pretty print JSON data"""
    if title:
        print(f"\n{'='*60}")
        print(f"{title}")
        print('='*60)
    print(json.dumps(data, indent=2))


# Example 1: Get GA4 Metrics
print_json(
    get_ga4_metrics(
        property_id='123456789',
        start_date='30daysAgo',
        end_date='today',
        metrics=['activeUsers', 'sessions', 'screenPageViews'],
        dimensions=['date']
    ),
    "GA4 Metrics - Last 30 Days"
)

# Example 2: GA4 Page Performance
print_json(
    get_ga4_page_performance(
        property_id='123456789',
        start_date='30daysAgo',
        end_date='today',
        limit=10
    ),
    "GA4 Top 10 Pages by Performance"
)

# Example 3: Search Console Top Queries
print_json(
    get_search_console_queries(
        site_url='https://example.com',
        start_date='2024-01-01',
        end_date='2024-01-31',
        limit=20
    ),
    "Search Console Top 20 Queries"
)

# Example 4: Search Opportunities
print_json(
    analyze_search_opportunities(
        site_url='https://example.com',
        start_date='2024-01-01',
        end_date='2024-01-31',
        min_impressions=100
    ),
    "SEO Opportunities Analysis"
)

# Example 5: Single Keyword Ranking
print_json(
    get_keyword_ranking(
        keyword='python tutorial',
        target_domain='example.com',
        location='us'
    ),
    "Keyword Ranking: 'python tutorial'"
)

# Example 6: Batch Keyword Rankings
print_json(
    batch_keyword_rankings(
        keywords=[
            'python tutorial',
            'web development',
            'seo optimization',
            'machine learning'
        ],
        target_domain='example.com',
        location='us'
    ),
    "Batch Keyword Rankings"
)

# Example 7: SERP Features Analysis
print_json(
    analyze_serp_features(
        keyword='machine learning',
        location='us'
    ),
    "SERP Features Analysis: 'machine learning'"
)

# Example 8: Custom Date Range Analysis
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=7)

print_json(
    get_search_console_queries(
        site_url='https://example.com',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        limit=10
    ),
    "Last 7 Days - Search Console Queries"
)

# Example 9: Device-specific Search Console Data
from seo_agent.tools.search_console_tools import get_search_console_performance

print_json(
    get_search_console_performance(
        site_url='https://example.com',
        start_date='2024-01-01',
        end_date='2024-01-31',
        dimensions=['device', 'country']
    ),
    "Multi-Dimensional Search Console Performance"
)

# Example 10: Competitive Rankings Comparison
from seo_agent.tools.serper_tools import compare_rankings

print_json(
    compare_rankings(
        keywords=['seo tools', 'keyword research', 'rank tracking'],
        domains=['example.com', 'competitor1.com', 'competitor2.com'],
        location='us'
    ),
    "Competitive Ranking Analysis"
)
