# Technical SEO Audit Checklist & Output Template

Work through this checklist top-to-bottom. Mark each item as PASS / FAIL / N/A.
At the end, compile all FAILs into the Prioritised Issues section.

---

## Technical SEO Audit — [Domain] — [Date]

**Audited by:** Neo SEO Agent — TechAuditor
**Scope:** [e.g. Full site / Homepage only / Key service pages]

---

### Section 1: Sitemap

- [ ] Sitemap found at `/sitemap.xml` or declared in robots.txt
- [ ] Sitemap returns 200 status
- [ ] No 404 URLs in sitemap
- [ ] All URLs use HTTPS (no HTTP entries)
- [ ] No duplicate URLs in sitemap
- [ ] URL count within Google's 50,000 limit
- [ ] Sitemap index used for large sites (> 50,000 URLs)
- [ ] `<lastmod>` dates are accurate (not all the same static date)

**Sitemap stats:** [Total URLs | 404 count | HTTP URLs | Duplicates]

---

### Section 2: robots.txt

- [ ] robots.txt returns 200 status
- [ ] No `Disallow: /` under `User-agent: *` or major bots
- [ ] CSS and JS files are NOT blocked
- [ ] Sitemap is declared with absolute URL
- [ ] No conflicting Allow/Disallow rules
- [ ] Crawl-delay not used for Google (use GSC instead)

**Key rules found:** [List significant Disallow patterns]

---

### Section 3: On-Page Tags (sampled pages)

- [ ] All pages have unique title tags
- [ ] All title tags are 50–60 characters
- [ ] All key pages have meta descriptions
- [ ] All meta descriptions are 145–160 characters
- [ ] Each page has exactly one H1
- [ ] H1 is not the same as the title tag (ideally varied but consistent)
- [ ] Canonical tags present and pointing to correct URL
- [ ] No `noindex` on pages that should be indexed
- [ ] No `nofollow` on internal navigation links

**Pages checked:** [list URLs]

---

### Section 4: Structured Data

- [ ] Homepage has LocalBusiness or Organization schema
- [ ] Service pages have Service schema
- [ ] Blog posts have Article or BlogPosting schema
- [ ] FAQ sections have FAQPage schema
- [ ] No schema validation errors (required fields missing)

**Schema types found:** [list per page type]

---

### Section 5: Status & Redirects

- [ ] Homepage returns 200
- [ ] No redirect chains longer than 1 hop
- [ ] All redirects use 301 (not 302) unless intentionally temporary
- [ ] No redirect loops detected
- [ ] HTTP homepage redirects to HTTPS correctly
- [ ] www/non-www redirect is consistent (pick one canonical version)

**Redirect issues:** [list any chains or loops]

---

### Section 6: Broken Links

- [ ] No internal links to 404 pages
- [ ] No links in sitemap to 404 pages
- [ ] 404 page returns correct 404 HTTP status (not soft 404)
- [ ] Custom 404 page exists (not server default)

**Broken links found:** [count and list top offenders]

---

### Section 7: Internal Linking

- [ ] Key pages linked from homepage
- [ ] Important pages reachable within 3 clicks from homepage
- [ ] No orphan pages (pages with 0 internal links)
- [ ] Internal links use descriptive anchor text (not "click here")
- [ ] No unnecessary nofollow on internal links

---

## Prioritised Issues

### CRITICAL (Fix within 48 hours)
| # | Issue | Page(s) Affected | Fix Required |
|---|---|---|---|

### HIGH (Fix within 2 weeks)
| # | Issue | Page(s) Affected | Fix Required |
|---|---|---|---|

### MEDIUM (Fix within 1 month)
| # | Issue | Page(s) Affected | Fix Required |
|---|---|---|---|

### LOW (Backlog)
| # | Issue | Page(s) Affected | Fix Required |
|---|---|---|---|

---

## Summary Scorecard

| Category | Status | Issues Found |
|---|---|---|
| Sitemap | PASS / FAIL | |
| robots.txt | PASS / FAIL | |
| On-Page Tags | PASS / FAIL | |
| Structured Data | PASS / FAIL | |
| Status & Redirects | PASS / FAIL | |
| Broken Links | PASS / FAIL | |
| Internal Linking | PASS / FAIL | |

**Overall technical health:** [GOOD / NEEDS WORK / CRITICAL ISSUES]
