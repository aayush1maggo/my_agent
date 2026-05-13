# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an intelligent SEO multi-agent system built with Google's Agent Development Kit (ADK) that integrates multiple SEO data sources: Google Analytics 4, Google Search Console, Serper.dev (live rankings), SEMrush API, Google Docs/Sheets/Slides, Basecamp API, and sitemap analysis. The system uses Gemini AI with specialized agents for different SEO domains.

The root agent is named "Neo" (coordinator) and is developed by "A.P. Web Solutions".

## Core Architecture

### Multi-Agent System (Google ADK)
The system uses **LLM-driven delegation** with a coordinator and 4 specialized sub-agents:

1. **Neo Coordinator** (`neo_coordinator`) - Root agent
   - Routes requests to specialized agents
   - Handles date/time utilities
   - Uses `transfer_to_agent()` for dynamic delegation
   - Tools: 3 utility tools (datetime functions)

2. **DataInsight** (`data_insight`) - Analytics Agent
   - GA4 metrics and traffic analysis
   - Search Console query/page performance
   - Google Sheets data reporting
   - Tools: 19 (GA4: 4, Search Console: 5, Sheets: 10)

3. **KeywordMaster** (`keyword_master`) - Keyword Research Agent
   - Keyword research and difficulty analysis
   - Live SERP ranking checks (Serper)
   - Backlink analysis (SEMrush)
   - Competitive intelligence
   - Tools: 17 (Serper: 4, SEMrush Keywords: 6, SEMrush Backlinks: 7)

4. **TechAuditor** (`tech_auditor`) - Technical SEO Agent
   - XML sitemap validation
   - 404 detection and protocol consistency
   - Google sitemap standards compliance
   - Tools: 2 (Sitemap analysis tools)

5. **DocManager** (`doc_manager`) - Documentation Agent
   - SEO report creation (Google Docs)
   - Presentation creation (Google Slides)
   - Project management (Basecamp via direct API)
   - Dashboard creation (Google Sheets)
   - Tools: 38 (Docs: 8, Slides: 14, Basecamp: 6, Sheets: 10 shared)

### Agent Framework (Google ADK)
- Built on `google.adk.agents.llm_agent.Agent` from Google's Agent Development Kit
- Uses function-calling paradigm where Python functions are automatically wrapped as `FunctionTools`
- **Parent-Child Hierarchy**: Coordinator has 4 sub-agents registered via `sub_agents` parameter
- **Agent Transfer**: LLM generates `transfer_to_agent(agent_name='target')` for routing
- Each agent defined in `seo_agent/agents/` directory with dedicated file
- Default model: `gemini-2.5-flash-lite` (configured in `seo_agent/config.py`)
- Backward compatible: `seo_agent/agent.py` imports from multi-agent system

### Authentication System
- Centralized OAuth management in `seo_agent/auth.py` via `GoogleAuthManager` class
- Uses pickle-based credential storage in `token.json` (auto-refreshes expired tokens)
- Requires `credentials.json` OAuth file from Google Cloud Console
- Scopes defined in `config.py`: GA4, Search Console, Google Docs, Google Sheets, Google Slides
- First run triggers OAuth flow via browser

### Direct API Integration
All integrations use direct API calls for optimal performance and token efficiency:
- **Basecamp 3 API** - Direct REST API calls via `basecamp_tools.py` (projects, people, todos)
- **SEMrush API** - Direct API integration via `semrush_api_tools.py` (keywords, backlinks, domain data)
- **Google APIs** - OAuth-based access to GA4, Search Console, Docs, Sheets, and Slides
- **Serper.dev** - Direct REST API for live SERP rankings

Note: MCP (Model Context Protocol) integration was removed to reduce token usage from 37k+ to ~3.3k tokens per request.

### Tool Organization
All tools in `seo_agent/tools/` directory:
- `utility_tools.py` - Date/time utilities (current datetime, date range calculation)
- `ga4_tools.py` - Google Analytics 4 API integration (4 tools)
- `search_console_tools.py` - Google Search Console API integration (5 tools)
- `serper_tools.py` - Serper.dev live SERP ranking API (4 tools)
- `semrush_api_tools.py` - Direct SEMrush API integration (13 tools for keywords/backlinks)
- `google_docs_tools.py` - Google Docs API (8 tools for read/write/create documents)
- `google_sheets_tools.py` - Google Sheets API (10 tools for read/write/create spreadsheets)
- `google_slides_tools.py` - Google Slides API (14 tools for presentations, slides, text, images, tables)
- `sitemap_tools.py` - XML sitemap analysis and validation (2 tools)
- `basecamp_tools.py` - Basecamp 3 API integration (6 tools for projects/todolists/todos/people)
- `mcp_tools.py` - DEPRECATED (kept for reference only)

