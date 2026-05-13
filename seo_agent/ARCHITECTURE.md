# SEO Agent - Multi-Agent Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SEO Multi-Agent System                      │
│                    (Google ADK - LLM-Driven Delegation)             │
└─────────────────────────────────────────────────────────────────────┘

                              User Query
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Neo Coordinator                                │
│                    (neo_coordinator)                                │
│                                                                     │
│  Role: Intelligent request routing                                 │
│  Tools: 3 (datetime utilities)                                     │
│  Logic: LLM analyzes intent → transfer_to_agent()                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
         ┌──────────────┐  ┌──────────┐  ┌──────────┐
         │              │  │          │  │          │
         ▼              ▼  ▼          ▼  ▼          ▼

┌─────────────────┐ ┌────────────────┐ ┌───────────────┐ ┌──────────────────┐
│  DataInsight    │ │ KeywordMaster  │ │  TechAuditor  │ │   DocManager     │
│ (data_insight)  │ │(keyword_master)│ │(tech_auditor) │ │ (doc_manager)    │
│                 │ │                │ │               │ │                  │
│ Analytics &     │ │ Keyword        │ │ Technical     │ │ Documentation &  │
│ Reporting       │ │ Research       │ │ SEO           │ │ Project Mgmt     │
│                 │ │                │ │               │ │                  │
│ Tools: 19       │ │ Tools: 17      │ │ Tools: 5      │ │ Tools: 17        │
└─────────────────┘ └────────────────┘ └───────────────┘ └──────────────────┘
        │                   │                  │                   │
        ▼                   ▼                  ▼                   ▼

┌─────────────────┐ ┌────────────────┐ ┌───────────────┐ ┌──────────────────┐
│ GA4: 4          │ │ Serper: 4      │ │ DevTools: 3   │ │ Docs: 8          │
│ Console: 5      │ │ Keywords: 6    │ │ Sitemap: 2    │ │ Basecamp: 1      │
│ Sheets: 10      │ │ Backlinks: 7   │ │               │ │ Sheets: 10       │
└─────────────────┘ └────────────────┘ └───────────────┘ └──────────────────┘
```

## Agent Details

### 1. Neo Coordinator (Root Agent)

**Name:** `neo_coordinator`
**Role:** Request routing and coordination
**Personality:** "Neo, the SEO orchestrator"

**Responsibilities:**
- Analyze user requests
- Calculate dates when needed
- Route to appropriate specialist
- Coordinate multi-domain requests

**Tools (3):**
- `get_current_datetime` - Current date/time
- `calculate_date_range` - Date range calculations
- `get_time_period_comparison_dates` - Period comparisons

**Routing Strategy:**
```
"Analyze GA4 traffic"        → DataInsight
"Research keywords"          → KeywordMaster
"Check Core Web Vitals"      → TechAuditor
"Create audit report"        → DocManager
"Audit and create report"    → TechAuditor → DocManager (sequential)
```

---

### 2. DataInsight (Analytics Agent)

**Name:** `data_insight`
**Role:** Analytics and data reporting
**Personality:** "DataInsight - Analytics and reporting specialist"

**Responsibilities:**
- GA4 traffic analysis
- Search Console performance
- Data visualization in Sheets
- Period-over-period comparisons
- SEO opportunity identification

**Tools (19):**
- **GA4 (4):** Metrics, page performance, traffic sources, trends
- **Search Console (5):** Queries, pages, performance, opportunities, comparisons
- **Google Sheets (10):** Read, write, append, create, update, batch operations

**Use Cases:**
- "Show me GA4 traffic for last 30 days"
- "Analyze Search Console performance"
- "Find SEO opportunities"
- "Create a traffic dashboard"

---

### 3. KeywordMaster (Keyword Research Agent)

**Name:** `keyword_master`
**Role:** Keyword research and competitive analysis
**Personality:** "KeywordMaster - SEO research and competitive analysis expert"

**Responsibilities:**
- Keyword research and discovery
- Live ranking checks
- SERP feature analysis
- Backlink analysis
- Competitive intelligence

**Tools (17):**
- **Serper (4):** Ranking checks, batch rankings, SERP features, competitor comparisons
- **SEMrush Keywords (6):** Overview, organic results, related keywords, difficulty, broad match, questions
- **SEMrush Backlinks (7):** Overview, list, referring domains, anchors, indexed pages, competitors, authority

**Use Cases:**
- "Research keywords for my blog"
- "Check our ranking for 'python tutorial'"
- "Analyze backlink profile"
- "Compare our rankings to competitors"

---

### 4. TechAuditor (Technical SEO Agent)

**Name:** `tech_auditor`
**Role:** Technical SEO and performance analysis
**Personality:** "TechAuditor - Technical SEO and performance analyst"

**Responsibilities:**
- Core Web Vitals analysis
- Performance bottleneck identification
- Sitemap validation
- Technical SEO audits
- JavaScript error detection

**Tools (5):**
- **Chrome DevTools (3):** List tools, query capabilities, page performance analysis
- **Sitemap (2):** Full analysis, quick summary

**Use Cases:**
- "Analyze page performance"
- "Check Core Web Vitals"
- "Audit my sitemap"
- "Find technical SEO issues"

---

### 5. DocManager (Documentation Agent)

**Name:** `doc_manager`
**Role:** Documentation and project management
**Personality:** "DocManager - Documentation and project coordination specialist"

**Responsibilities:**
- SEO report creation
- Content brief writing
- Project tracking in Basecamp
- Dashboard creation
- Client deliverables

**Tools (17):**
- **Google Docs (8):** Read, create, append, replace, insert, list, metadata, clear
- **Basecamp MCP (1):** Full project management toolset
- **Google Sheets (10):** Shared with DataInsight for reporting

**Use Cases:**
- "Create an SEO audit report"
- "Write a content brief"
- "Track project tasks in Basecamp"
- "Create a keyword tracking spreadsheet"

### Sequential Workflows

- **basecamp_workflow**: Two-step automation for Basecamp reporting. DocManager clone pulls todos/todolists/comments and assembles the structured summary, then KeywordMaster clone researches fresh SEO/CRO strategies for the Next Steps list.
- **keyword_mapping_workflow**: Keyword research and mapping pipeline. KeywordMaster clone compiles service/location keyword clusters plus metadata guidance, followed by a DocManager clone that builds a Google Sheets workbook with `Keyword Research` and `Keyword Mapping` tabs populated from the research.

---

## Communication Flow

### Simple Request (Single Agent)
```
User: "Show GA4 metrics for last 30 days"
  │
  ▼
