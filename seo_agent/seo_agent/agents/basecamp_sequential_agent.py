"""Basecamp month-end workflow agent using SequentialAgent."""
from copy import deepcopy

from google.adk.agents.llm_agent import Agent as LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent

from .documentation_agent import documentation_agent
from .keyword_agent import keyword_agent


def _clone_agent(agent: LlmAgent, new_name: str, extra_instruction: str) -> LlmAgent:
    """Create an independent clone of an agent with additional instructions."""
    data = deepcopy(agent.model_dump())
    data["name"] = new_name
    base_instruction = data.get("instruction", "")
    data["instruction"] = f"{base_instruction}\n\nAdditional instructions for basecamp_workflow:\n{extra_instruction}"
    return LlmAgent(**data)


basecamp_doc_agent = _clone_agent(
    documentation_agent,
    "basecamp_doc_manager",
    (
        "You are running step 1 of the basecamp_workflow. Ask for Basecamp project IDs and target month/year "
        "if not provided. Use generate_basecamp_structured_summary() to fetch todos/todolists/comments and group them "
        "under the headings from structure.txt (On Page/Technical, Off Page, Local SEO, Next Steps). Populate the first "
        "three sections with concise bullet points using the format `Title - one short sentence.` Do not include people "
        "names, owner labels, or long explanations. Leave the Next Steps list empty for now. Mention the reporting period "
        "and total tasks processed."
    ),
)

basecamp_keyword_agent = _clone_agent(
    keyword_agent,
    "basecamp_keyword_master",
    (
        "You are running step 2 of the basecamp_workflow. Review DocManager's structured summary (On Page/Technical, "
        "Off Page, Local SEO). Use search/keyword tools to research fresh SEO/CRO strategies tied to those themes. "
        "Fill the Next Steps section with 5-8 concise bullet points in the `Title - one short sentence.` format (mirror "
        "structure.txt). Focus on rationale and expected impact without naming people."
    ),
)


# Sequential workflow: clone DocManager handles Basecamp reporting, cloned KeywordMaster adds strategies.
basecamp_workflow_agent = SequentialAgent(
    name="basecamp_workflow",
    description=(
        "Basecamp month-end workflow. Step 1: DocManager clone pulls project todos/todolists/comments for the "
        "requested month and prepares the summary. Step 2: KeywordMaster clone researches fresh SEO/CRO strategies "
        "and adds prioritized next steps."
    ),
    sub_agents=[
        basecamp_doc_agent,
        basecamp_keyword_agent,
    ],
)