## Development Commands

### Setup
```bash
# Windows
setup.bat

# Unix/Mac
./setup.sh

# Manual setup
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Running the Agent
```bash
# Interactive mode
python run_agent.py

# Programmatic usage
python examples/basic_usage.py
python examples/direct_tool_usage.py
python examples/datetime_usage.py
```

### Testing
```bash
# Run specific test files
python -m pytest tests/test_semrush_api.py
python -m pytest tests/test_sheets_integration.py
python -m pytest tests/test_sitemap_analyzer.py
python -m pytest tests/test_multi_agent.py

# Run all tests
python -m pytest tests/
```

### Environment Setup
Create `seo_agent/.env` with:
```
GOOGLE_API_KEY=your_google_api_key
SERPER_API_KEY=your_serper_api_key
DATAFORSEO_LOGIN=your_dataforseo_login_email
DATAFORSEO_PASSWORD=your_dataforseo_password
SEMRUSH_API_KEY=your_semrush_api_key
BASECAMP_API_KEY=your_basecamp_api_key
BASECAMP_ACCOUNT_ID=your_account_id
GOOGLE_OAUTH_CREDENTIALS=credentials.json
GOOGLE_OAUTH_TOKEN=token.json
```

## Key Implementation Patterns

### Date Handling
- GA4/Search Console accept relative dates: `30daysAgo`, `today`, `yesterday`
- Absolute dates must be `YYYY-MM-DD` format
- Use `calculate_date_range()` from utility_tools to convert natural language to API format
- Always use `get_current_datetime()` for "today" to ensure correct timezone

### API ID Formats
- **GA4 Property ID**: Accept both `123456789` and `properties/123456789` - normalize in tool
- **Search Console Site URL**: Must be exact URL like `https://example.com` (no trailing slash variations)
- **Serper Domain**: Extract from full URL if user provides one

### Error Handling in Tools
- All tools return dictionaries with structured data
- Include error field: `{"error": "message"}` for failures
- Never raise exceptions - catch and return error dict for agent to interpret

### Basecamp API Pattern
Basecamp integration uses direct REST API calls:
- Requires `BASECAMP_API_KEY` (OAuth token) and `BASECAMP_ACCOUNT_ID` in `.env`
- All functions in `basecamp_tools.py` use standard requests library
- Functions: get_projects, get_people, get_todolists, get_todos, create_todo, update_todo
- Returns structured dictionaries with status and data

**Workflow for accessing todos:**
1. Call `get_basecamp_projects()` to get project ID
2. Call `get_basecamp_todolists(project_id)` to get todolist IDs
3. Call `get_basecamp_todos(project_id, todolist_id)` to get todos from specific list
   - OR call `get_basecamp_todos(project_id)` without todolist_id to get ALL todos

Example:
```python
# Get projects
projects = get_basecamp_projects()
# Returns: {'status': 'success', 'projects': [...], 'count': N}

# Get todolists for a project
todolists = get_basecamp_todolists(project_id=43527235)
# Returns: {'status': 'success', 'todolists': [{'id': 123, 'name': 'Sprint Tasks', ...}], 'count': N}

# Get all todos (fetches from all todolists automatically)
todos = get_basecamp_todos(project_id=43527235)
# Returns: {'status': 'success', 'todos': [...], 'count': N}
```

### SEMrush API Pattern
- Direct API integration via `semrush_api_tools.py` (13 functions)
- Covers keyword research, backlinks, and domain analysis
- API key stored in `config.SEMRUSH_API_KEY`
- No MCP wrapper needed - direct function calls only

### Google Docs/Sheets/Slides Pattern
- All functions accept document/spreadsheet/presentation ID or full URL
- Extract ID from URL if needed:
  - Docs: `docs.google.com/document/d/{ID}/edit`
  - Sheets: `docs.google.com/spreadsheets/d/{ID}/edit`
  - Slides: `docs.google.com/presentation/d/{ID}/edit`
- Use `googleapiclient.discovery.build()` with OAuth credentials
- Batch operations preferred for multiple updates
- Slides uses EMU (English Metric Units) for positioning: 1 point = 12,700 EMU

