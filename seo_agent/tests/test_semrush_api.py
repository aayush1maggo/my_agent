import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
"""Test SEMrush API Direct Tools"""
from seo_agent import seo_agent
from seo_agent.tools.semrush_api_tools import (
    get_keyword_overview,
    get_keyword_organic_results,
    get_related_keywords,
    get_backlinks_overview,
    get_referring_domains
)

print("SEMrush API Tools Test")
print("=" * 60)
print()

# Test 1: Keyword Overview
print("Test 1: Keyword Overview")
print("-" * 60)
try:
    result = get_keyword_overview('seo', 'us')
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Keyword: {result['keyword']}")
        print(f"Database: {result['database_name']}")
        print(f"Rows returned: {result['row_count']}")
        print(f"Columns: {result['columns']}")
        if result['data']:
            print(f"\nSample data:")
            for key, value in result['data'][0].items():
                print(f"  {key}: {value}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print()

# Test 2: Keyword Organic Results
print("Test 2: Keyword Organic Results (Top 5)")
print("-" * 60)
try:
    result = get_keyword_organic_results('python', 'us', limit=5)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Keyword: {result['keyword']}")
        print(f"Results: {result['row_count']}")
        if result['data']:
            print(f"\nTop ranking domains:")
            for i, row in enumerate(result['data'][:5], 1):
                print(f"  {i}. Position {row.get('Po', 'N/A')}: {row.get('Dn', 'N/A')}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"Exception: {e}")

print()
print("=" * 60)
print()

# Test 3: Related Keywords
print("Test 3: Related Keywords (Top 10)")
print("-" * 60)
try:
    result = get_related_keywords('digital marketing', 'us', limit=10)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Seed keyword: {result['seed_keyword']}")
        print(f"Related keywords found: {result['row_count']}")
        if result['data']:
            print(f"\nRelated keywords:")
            for i, row in enumerate(result['data'][:10], 1):
                keyword = row.get('Ph', 'N/A')
                volume = row.get('Nq', 'N/A')
                print(f"  {i}. {keyword} ({volume} searches/month)")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"Exception: {e}")

print()
print("=" * 60)
print()

# Test 4: Backlinks Overview
print("Test 4: Backlinks Overview")
print("-" * 60)
try:
    result = get_backlinks_overview('wikipedia.org', 'root_domain')
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Domain: {result['domain']}")
        print(f"Target type: {result['target_type']}")
        if result['data']:
            print(f"\nBacklink metrics:")
            for key, value in result['data'][0].items():
                print(f"  {key}: {value}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"Exception: {e}")

print()
print("=" * 60)
print()

# Test 5: Referring Domains
print("Test 5: Referring Domains (Top 5)")
print("-" * 60)
try:
    result = get_referring_domains('wikipedia.org', 'root_domain', limit=5)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Domain: {result['domain']}")
        print(f"Referring domains found: {result['row_count']}")
        if result['data']:
            print(f"\nTop referring domains:")
            for i, row in enumerate(result['data'][:5], 1):
                domain = row.get('domain', 'N/A')
                backlinks = row.get('backlinks_num', 'N/A')
                ascore = row.get('domain_ascore', 'N/A')
                print(f"  {i}. {domain} ({backlinks} backlinks, AS: {ascore})")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"Exception: {e}")

print()
print("=" * 60)
print()

# Summary
print("Test Summary")
print("-" * 60)
print(f"Total tools in agent: {len(seo_agent.tools)}")

# Count SEMrush tools
semrush_tools = [
    tool.__name__ for tool in seo_agent.tools
    if hasattr(tool, '__name__') and (
        'semrush' in tool.__name__.lower() or
        'keyword' in tool.__name__.lower() or
        'backlink' in tool.__name__.lower()
    )
]

print(f"SEMrush-related tools: {len(semrush_tools)}")
print("\nSEMrush API tools loaded:")
for i, tool in enumerate(semrush_tools, 1):
    print(f"  {i}. {tool}")

print()
print("Test complete!")
