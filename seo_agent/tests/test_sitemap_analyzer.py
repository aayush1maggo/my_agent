"""Test Sitemap Analyzer Tool"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from seo_agent.tools.sitemap_tools import analyze_sitemap, get_sitemap_summary

print("Sitemap Analyzer Test")
print("=" * 60)
print()

# Test 1: Get sitemap summary (fast)
print("Test 1: Get Sitemap Summary")
print("-" * 60)
try:
    # Using a real sitemap URL for testing
    result = get_sitemap_summary('https://www.python.org/sitemap.xml')
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Total URLs: {result['total_urls']}")
        print(f"Has sub-sitemaps: {result['has_sub_sitemaps']}")
        print(f"Sample URLs:")
        for url in result.get('sample_urls', [])[:3]:
            print(f"  - {url}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print()

# Test 2: Full sitemap analysis (without URL checking for speed)
print("Test 2: Full Sitemap Analysis (without URL status checks)")
print("-" * 60)
try:
    result = analyze_sitemap(
        'https://www.python.org/sitemap.xml',
        check_urls=False  # Skip URL checking for faster test
    )
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"\nSummary:")
        for key, value in result['summary'].items():
            print(f"  {key}: {value}")

        print(f"\nErrors ({len(result['errors'])}):")
        for error in result['errors'][:5]:
            print(f"  - {error}")

        print(f"\nWarnings ({len(result['warnings'])}):")
        for warning in result['warnings'][:5]:
            print(f"  - {warning}")

        print(f"\nRecommendations ({len(result['recommendations'])}):")
        for rec in result['recommendations'][:5]:
            print(f"  - {rec}")

        print(f"\nAssessment: {result.get('assessment', 'N/A')}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print()

# Test 3: Verify tools are loaded in agent
print("Test 3: Verify Tools in Agent")
print("-" * 60)
try:
    from seo_agent import seo_agent

    sitemap_tools = [
        tool.__name__ for tool in seo_agent.tools
        if hasattr(tool, '__name__') and 'sitemap' in tool.__name__.lower()
    ]

    print(f"Total agent tools: {len(seo_agent.tools)}")
    print(f"Sitemap tools found: {len(sitemap_tools)}")
    for tool in sitemap_tools:
        print(f"  - {tool}")

    if len(sitemap_tools) >= 2:
        print("\n[PASS] Sitemap tools loaded successfully!")
    else:
        print("\n[FAIL] Expected at least 2 sitemap tools")
except Exception as e:
    print(f"Exception: {e}")

print()
print("Test complete!")