## Agent Behavior Notes

### Agent Instruction Design
The agent's system instruction in `agent.py:92-180` is comprehensive and defines:
- Tool capabilities grouped by category (10 categories)
- When to use datetime utilities (interpret "today", "last month", etc.)
- Required identifier formats (property ID, site URL, dates)
- Focus on actionable insights over raw data
- SEO expertise and strategic recommendations

### Tool Registration
Tools are registered as a flat list in `agent.py:181-255`. Order doesn't matter - agent selects based on descriptions and current context.

### Response Style
Agent returns plain text responses with analysis and recommendations. Not designed for JSON structured output.

## Critical Implementation Details

### OAuth Token Persistence
- `token.json` contains pickled credentials - do NOT commit to git
- `credentials.json` is OAuth client config - also in `.gitignore`
- Token auto-refreshes but may need re-auth if scopes change

### API Authentication
- **Google APIs**: OAuth 2.0 via `GoogleAuthManager` in `auth.py`
- **Basecamp API**: Bearer token authentication via `BASECAMP_API_KEY`
- **SEMrush API**: API key authentication via `SEMRUSH_API_KEY`
- **Serper.dev**: API key authentication via `SERPER_API_KEY`

### Date Range Calculations
`utility_tools.py` provides:
- `calculate_date_range(period)` - Converts "last 30 days" to start/end dates
- `get_time_period_comparison_dates(current_start, current_end)` - Gets previous period for comparison
- Essential for period-over-period analysis

### Sitemap Analysis
`sitemap_tools.py` performs comprehensive validation:
- 404 detection via HTTP HEAD requests
- Protocol consistency (HTTP vs HTTPS)
- Duplicate URL detection
- Google sitemap standards compliance
- Returns actionable recommendations

### Google Slides Implementation
`google_slides_tools.py` provides comprehensive presentation management (14 functions):

**Core Functions:**
- `create_presentation(title)` - Create new blank presentation
- `get_presentation(presentation_id)` - Get presentation structure and metadata
- `list_presentations(max_results, query)` - List presentations in Drive

**Slide Management:**
- `add_slide(presentation_id, position, layout)` - Add new slide with layout (BLANK, TITLE, TITLE_AND_BODY, etc.)
- `delete_slide(presentation_id, slide_id)` - Remove slide
- `duplicate_slide(presentation_id, slide_id, insertion_index)` - Copy existing slide
- `get_slide_thumbnail(presentation_id, slide_id, thumbnail_size)` - Get slide preview image

**Content Addition:**
- `add_title_to_slide(presentation_id, slide_id, title, subtitle)` - Add title/subtitle to slide placeholders
- `add_text_to_slide(presentation_id, slide_id, text, x, y, width, height)` - Add text box with positioning
- `add_bullet_points_to_slide(presentation_id, slide_id, bullet_points, x, y, width, height)` - Add formatted bullet list
- `add_image_to_slide(presentation_id, slide_id, image_url, x, y, width, height)` - Insert image from URL
- `add_table_to_slide(presentation_id, slide_id, rows, columns, x, y, width, height)` - Create table
- `update_table_cell(presentation_id, table_id, row, column, text)` - Update table cell content

**Text Operations:**
- `replace_text_in_presentation(presentation_id, find_text, replace_text, match_case)` - Find/replace across all slides

**Positioning System:**
- Coordinates use points (1 point = 1/72 inch)
- Internally converted to EMU (English Metric Units): 1 point = 12,700 EMU
- Default positions provided for common use cases
- Origin (0,0) is top-left corner of slide

**Common Slide Layouts:**
- `BLANK` - Empty slide
- `TITLE` - Title slide with centered title
- `TITLE_AND_BODY` - Title with content area
- `TITLE_ONLY` - Title with blank space below
- `SECTION_HEADER` - Section divider slide

## Common Gotchas

1. **Token Efficiency**: The system was optimized by removing MCP integration, reducing token usage from 37k+ to ~3.3k per request. Always use direct API calls.

2. **Scope Changes**: If adding new Google API scopes, delete `token.json` to force re-authentication.

3. **Property ID Normalization**: Always handle both formats in tools - users may provide either `123456789` or `properties/123456789`.

4. **Date Format Confusion**: GA4 uses `NdaysAgo` format, but absolute dates need `YYYY-MM-DD`. Don't mix formats.

