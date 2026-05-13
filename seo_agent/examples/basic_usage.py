"""Basic usage examples for SEO Agent"""
from seo_agent import seo_agent

# Example 1: GA4 Metrics Analysis
print("=== Example 1: GA4 Metrics Analysis ===")
response = seo_agent.run("""
Get GA4 metrics for property 123456789 for the last 30 days.
Show me users, sessions, and bounce rate.
""")
print(response)

# Example 2: Search Console Query Analysis
print("\n=== Example 2: Search Console Query Analysis ===")
response = seo_agent.run("""
Show me the top 20 search queries for https://example.com
from the last 30 days with their clicks, impressions, CTR, and position.
""")
print(response)

# Example 3: Keyword Ranking Check
print("\n=== Example 3: Keyword Ranking Check ===")
response = seo_agent.run("""
What's the current ranking for 'python tutorial' for example.com in the US?
Also show me what SERP features are present.
""")
print(response)

# Example 4: SEO Opportunities
print("\n=== Example 4: SEO Opportunities ===")
response = seo_agent.run("""
Find SEO opportunities for https://example.com from the last 30 days.
Focus on queries with high impressions but low CTR.
""")
print(response)

# Example 5: Comprehensive SEO Analysis
print("\n=== Example 5: Comprehensive SEO Analysis ===")
response = seo_agent.run("""
I want a comprehensive SEO analysis for my website https://example.com
with GA4 property 123456789. Please:
1. Analyze traffic trends
2. Show top performing pages
3. Identify search opportunities
4. Check rankings for my top keywords
""")
print(response)
