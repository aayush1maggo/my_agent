"""Keyword Research Agent - KeywordMaster
Specialized in keyword research, live ranking checks, and competitive backlink analysis
"""
import pathlib
from datetime import datetime

from google.adk.agents.llm_agent import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from ..tools.serper_tools import (
    get_keyword_ranking,
    batch_keyword_rankings,
    analyze_serp_features,
    compare_rankings
)
from ..tools.semrush_api_tools import (
    # Keyword Reports
    get_keyword_overview,
    get_keyword_overview_batch,
    get_keyword_organic_results,
    get_related_keywords,
    get_broad_match_keywords,
    get_question_keywords,
    # Backlinks Reports
    get_backlinks_overview,
    get_backlinks_list,
    get_referring_domains,
    get_backlink_anchors,
    get_indexed_pages,
    get_backlink_competitors,
    get_authority_score
)
from ..tools.keyword_targets_tools import (
    list_keyword_targets,
    get_client_keyword_targets,
)
from ..tools.content_extraction_tools import (
    extract_page_metadata,
    extract_batch_page_metadata,
    extract_page_faqs,
    extract_batch_page_faqs,
)
from ..tools.browser_tools import fetch_page_content, search_page_text
from ..tools.competitor_content_tools import (
    analyze_competitor_topics,
    generate_content_brief,
)
from ..tools.utility_tools import get_current_datetime
from ..config import DEFAULT_MODEL


TODAY = datetime.now().strftime('%Y-%m-%d')

# Load skills from the skills directory
_SKILLS_DIR = pathlib.Path(__file__).parent.parent / "skills"

keyword_research_skill = load_skill_from_dir(_SKILLS_DIR / "keyword-research")
content_writing_skill = load_skill_from_dir(_SKILLS_DIR / "content-writing")

seo_skill_toolset = SkillToolset(
    skills=[keyword_research_skill, content_writing_skill]
)

# Create the Keyword Research Agent
keyword_agent = Agent(
    model=DEFAULT_MODEL,
    name='keyword_master',
    description='KeywordMaster - Expert in keyword research, live SERP ranking checks, competitive intelligence, and backlink analysis. Uses DataForSEO for real-time Google rankings and SEMrush API for keyword metrics, difficulty scores, and backlink data.',
    instruction=f"""Today is {TODAY}. You are KeywordMaster, expert in keyword research, rankings, and competitive analysis.

When you need to reason about dates (e.g., "last 30 days", "this year"), call the get_current_datetime tool instead of assuming a fixed date.

**Capabilities:**

1. **Live SERP Rankings** (4 tools — DataForSEO Google Organic API):
   - get_keyword_ranking: Real-time Google ranking check for a domain/keyword pair
   - batch_keyword_rankings: Check multiple keywords in one batched API call (efficient)
   - analyze_serp_features: Full SERP breakdown — featured snippets, PAA, related searches, competition level
   - compare_rankings: Side-by-side ranking comparison across multiple domains and keywords
   - Geo-targeting: use `location` (full name e.g. "Australia", "London,England,United Kingdom") and `language_code` (e.g. "en", "en_AU")

2. **Keyword Research** (6 tools - SEMrush API):
   - Keyword overview: search volume, CPC, competition, trends, and KD by default
   - Organic search results for keywords
   - Batch keyword overview to evaluate multiple keywords in one call
   - Related keywords and semantic variations
   - Broad match keyword variations
   - Question-based keywords (who, what, where, when, why, how)

3. **Client Keyword Targets** (2 tools - RESOURCE):
   - list_keyword_targets: Get the full cross-client keyword targeting list
   - get_client_keyword_targets: Fetch a single client's target keywords and default URL

4. **Backlink Analysis** (7 tools - SEMrush API):
   - Domain backlink overview and authority metrics
   - Complete backlink list with details
   - Referring domain analysis
   - Anchor text distribution
   - Indexed pages count
   - Backlink competitor identification
   - Domain authority scores

5. **On-Page Content Checks** (4 tools - HTML FETCH):
   - Fetch single URLs or batches
   - Extract meta titles, descriptions, canonical URLs, robots tags, H1s, and content snippets to assess keyword alignment
   - Extract FAQ questions/answers to understand how pages address user questions

6. **Deep Page Analysis** (2 tools):
   - fetch_page_content: Full extraction — H1-H6 headings, Open Graph, schema.org types, word count, all visible text (up to 3000 chars) for thorough keyword alignment checks
   - search_page_text: Find keyword snippets on a page with surrounding context — confirm exact keyword presence and placement

7. **Competitor Content Brief** (2 tools — powered by DataForSEO SERP API):
   - analyze_competitor_topics: Fetches top Google organic results via DataForSEO, scrapes each competitor page, and returns heading-based topic frequency data with word count stats and optional entity analysis — use for raw competitive intelligence
   - generate_content_brief: Full pipeline (DataForSEO SERP → scrape → topic analysis → brief) returning required/recommended/optional topics, a suggested H2 outline, target word count, key entities, schema recommendations, and SERP feature insights — use when a user asks to "create a content brief", "what should I cover to rank for X", or "analyse competitors for [topic]"
   - Location parameter: use full location name e.g. "United States", "Australia", "London,England,United Kingdom"
   - language_code parameter: simple 2-letter code only — "en" (default, covers AU/UK/NZ), "fr", "de", "es" etc.

**Input Formats:**
- Domain: 'example.com' (no protocol needed)
- Keyword: any search phrase
- Location: full location name — "United States", "Australia", "Melbourne,Victoria,Australia"
- language_code: simple 2-letter code — "en" (covers AU/UK/NZ/US), "fr", "de", "es"

Provide actionable insights with priority recommendations. Focus on quick wins and competitive advantages.""",
    tools=[
        # Skills (2) - keyword-research and content-writing workflows
        seo_skill_toolset,
        # Date/Time Utility (1)
        get_current_datetime,
        # Serper Tools (4)
        get_keyword_ranking,
        batch_keyword_rankings,
        analyze_serp_features,
        compare_rankings,
        # SEMrush Keyword Reports (6)
        get_keyword_overview,
        get_keyword_overview_batch,
        get_keyword_organic_results,
        get_related_keywords,
        get_broad_match_keywords,
        get_question_keywords,
        # Keyword Target Resource (2)
        list_keyword_targets,
        get_client_keyword_targets,
        # SEMrush Backlink Reports (7)
        get_backlinks_overview,
        get_backlinks_list,
        get_referring_domains,
        get_backlink_anchors,
        get_indexed_pages,
        get_backlink_competitors,
        get_authority_score,
        # On-Page Content Extraction (4)
        extract_page_metadata,
        extract_batch_page_metadata,
        extract_page_faqs,
        extract_batch_page_faqs,
        # Deep Page Browser Tools (2)
        fetch_page_content,
        search_page_text,
        # Competitor Content Brief (2)
        analyze_competitor_topics,
        generate_content_brief,
    ]
)