5. **Basecamp Authentication**: Basecamp requires both `BASECAMP_API_KEY` (OAuth token) and `BASECAMP_ACCOUNT_ID` to be set in `.env`.

6. **Credentials File Location**: OAuth credentials must be in project root as `credentials.json` (or path in `.env`).

7. **Slides Scope Update**: If upgrading from version without Slides support, delete `token.json` to re-authenticate with new `presentations` scope.

## Testing Strategy

Tests in `tests/` directory validate:
- API integrations (`test_semrush_api.py`, `test_sheets_integration.py`)
- Multi-agent system (`test_multi_agent.py`)
- Sitemap validation (`test_sitemap_analyzer.py`)
- Agent functionality (`test_semrush_agent.py`)

Tests may require:
- Valid OAuth credentials (`credentials.json`)
- API keys in environment variables (`.env` file)
- Active internet connection for API calls

## Multi-Agent Patterns

### Agent Transfer Flow
```
User Request → Neo Coordinator
    ├─ Analyzes intent
    ├─ Calculates dates if needed (utility tools)
    └─ Transfers to specialist:
        ├─ transfer_to_agent(agent_name='data_insight')
        ├─ transfer_to_agent(agent_name='keyword_master')
        ├─ transfer_to_agent(agent_name='tech_auditor')
        └─ transfer_to_agent(agent_name='doc_manager')
```

### Delegation Strategy
- **Single-focus requests**: Direct transfer to appropriate specialist
- **Multi-domain requests**: Sequential transfers (e.g., audit → analyze → report)
- **Date calculations**: Coordinator handles before delegating to DataInsight
- **Clarification needed**: Coordinator asks before delegating

### Adding New Tools
1. Create tool function in appropriate `seo_agent/tools/*.py` file
2. Import tool in relevant agent file (`seo_agent/agents/*.py`)
3. Add to agent's `tools` list
4. Update agent's `instruction` to explain when to use the tool
5. Test tool independently, then test agent transfer

### Creating New Agents
1. Create new file in `seo_agent/agents/`
2. Define agent with focused tools and clear description
3. Import in `seo_agent/agents/__init__.py`
4. Register as sub-agent in coordinator's `sub_agents` list
5. Update coordinator's `instruction` with transfer rules
6. Update exports in `seo_agent/agent.py` and `seo_agent/__init__.py`

## File Structure Summary

```
seo_agent/
├── seo_agent/
│   ├── agents/                       # Multi-agent system
│   │   ├── __init__.py              # Agent exports
│   │   ├── coordinator.py           # Neo - Root coordinator
│   │   ├── analytics_agent.py       # DataInsight - GA4/Search Console
│   │   ├── keyword_agent.py         # KeywordMaster - Research/rankings
│   │   ├── technical_agent.py       # TechAuditor - Performance/sitemaps
│   │   └── documentation_agent.py   # DocManager - Docs/Basecamp
│   ├── tools/                        # Tool implementations
│   │   ├── ga4_tools.py
│   │   ├── search_console_tools.py
│   │   ├── serper_tools.py
│   │   ├── semrush_api_tools.py
│   │   ├── google_docs_tools.py
│   │   ├── google_sheets_tools.py
│   │   ├── google_slides_tools.py
│   │   ├── sitemap_tools.py
│   │   ├── basecamp_tools.py
│   │   ├── utility_tools.py
│   │   ├── mcp_tools.py             # DEPRECATED
│   │   └── __init__.py
│   ├── agent.py                     # Backward compatibility imports
│   ├── auth.py                      # OAuth manager
│   ├── config.py                    # Environment config
│   └── __init__.py                  # Package exports
├── examples/                         # Usage examples
├── tests/                            # Test suite
│   └── test_multi_agent.py          # Multi-agent system tests
├── run_agent.py                     # Interactive CLI runner
├── requirements.txt                 # Dependencies
├── credentials.json                 # OAuth client config (not in git)
└── token.json                       # OAuth token storage (not in git)
```

## Dependencies

Core dependencies from `requirements.txt`:
- `google-adk` - Agent Development Kit framework
- `google-auth-oauthlib` - OAuth authentication
- `google-analytics-data` - GA4 API client
- `google-api-python-client` - Generic Google API client (Docs, Sheets, Search Console)
- `requests` - HTTP client for Serper/SEMrush APIs
- `python-dotenv` - Environment variable loading
