# Multi-Agent Migration Guide

## Overview

The SEO Agent has been refactored from a single-agent system into a **multi-agent architecture** for better organization, maintainability, and performance. This guide explains the changes and how to use the new system.

## What Changed?

### Before (v1.0.0) - Single Agent
```python
from seo_agent import seo_agent

# Single agent with 61 tools
response = seo_agent.run("Analyze my SEO performance")
```

### After (v2.0.0) - Multi-Agent System
```python
from seo_agent import seo_agent  # Still works! (backward compatible)

# Now routes through coordinator to 4 specialized agents:
# - DataInsight (analytics)
# - KeywordMaster (keywords/rankings)
# - TechAuditor (technical SEO)
# - DocManager (reports/projects)

response = seo_agent.run("Analyze my SEO performance")
```

## Architecture Changes

### Old Structure (Single Agent)
```
seo_agent (61 tools)
├── GA4 tools (4)
├── Search Console tools (5)
├── Serper tools (4)
├── SEMrush Keyword tools (6)
├── SEMrush Backlink tools (7)
├── Google Docs tools (8)
├── Google Sheets tools (10)
├── Sitemap tools (2)
├── Chrome DevTools tools (3)
├── Basecamp MCP (1)
├── Utility tools (3)
└── MCP info tools (7)
```

### New Structure (Multi-Agent)
```
Neo Coordinator (3 utility tools)
├── DataInsight (19 tools)
│   ├── GA4 (4)
│   ├── Search Console (5)
│   └── Sheets (10)
│
├── KeywordMaster (17 tools)
│   ├── Serper (4)
│   ├── SEMrush Keywords (6)
│   └── SEMrush Backlinks (7)
│
├── TechAuditor (5 tools)
│   ├── Chrome DevTools (3)
│   └── Sitemap (2)
│
└── DocManager (17 tools)
    ├── Docs (8)
    ├── Basecamp MCP (1)
    └── Sheets (10 - shared)
```

## Backward Compatibility

**All existing code continues to work without changes!**

```python
# Old import - still works
from seo_agent import seo_agent
response = seo_agent.run("Your query")

# Also works
from seo_agent import root_agent
response = root_agent.run("Your query")
```

## New Capabilities

### Direct Agent Access
You can now access specialized agents directly:

```python
from seo_agent import (
    analytics_agent,      # DataInsight
    keyword_agent,        # KeywordMaster
    technical_agent,      # TechAuditor
    documentation_agent   # DocManager
)

# Use specialized agent directly
response = analytics_agent.run("Show GA4 metrics for property 123456789")
```

### How Routing Works

The coordinator (Neo) uses **LLM-driven delegation** to automatically route requests:

```python
# User asks about analytics → Routes to DataInsight
seo_agent.run("Show my GA4 traffic for last 30 days")

# User asks about keywords → Routes to KeywordMaster
seo_agent.run("Research keywords for 'python tutorial'")

# User asks about performance → Routes to TechAuditor
seo_agent.run("Analyze my site's Core Web Vitals")

# User asks for a report → Routes to DocManager
seo_agent.run("Create an SEO audit report")

# Complex requests → Routes sequentially
seo_agent.run("Audit my site and create a report")
# First: TechAuditor analyzes
# Then: DocManager creates report
```

## Benefits of Multi-Agent Architecture

1. **Better Context Management**
   - Each agent has focused tools (5-19 instead of 61)
   - LLM can better understand which tools to use
   - Reduced token usage per agent interaction

2. **Improved Organization**
   - Clear separation of concerns
   - Easier to maintain and debug
   - Easier to add new features

3. **Better Performance**
   - Specialized agents load faster
   - More efficient tool selection
   - Potential for parallel agent execution

4. **Scalability**
   - Easy to add new specialized agents
   - Can extend specific domains without affecting others
   - Better suited for team collaboration

## File Structure

New files created:
```
seo_agent/agents/
├── __init__.py              # Agent exports
├── coordinator.py           # Neo - Routes requests
├── analytics_agent.py       # DataInsight - GA4/Search Console
├── keyword_agent.py         # KeywordMaster - Keywords/Rankings
├── technical_agent.py       # TechAuditor - Performance/Sitemaps
└── documentation_agent.py   # DocManager - Reports/Projects
```

Updated files:
```
seo_agent/agent.py           # Now imports from agents/
seo_agent/__init__.py        # Exports all agents
CLAUDE.md                    # Updated with multi-agent docs
```

New files:
```
tests/test_multi_agent.py    # Tests for multi-agent system
validate_structure.py        # Structure validation script
MIGRATION_GUIDE.md           # This file
```

## Testing

### Validate Structure
```bash
python validate_structure.py
```

### Run Multi-Agent Tests
```bash
# Requires dependencies installed
python -m pytest tests/test_multi_agent.py -v
```

### Test Individual Agents
```python
from seo_agent import analytics_agent, keyword_agent

# Test analytics
print(analytics_agent.name)  # 'data_insight'
print(len(analytics_agent.tools))  # 19

# Test keyword research
print(keyword_agent.name)  # 'keyword_master'
print(len(keyword_agent.tools))  # 17
```

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'google'`:
```bash
pip install -r requirements.txt
```

### Routing Issues
If the coordinator doesn't route correctly:
- Check that agent `description` fields are clear
- Review coordinator's `instruction` for routing rules
- Test direct agent access to isolate issues

### Tool Access
If a tool isn't available:
- Check which agent should have that tool
- Verify tool is imported in agent file
- Check tool is in agent's `tools` list

## Migration Checklist

- [x] Multi-agent structure created
- [x] Backward compatibility maintained
- [x] Tests created
- [x] Documentation updated (CLAUDE.md)
- [x] Validation script created
- [ ] Install dependencies
- [ ] Run tests
- [ ] Test with real queries
- [ ] Update custom integrations (if any)

## Questions?

See `CLAUDE.md` for detailed architecture documentation and implementation patterns.

## Version History

- **v1.0.0**: Single-agent system with 61 tools
- **v2.0.0**: Multi-agent system with coordinator + 4 specialists
