# Technical SEO Issue Priority Matrix

## Severity Levels

### CRITICAL — Fix within 48 hours
Issues that directly block search engines from crawling or indexing the site.

| Issue | Example | Impact |
|---|---|---|
| Site blocked by robots.txt | `Disallow: /` under `User-agent: *` | Entire site deindexed |
| Sitemap URLs returning 404 | Key pages in sitemap but not live | Pages not submitted to Google |
| Homepage returning non-200 status | 500 server error on homepage | Site appears down to Googlebot |
| Redirect loop | Page A → B → A | Crawl budget wasted, page not indexed |
| Missing canonical on paginated pages | /page/2 canonical points to itself | Duplicate content indexed |

### HIGH — Fix within 2 weeks
Issues that waste crawl budget or cause significant ranking signal dilution.

| Issue | Example | Impact |
|---|---|---|
| 404 pages with internal links pointing to them | Dead service page still linked from nav | Link equity wasted |
| Long redirect chains (3+ hops) | /old → /redirect1 → /redirect2 → /new | PageRank dilution |
| Duplicate title tags | 10+ pages share same title | Ranking confusion |
| Missing H1 on key pages | Service pages have no H1 | On-page signal lost |
| Mixed HTTP/HTTPS in sitemap | Some URLs use http:// | Security warnings, crawl split |
| Pages blocked in robots.txt but in sitemap | Contradiction confuses Googlebot | Mixed signals |

### MEDIUM — Fix within 1 month
Issues that reduce SEO performance but don't critically block crawling.

| Issue | Example | Impact |
|---|---|---|
| Missing meta descriptions on key pages | Top-traffic pages lack meta desc | Lower CTR in SERPs |
| No schema markup on service/product pages | Service page has no LocalBusiness schema | Missed rich result opportunity |
| Thin content pages indexed | Pages with < 200 words | Quality dilution |
| Images missing alt text | Hero images have no alt | Accessibility + image search loss |
| Excessive internal nofollow links | Navigation links marked nofollow | Link equity not flowing |
| Canonical pointing to wrong URL | Self-referential canonicals wrong | Duplicate content risk |

### LOW — Add to backlog
Issues that are best practice improvements with minor direct ranking impact.

| Issue | Example | Impact |
|---|---|---|
| Title tags slightly over 60 chars | Titles truncated in SERPs | Aesthetic, minor CTR |
| Missing Open Graph tags | Social shares show no preview | Social traffic quality |
| No sitemap index file | Only one sitemap, no index | Minor crawling efficiency |
| Crawl-delay set in robots.txt | `Crawl-delay: 10` | Slows Googlebot (for Google, adjust in GSC) |
| Pages deep in crawl (4+ clicks) | Important pages buried | Discovery time increases |

## Decision Rules

1. **Anything blocking indexing = Critical**, regardless of page importance
2. **Broken links to pages in top 20 GA4 pages = High** (not medium) — elevated because of traffic impact
3. **Schema missing on a page that already ranks positions 4–10 = High** — schema could push it to featured snippet
4. **Duplicate content issues = High if affecting more than 10 pages**, Medium if isolated