Coordinator: Analyzes → "This is analytics" → transfer_to_agent('data_insight')
  │
  ▼
DataInsight: Executes GA4 tools → Returns results
  │
  ▼
User: Receives analytics results
```

### Complex Request (Multiple Agents)
```
User: "Audit my site and create a report"
  │
  ▼
Coordinator: "Need technical audit first"
  │
  ▼
TechAuditor: Runs sitemap + performance analysis
  │
  ▼
Coordinator: "Now need report"
  │
  ▼
DocManager: Creates report with TechAuditor's findings
  │
  ▼
User: Receives comprehensive audit report
```

### Date Calculation Request
```
User: "Show Search Console data for last month"
  │
  ▼
Coordinator:
  1. Calls calculate_date_range("last month")
  2. Gets start_date, end_date
  3. transfer_to_agent('data_insight') with dates
  │
  ▼
DataInsight: Fetches Search Console data with calculated dates
  │
  ▼
User: Receives last month's data
```

## Tool Distribution Matrix

| Tool Category | Total | DataInsight | KeywordMaster | TechAuditor | DocManager | Coordinator |
|---------------|-------|-------------|---------------|-------------|------------|-------------|
| GA4 | 4 | ✓ | | | | |
| Search Console | 5 | ✓ | | | | |
| Serper | 4 | | ✓ | | | |
| SEMrush Keywords | 6 | | ✓ | | | |
| SEMrush Backlinks | 7 | | ✓ | | | |
| Chrome DevTools | 3 | | | ✓ | | |
| Sitemap | 2 | | | ✓ | | |
| Google Docs | 8 | | | | ✓ | |
| Google Sheets | 10 | ✓ | | | ✓ (shared) | |
| Basecamp MCP | 1 | | | | ✓ | |
| Datetime Utils | 3 | | | | | ✓ |
| **TOTAL** | **53** | **19** | **17** | **5** | **19** | **3** |

*Note: Google Sheets tools (10) are shared between DataInsight and DocManager, so total unique tools is 53, but distributed count is 63*

## Integration Points

### OAuth Authentication
All agents share the same OAuth credentials managed by `GoogleAuthManager`:
- GA4, Search Console, Docs, Sheets use same token
- MCP servers have separate authentication
- Token auto-refresh handled centrally

### MCP Servers
- **Basecamp:** Remote HTTP server via DocManager
- **SEMrush:** Disabled (using direct API via KeywordMaster)
- **Chrome DevTools:** Local stdio server via TechAuditor

### Shared State
All agents in the hierarchy share `session.state`:
- Can pass data between agents
- Coordinator can set context for specialists
- Specialists can return results via state

## Extensibility

### Adding a New Tool
1. Create function in `seo_agent/tools/*.py`
2. Import in appropriate agent file
3. Add to agent's `tools` list
4. Update agent `instruction` with usage guidelines

### Creating a New Agent
1. Create `seo_agent/agents/new_agent.py`
2. Define Agent with name, description, tools, instruction
3. Import in `seo_agent/agents/__init__.py`
4. Add to coordinator's `sub_agents` list
5. Update coordinator's routing logic
6. Update exports in `seo_agent/__init__.py`

### Modifying Routing Logic
Edit `seo_agent/agents/coordinator.py`:
- Update `instruction` with new routing rules
- Add examples for when to transfer
- Ensure agent descriptions are clear

## Performance Considerations

### Context Management
- Each agent has focused tool set (3-19 vs 61)
- Reduces LLM context size
- Improves tool selection accuracy

### Potential Optimizations
- Parallel agent execution for independent tasks
- Caching of agent responses
- Tool result memoization
- Lazy loading of MCP connections

## Backward Compatibility

### Import Compatibility
```python
# All of these work:
from seo_agent import seo_agent        # Main coordinator
from seo_agent import root_agent       # Alias for seo_agent
from seo_agent import seo_coordinator  # Explicit coordinator

# New in v2.0:
from seo_agent import analytics_agent
from seo_agent import keyword_agent
from seo_agent import technical_agent
from seo_agent import documentation_agent
```

### Usage Compatibility
```python
# Old code (v1.0) - STILL WORKS
response = seo_agent.run("any query")

# New code (v2.0) - Direct agent access
response = analytics_agent.run("GA4 metrics query")
```

---

**Architecture Version:** 2.0.0
**Last Updated:** 2025-11-17
**Status:** Production Ready
