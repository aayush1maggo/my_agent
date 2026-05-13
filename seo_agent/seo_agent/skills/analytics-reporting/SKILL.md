---
name: analytics-reporting
description: >
  Run a structured SEO performance analysis using GA4 and Search Console data.
  Covers traffic trends, channel breakdown, top pages, search query performance,
  CTR opportunities, and period-over-period comparison. Delivers an actionable
  insight summary suitable for client reporting.
---

## Analytics Reporting Workflow

Read `references/metrics-guide.md` to understand how to interpret each metric.
Use `references/report-structure.md` for the output format.

**Step 1 — Establish the date range**
- Call `get_current_datetime` to confirm today's date
- Default reporting period: last 28 days vs previous 28 days
- If the user specifies "last month", "this quarter", etc., calculate exact YYYY-MM-DD dates
- GA4 accepts relative dates: `30daysAgo`, `yesterday`, `today`

**Step 2 — GA4 traffic overview**
- Call `get_ga4_metrics` with dimensions=['sessionDefaultChannelGroup'] for channel breakdown
  - Metrics: sessions, totalUsers, engagedSessions, engagementRate, conversions
- Call `analyze_ga4_trends` to identify period-over-period changes and any traffic anomalies
- Call `get_ga4_traffic_sources` for source/medium breakdown

**Step 3 — Top page performance**
- Call `get_ga4_page_performance` to get top 20 pages by sessions
- Note: which pages gained traffic, which lost, any new entrants in top 10

**Step 4 — Search Console query analysis**
- Call `get_search_console_queries` with the same date range
  - Dimensions: query; metrics: clicks, impressions, ctr, position
- Call `get_search_console_pages` for page-level search performance
- Call `analyze_search_opportunities` to surface:
  - High impressions + low CTR (title/meta description fix needed)
  - Positions 11–20 (close to page 1 — content optimisation opportunity)
  - Good position + low clicks (featured snippet or rich result opportunity)

**Step 5 — Period comparison**
- Call `compare_periods` for the current vs previous period on key metrics
- Flag: any metric that changed by more than 10% needs an explanation

**Step 6 — Keyword-to-page mapping (optional)**
- Call `get_keyword_landing_pages` to see which queries drive which pages
- Use this to identify pages that rank for multiple keywords (consolidation opportunity)

**Step 7 — Deliver the report**
- Follow `references/report-structure.md` for section order and format
- Every metric change must be explained — never report a number without a "why"
- End with 3–5 prioritised recommendations tied to the data
