"""Keyword research and mapping workflow agent using SequentialAgent."""
from copy import deepcopy

from google.adk.agents.llm_agent import Agent as LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent

from .keyword_agent import keyword_agent
from .documentation_agent import documentation_agent


def _clone_agent(agent: LlmAgent, new_name: str, extra_instruction: str) -> LlmAgent:
    """Clone an existing agent while appending workflow-specific instructions."""
    data = deepcopy(agent.model_dump())
    data["name"] = new_name
    base_instruction = data.get("instruction", "")
    data["instruction"] = (
        f"{base_instruction}\n\nAdditional instructions for keyword_mapping_workflow:\n{extra_instruction}"
    )
    return LlmAgent(**data)


keyword_research_stage_agent = _clone_agent(
    keyword_agent,
    "keyword_mapping_researcher",
    (
        "You are step 1 of the keyword_mapping_workflow. Start by restating the website description, core services, "
        "and target locations the user provides. If any of these are missing, ask clarifying questions before moving on. "
        "Use SEMrush keyword reports, Serper ranking checks, and on-page extraction tools to build a research blueprint "
        "that DocManager can put into Google Sheets.\n\n"
        "Deliverables for DocManager:\n"
        "- A structured outline of the spreadsheet title and any naming context (brand, region, etc.).\n"
        "- For the `Keyword Research` tab, prepare grouped findings per service/location pairing with metrics "
        "(primary keyword, supporting keywords, search intent, volume, difficulty, CPC, priority score, FAQ ideas). "
        "Flag both commercial terms and long-tail/FAQ opportunities separately.\n"
        "- For the `Keyword Mapping` tab, map each recommended page (existing or net-new) to a primary keyword, "
        "supporting cluster, recommended URL slug, and content angle. Include draft copy for Optimized Meta Title (<=60 "
        "characters), Optimized Meta Description (<=155 characters), H1, sensible H2 theme groupings, and bullet H3 "
        "ideas. Provide concise rationale for each mapping.\n"
        "- Output the research in clearly labeled sections so DocManager can translate it directly into sheets without "
        "additional reasoning.\n"
        "Always cite which tools and data sources informed each recommendation."
    ),
)

keyword_mapping_doc_agent = _clone_agent(
    documentation_agent,
    "keyword_mapping_doc_manager",
    (
        "You are step 2 of the keyword_mapping_workflow. Use the structured research handoff from "
        "KeywordMaster to create or update a Google Sheet. Unless the user specifies an existing "
        "spreadsheet ID, create a new sheet titled `Keyword Research & Mapping - <Brand/Website> (Date)` and confirm "
        "the link.\n\n"
        "Sheet requirements:\n"
        "1. Tab `Keyword Research` with columns: Service, Location, Primary Keyword, Supporting Keywords, Search Intent, "
        "Search Volume, Difficulty, CPC, Priority, FAQ / Long-Tail Ideas, Notes.\n"
        "2. Tab `Keyword Mapping` with columns: Page / URL, Primary Keyword, Supporting Keywords, Optimized Meta Title, "
        "Optimized Meta Description, H1 Tag, H2 Tags, H3 Tags, Notes.\n"
        "Populate both tabs using the data from step 1, keeping formatting consistent (one keyword per row, supporting "
        "keywords comma-separated). Include any rationale or TODOs in the Notes column.\n"
        "If multiple services or locations exist, group rows logically and add frozen header rows. Confirm completion by "
        "summarizing the sheet structure and sharing the spreadsheet URL."
    ),
)


keyword_mapping_workflow_agent = SequentialAgent(
    name="keyword_mapping_workflow",
    description=(
        "Two-step keyword research and mapping workflow. Step 1 (KeywordMaster clone) researches service/location "
        "keywords, FAQs, and metadata guidance. Step 2 (DocManager clone) builds a Google Sheets document with "
        "Keyword Research and Keyword Mapping tabs populated from the research."
    ),
    sub_agents=[
        keyword_research_stage_agent,
        keyword_mapping_doc_agent,
    ],
)
