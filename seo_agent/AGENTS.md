# Repository Guidelines

## Project Structure & Modules
- Core package lives in `seo_agent/` with agents in `seo_agent/agents/` and shared tools in `seo_agent/tools/`.
- Example scripts are in `examples/` and are safe places to prototype usage patterns.
- Tests live in `tests/` and follow `test_*.py` naming.
- High-level docs are in `README.md`, `ARCHITECTURE.md`, `MIGRATION_GUIDE.md`, and `CLAUDE.md`.

## Setup, Run & Test
- Create a virtualenv and install deps: `python -m venv venv && venv\Scripts\activate` (or `source venv/bin/activate`) then `pip install -r requirements.txt`.
- Run the interactive agent: `python run_agent.py`.
- Run all tests: `pytest` (or `python -m pytest tests -v`).
- Optional structure check: `python validate_structure.py`.

## Coding Style & Naming
- Use Python 3, PEP 8 style, and 4-space indentation.
- Prefer descriptive, domain-specific names (e.g., `analytics_agent`, `keyword_agent`, `*_tools.py`).
- New tools go in `seo_agent/tools/` and are imported into the appropriate agent; keep function names snake_case.
- Keep module-level docstrings and clear instructions for each agent and tool.

## Testing Guidelines
- Use `pytest` for all tests; place new tests in `tests/` with `test_<feature>.py`.
- Mirror patterns in `tests/test_multi_agent.py` for structure and assertions.
- For changes that touch agents or tools, add/extend tests that cover agent imports, tool counts, and basic behavior.
- Integration tests that require real API credentials should be isolated and clearly marked or skipped by default.

## Multi-Agent Capabilities

- The root agent is `seo_coordinator` (exported as `seo_agent` and `root_agent`) with name `neo_coordinator`.
- `seo_coordinator` has 6 specialist sub-agents:
  - `analytics_agent` (`data_insight`) – GA4, Search Console, traffic analysis, dashboards/reports.
  - `keyword_agent` (`keyword_master`) – keyword research, rankings, SERP features, competitive analysis.
  - `technical_agent` (`tech_auditor`) – Core Web Vitals, performance, sitemaps, technical audits.
  - `documentation_agent` (`doc_manager`) – Google Docs/Slides/Sheets reports and Basecamp projects.
  - `local_seo_agent` (`local_citation`) – local SEO, citation strategy, and directory listing guidance.
  - `cro_agent` (`conversion_optimizer`) – conversion rate optimization (CRO), funnels, experiments, and landing page UX.
- The coordinator only has 3 utility tools: `get_current_datetime`, `calculate_date_range`, and `get_time_period_comparison_dates`; all heavy lifting happens in specialists.
- Keep `tests/test_multi_agent.py` in sync with:
  - The number of `sub_agents` on `seo_coordinator`.
  - The tool counts and names for each specialist agent.

## Commits & Pull Requests
- Write clear, imperative commit messages (e.g., `Add GA4 trend analysis tools`) and group related changes together.
- Do not commit secrets (`seo_agent/.env`, `credentials.json`, `token.json`, `basecamp_token.json`, etc.).
- For PRs, include: purpose, summary of changes, affected modules, and how to reproduce or run tests.
- Update relevant docs (`ARCHITECTURE.md`, `MIGRATION_GUIDE.md`, `README.md`) when you change behavior, configuration, or agent responsibilities.

