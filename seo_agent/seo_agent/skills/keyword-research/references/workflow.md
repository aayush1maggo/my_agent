# Keyword Research — Tool Usage Reference

## Tool Selection Guide

### When to use each tool

**`get_keyword_overview(keyword, database)`**
- Use for: single keyword analysis — volume, KD, CPC, trend, competition
- Always pass `include_trends=True`
- Database examples: "au" (Australia), "us" (USA), "gb" (UK)

**`get_keyword_overview_batch(keywords, database)`**
- Use for: 6+ keywords at once — same data as overview but efficient
- Preferred over calling get_keyword_overview in a loop

**`get_related_keywords(keyword, database, limit)`**
- Use for: finding semantically related keywords and LSI terms
- Limit to 20–30 to avoid noise; filter by volume > 50

**`get_broad_match_keywords(keyword, database, limit)`**
- Use for: long-tail variations that include the seed keyword phrase
- Good for finding location + service combinations (e.g. "emergency plumber south yarra")

**`get_question_keywords(keyword, database, limit)`**
- Use for: who/what/where/when/why/how queries
- These map directly to FAQ sections and blog post titles

**`get_keyword_organic_results(keyword, database)`**
- Use for: seeing which URLs rank and their estimated traffic
- Reveals if a SERP is dominated by directories, Reddit, YouTube (harder to beat)

**`get_keyword_ranking(keyword, target_domain, location, gl)`**
- Use for: checking a single keyword's live position for a domain
- More accurate than SEMrush for real-time positions

**`batch_keyword_rankings(keywords, target_domain, location, gl)`**
- Use for: checking 5+ keywords at once for a domain
- Returns ranking coverage summary — use to identify quick wins

**`analyze_serp_features(keyword, location, gl)`**
- Use for: understanding what SERP features appear for a keyword
- Use on the top 5 priority keywords to spot featured snippet opportunities

**`compare_rankings(keywords, domains, location, gl)`**
- Use for: head-to-head comparison of 2–4 competitor domains
- Reveals the ranking gap and which competitor owns which keywords

**`get_client_keyword_targets(client_name_or_domain)`**
- Use for: retrieving the pre-set target keywords for an existing client
- Always call this if the user says "use our target keywords" or references a known client

**`get_backlinks_overview(domain)`**
- Use for: understanding why a competitor ranks well (link authority)
- Call on the top 1–2 ranking competitors for hard keywords

## Common Research Patterns

### Pattern A: New client — full research from scratch
1. `get_client_keyword_targets` (check if they exist)
2. `get_keyword_overview_batch` (5 seed keywords)
3. `get_related_keywords` + `get_broad_match_keywords` (top seed)
4. `get_question_keywords` (top seed)
5. `batch_keyword_rankings` (all expanded keywords vs client domain)
6. `analyze_serp_features` (top 5 targets)

### Pattern B: Existing client — monthly update
1. `get_client_keyword_targets` (get their tracked keywords)
2. `batch_keyword_rankings` (check current positions)
3. `get_keyword_overview_batch` (refresh volume/KD data)
4. Compare to previous month — report movers and losers

### Pattern C: Competitor analysis request
1. `compare_rankings` (client + 2–3 competitors, top keywords)
2. `get_backlinks_overview` (top competitor)
3. `get_backlink_competitors` (find all competitors by backlink overlap)
4. Report the ranking gap and recommended actions
