"""Guest post planning workflow agent using SequentialAgent."""
from copy import deepcopy

from google.adk.agents.llm_agent import Agent as LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent

from .keyword_agent import keyword_agent
from .analytics_agent import analytics_agent
from .documentation_agent import documentation_agent


def _clone_agent(agent: LlmAgent, new_name: str, extra_instruction: str) -> LlmAgent:
    """Clone an agent instance and append workflow-specific directions."""
    data = deepcopy(agent.model_dump())
    data["name"] = new_name
    base_instruction = data.get("instruction", "")
    data["instruction"] = (
        f"{base_instruction}\n\nAdditional instructions for guest_post_workflow:\n{extra_instruction}"
    )
    return LlmAgent(**data)


guest_post_keyword_agent = _clone_agent(
    keyword_agent,
    "guest_post_keyword_master",
    (
        "You are step 1 of the guest_post_workflow. Collect the client's name, website, and the requested number of "
        "guest posts (rows). Ask for missing information before continuing.\n\n"
        "Process:\n"
        "1. Call get_client_keyword_targets(client) to load the keyword list, default URL, and location metadata.\n"
        "2. Confirm you have at least 2 × requested guest posts keywords (two per row). Combine service intent + "
        "location variety so each row pairs two complementary keywords from the targeting list without duplication.\n"
        "3. For each keyword, capture the recommended location (from the targeting list). Use that value when calling "
        "get_keyword_ranking (single) or batch_keyword_rankings (batches) so rankings align with the user's geo target. "
        "Record the live result as `KW Ranking Before` (position number or 'Not found').\n"
        "4. Draft a guest post title (<=70 characters) that blends both keywords naturally. Each title should sound like "
        "a real publication pitch, highlight the core benefit, and avoid keyword lists. Explain why the angle fits the "
        "selected keywords.\n"
        "5. Propose two anchor texts per guest post that follow best practices:\n"
        "   - Anchor text 1: natural/brand-led partial match (e.g., brand + service)\n"
        "   - Anchor text 2: descriptive/supporting phrase with the second keyword (no spammy exact-match repetition)\n"
        "   Mention why each anchor text is safe (contextual, value-driven, avoids keyword stuffing).\n"
        "6. Output a structured plan for each row -> Guest Post #, keyword pair, suggested title, anchor text "
        "recommendations, keyword location, KW ranking before, and the target domain (from the keyword target list). "
        "Highlight any keywords missing ranking data so the next step can still map landing pages.\n"
        "Deliverables: Provide a JSON-like bullet list for each guest post row that includes the two keywords, anchors, "
        "location, title, rank_before, and notes. This feeds the Search Console + Sheets stages."
    ),
)


guest_post_search_console_agent = _clone_agent(
    analytics_agent,
    "guest_post_search_console",
    (
        "You are step 2 of the guest_post_workflow. Using the keyword pairings from step 1, map each keyword to its "
        "best-performing landing page via Search Console.\n\n"
        "Instructions:\n"
        "1. Confirm the site's canonical URL (provided in the keyword target list / prior step). If unclear, ask.\n"
        "2. Collect all keywords from the plan (deduplicate). Use get_keyword_landing_pages(site_url, keywords) with "
        "match_type='exact' to pull the last ~30 days of landing page data.\n"
        "3. For each keyword in the plan, select the landing page with the highest clicks; if no mapping exists, choose "
        "the closest match (contains) or note 'No data - publish guest post to introduce topic'.\n"
        "4. Provide a concise table mapping keyword -> landing page URL + performance metrics (clicks, impressions, "
        "position). Flag any missing URLs so DocManager can still populate the sheet with an action note.\n"
        "5. Pass the enriched data set forward, keyed by guest post row number, so the final step can combine anchor "
        "texts, rankings, and landing pages.\n"
        "If Search Console access fails, explain the issue and provide a fallback recommendation (e.g., use sitemap or "
        "manual mapping)."
    ),
)


guest_post_sheet_agent = _clone_agent(
    documentation_agent,
    "guest_post_doc_manager",
    (
        "You are step 3 of the guest_post_workflow. Turn the guest post plan + Search Console mappings into a Google "
        "Sheet. Unless the user provides an existing sheet ID, create a new spreadsheet named "
        "`Guest Post Plan - <Client Name> - <YYYY-MM-DD>`.\n\n"
        "Sheet requirements:\n"
        "- Columns (exact order + spelling): "
        "`Client`, `Guest Post Title`, `Anchor text 1`, `Target Keyword 1`, `KW Ranking Before`, `KW Ranking After`, "
        "`Target Landing Page`, `Anchor text 2`, `Target Keyword 2`, `KW Ranking Before`, `KW Ranking After`, "
        "`Target Landing Page`.\n"
        "- Each row represents one guest post opportunity containing two keywords.\n"
        "- Populate Guest Post Title + Anchor text / Target Keyword / KW Ranking Before from step 1. Use Search Console "
        "mappings from step 2 for the landing page columns. If Search Console lacked data, add a short note such as "
        "'No GSC data - create new topical hub' in the landing page cell.\n"
        "- Set `KW Ranking After` as blank for now; insert a placeholder like `\"\"` or leave empty (the team updates "
        "post-launch).\n"
        "- After populating all requested rows, include a short summary note referencing the sheet URL and how many guest "
        "posts were planned.\n"
        "Close your response with the new Google Sheet link and any follow-up guidance (e.g., queue outreach, monitor "
        "rankings after publishing)."
    ),
)


guest_post_workflow_agent = SequentialAgent(
    name="guest_post_workflow",
    description=(
        "Guest post planning workflow. Step 1 (KeywordMaster clone) selects keyword pairs, anchor texts, and captures "
        "live rankings by location. Step 2 (DataInsight clone) maps each keyword to its best landing page via Search "
        "Console. Step 3 (DocManager clone) builds a Google Sheet with the required guest post columns and rows."
    ),
    sub_agents=[
        guest_post_keyword_agent,
        guest_post_search_console_agent,
        guest_post_sheet_agent,
    ],
)
