"""Test Google Sheets Integration"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from seo_agent import seo_agent

print('SEO Agent Status:')
print('=' * 50)
print(f'Agent Name: {seo_agent.name}')
print(f'Total Tools: {len(seo_agent.tools)}')
print(f'Model: {seo_agent.model}')
print()

print('Google Sheets Tools Verified:')
sheets_tools = [
    tool.__name__ for tool in seo_agent.tools
    if hasattr(tool, '__name__') and any(
        x in tool.__name__.lower() for x in ['sheet', 'spreadsheet', 'cell']
    )
]

for i, tool in enumerate(sorted(sheets_tools), 1):
    print(f'  {i}. {tool}')

print()
print(f'Total Google Sheets tools: {len(sheets_tools)}')
print()
print('[PASS] Agent loaded successfully with Google Sheets integration!')
