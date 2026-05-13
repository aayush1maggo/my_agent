import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
"""Test SEMrush MCP through the Agent"""
from seo_agent import seo_agent

print("Testing SEMrush MCP Integration through Agent")
print("=" * 60)
print()

# Test 1: Ask agent about SEMrush
print("Test 1: Ask agent to list available SEMrush reports")
print("-" * 60)
try:
    response = seo_agent.run("What SEMrush reports are available? Use semrush_toolkit_info.")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)

# Test 2: Simple query
print("Test 2: Ask agent about SEMrush capabilities")
print("-" * 60)
try:
    response = seo_agent.run("Tell me about your SEMrush integration and what data you can access")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("Test complete")
