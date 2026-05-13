"""
Example usage of Serper tools with location and country code parameters
"""
from seo_agent.tools.serper_tools import (
    get_keyword_ranking,
    batch_keyword_rankings,
    analyze_serp_features,
    compare_rankings
)

# Example 1: Check ranking in Melbourne, Australia
print("=" * 60)
print("Example 1: Ranking check in Melbourne, Australia")
print("=" * 60)

ranking = get_keyword_ranking(
    keyword="seo services",
    target_domain="example.com",
    location="Melbourne, Victoria, Australia",
    gl="au"
)

print(f"Keyword: {ranking['keyword']}")
print(f"Location: {ranking['metadata']['location']}")
print(f"Country Code: {ranking['metadata']['country_code']}")
print(f"Position: {ranking['position']}")
print()

# Example 2: Batch check in New York, USA
print("=" * 60)
print("Example 2: Batch ranking in New York, USA")
print("=" * 60)

batch_results = batch_keyword_rankings(
    keywords=["digital marketing", "seo agency", "ppc management"],
    target_domain="example.com",
    location="New York, NY, United States",
    gl="us"
)

print(f"Total keywords: {batch_results['summary']['total_keywords']}")
print(f"Keywords found: {batch_results['summary']['keywords_found']}")
print(f"Average position: {batch_results['summary']['average_position']}")
print()

# Example 3: Analyze SERP features in London, UK
print("=" * 60)
print("Example 3: SERP analysis in London, UK")
print("=" * 60)

serp_analysis = analyze_serp_features(
    keyword="best restaurants",
    location="London, England, United Kingdom",
    gl="uk"
)

print(f"Keyword: {serp_analysis['keyword']}")
print(f"Competition level: {serp_analysis['competition_analysis']['level']}")
print(f"Has featured snippet: {serp_analysis['insights']['has_featured_snippet']}")
print(f"PAA questions: {serp_analysis['insights']['paa_count']}")
print()

# Example 4: Compare domains in Toronto, Canada
print("=" * 60)
print("Example 4: Domain comparison in Toronto, Canada")
print("=" * 60)

comparison = compare_rankings(
    keywords=["web design", "website development"],
    domains=["example.com", "competitor1.com", "competitor2.com"],
    location="Toronto, Ontario, Canada",
    gl="ca"
)

print("Domain Summary:")
for domain, stats in comparison['domain_summary'].items():
    print(f"  {domain}: Found {stats['found']} times, Avg position: {stats['average_position']}")
print()

# Example 5: Different cities in the same country
print("=" * 60)
print("Example 5: Sydney vs Melbourne (same country, different cities)")
print("=" * 60)

sydney_ranking = get_keyword_ranking(
    keyword="coffee shops",
    target_domain="example.com",
    location="Sydney, New South Wales, Australia",
    gl="au"
)

melbourne_ranking = get_keyword_ranking(
    keyword="coffee shops",
    target_domain="example.com",
    location="Melbourne, Victoria, Australia",
    gl="au"
)

print(f"Sydney position: {sydney_ranking['position']}")
print(f"Melbourne position: {melbourne_ranking['position']}")
print()

print("=" * 60)
print("Location Parameter Examples:")
print("=" * 60)
print("""
Common location formats:
- United States: "New York, NY, United States" (gl="us")
- Australia: "Melbourne, Victoria, Australia" (gl="au")
- United Kingdom: "London, England, United Kingdom" (gl="uk")
- Canada: "Toronto, Ontario, Canada" (gl="ca")
- Germany: "Berlin, Germany" (gl="de")
- France: "Paris, France" (gl="fr")

Note:
- 'location' = Full city/region name for localized results
- 'gl' = 2-letter country code for Google country domain
""")
