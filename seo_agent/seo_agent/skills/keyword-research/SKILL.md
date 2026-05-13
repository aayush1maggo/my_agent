---
name: keyword-research
description: >
  Perform structured SEO keyword research for a client domain or topic.
  Covers seed keyword analysis, difficulty scoring, long-tail expansion,
  question keywords, SERP feature analysis, and competitor benchmarking.
  Produces a prioritised keyword list grouped by ranking opportunity tier.
---

## Keyword Research Workflow

Read `references/metrics-guide.md` first to understand how to interpret KD, volume, and CPC scores.

**Step 1 — Clarify inputs**
- Confirm the client domain (e.g. `example.com`, no protocol)
- Confirm the topic, product, or service to research
- Confirm the target location and country code (e.g. location="Melbourne, Victoria, Australia", gl="au")
- If the user says "use our target keywords", call `get_client_keyword_targets` first

**Step 2 — Seed keyword analysis**
- Call `get_keyword_overview` for 3–5 core seed keywords
- Note: always request `include_trends=True` to see seasonality
- Call `get_keyword_overview_batch` if there are 6+ seeds (one API call is more efficient)
- Record: search volume, KD (keyword difficulty), CPC, competition, trend direction

**Step 3 — Expand the keyword list**
- Call `get_related_keywords` on the highest-volume seed keyword
- Call `get_broad_match_keywords` on the primary seed keyword for long-tail variations
- Call `get_question_keywords` on the primary topic to find "how/what/why/when/who" queries
- Add any expansion keywords with volume > 50/month to your working list

**Step 4 — Check current rankings**
- Call `batch_keyword_rankings` with your expanded list and the client domain
- Note which keywords the site already ranks for (positions 1–10, 11–30, 31–100)
- Keywords in positions 11–30 are "quick wins" — small optimisation can move them to page 1

**Step 5 — SERP feature analysis (top 5 targets)**
- Call `analyze_serp_features` on the 5 highest-priority target keywords
- Identify: featured snippet opportunities, People Also Ask questions, knowledge graph presence
- Use PAA questions as headings/FAQ content in the recommended pages

**Step 6 — Competitor benchmarking (optional)**
- Call `compare_rankings` with 2–3 competitor domains to see the gap
- Call `get_backlinks_overview` on a competitor if their rankings seem unusually strong

**Step 7 — Deliver output**
- Follow the template in `references/output-template.md`
- Group keywords into three tiers as defined in `references/metrics-guide.md`
- Include a "Quick Wins" section at the top for any position 11–30 keywords

**Step 8 — Handoff for document creation (if requested)**
- If the user asked for a Google Doc or Google Sheet, do NOT attempt to create it yourself.
- Instead, after delivering the Step 7 output, end your response with this exact block:

  ---
  HANDOFF TO DOC MANAGER
  The keyword research above is complete. To create the Google Doc/Sheet,
  ask Neo: "Take the keyword research above and put it into a Google Doc"
  ---

- This tells the coordinator to route to doc_manager with the research already in context.
