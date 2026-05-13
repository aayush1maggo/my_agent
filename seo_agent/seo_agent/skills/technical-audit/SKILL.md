---
name: technical-audit
description: >
  Perform a structured technical SEO audit for a website. Covers sitemap health,
  robots.txt crawl rules, on-page tag audits, broken link detection, structured
  data validation, redirect chains, and Core Web Vitals indicators. Delivers a
  prioritised issue list with specific fixes.
---

## Technical Audit Workflow

Read `references/priority-matrix.md` to correctly classify issue severity.
Use `references/audit-checklist.md` as your running checklist — work through it top to bottom.

**Step 1 — Sitemap audit**
- Call `analyze_sitemap` with the sitemap URL (e.g. `https://example.com/sitemap.xml`)
  - Checks: 404 URLs, HTTP vs HTTPS mix, duplicate URLs, Google compliance
- Call `get_sitemap_summary` for a high-level count summary
- Flag any 404s in the sitemap as Critical priority

**Step 2 — robots.txt audit**
- Call `analyze_robots_txt` with the site root URL
- Call `get_robots_txt_summary` for rule counts
- Check: is anything important blocked? Are CSS/JS disallowed? Is the sitemap declared?
- Flag any `Disallow: /` under `User-agent: *` as Critical

**Step 3 — On-page tag audit (sample pages)**
- Call `extract_batch_page_metadata` on the homepage + 5–10 key pages
  - Check: missing title tags, duplicate titles, missing meta descriptions, missing H1, canonical mismatches
- Call `fetch_page_content` on each page for deeper headings and schema check

**Step 4 — Structured data audit**
- Call `extract_structured_data` on key page types (home, service, blog, contact)
  - Check: schema type present, required fields populated, no missing @type
- Flag missing schema where it would help: LocalBusiness, Service, Article, FAQPage

**Step 5 — Broken link detection**
- For sites < 200 pages: call `find_broken_links` on the domain root
- For sites > 200 pages: call `run_screaming_frog_404_report` (requires SF CLI)
- Also call `analyze_sitemap` to cross-check: sitemap URLs returning 404 are highest priority

**Step 6 — Redirect and status checks**
- Call `batch_check_page_status` on the top 20 pages (from sitemap or known URLs)
  - Check: redirect chains (more than 1 hop is wasteful), 301 vs 302, X-Robots-Tag headers
- Call `check_page_status` on the homepage specifically for latency benchmarking

**Step 7 — Internal linking spot-check**
- Call `extract_all_links` on the homepage and 2–3 key service/category pages
  - Check: are important pages linked from the homepage? Any nofollow on internal links?
  - Check: are pages deep in the crawl (3+ clicks from home)?

**Step 8 — Deliver the audit report**
- Follow `references/audit-checklist.md` for the output structure
- Use the severity levels from `references/priority-matrix.md`
- Group issues: Critical → High → Medium → Low
- For each issue: what it is, where it was found, exact fix required, expected impact
