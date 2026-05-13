# Analytics Metrics Interpretation Guide

## GA4 Core Metrics

| Metric | What it means | Good/Bad signal |
|---|---|---|
| **Sessions** | Total visits (resets on 30-min inactivity) | Baseline traffic volume |
| **Total Users** | Unique users (by device/browser) | Audience size |
| **Engaged Sessions** | Sessions with 10s+ activity, 2+ pages, or conversion | Quality indicator |
| **Engagement Rate** | Engaged sessions / total sessions | > 50% = healthy; < 40% = investigate |
| **Bounce Rate** | 1 - engagement rate (GA4 definition) | < 60% is acceptable for most sites |
| **Avg Engagement Time** | Time spent in engaged sessions | > 1:30 min = strong for content; > 0:45 for service pages |
| **Conversions** | Goal completions (form, call, purchase) | Core business metric |
| **Conversion Rate** | Conversions / sessions | Benchmark against industry avg |

## Channel Breakdown (Session Default Channel Group)

| Channel | Expected share | Notes |
|---|---|---|
| Organic Search | 40–70% for established sites | Core SEO metric — track month-over-month |
| Direct | 10–25% | High direct = strong brand recognition |
| Referral | 5–15% | Indicates backlink/partnership traffic |
| Paid Search | Varies | Compare ROI vs Organic CPL |
| Social | 2–10% | Low for B2B; higher for B2C |
| Email | 2–8% | Owned channel — not SEO but important |
| Unassigned | < 5% | Investigate if high — tracking issue |

## Period-over-Period Change Thresholds

| Change | Interpretation |
|---|---|
| > +20% | Strong growth — investigate what drove it |
| +5% to +20% | Steady growth |
| -5% to +5% | Stable — acceptable fluctuation |
| -5% to -20% | Declining — needs explanation and action |
| < -20% | Significant drop — urgent investigation |

## Search Console Metrics

| Metric | Definition | Action triggers |
|---|---|---|
| **Clicks** | Users who clicked through to site | Falling clicks = ranking drop or CTR problem |
| **Impressions** | Times site appeared in results | Rising impressions + flat clicks = CTR issue |
| **CTR** | Clicks / Impressions | < 2% = title/meta optimisation needed |
| **Avg Position** | Average ranking position for queries | < 10 = page 1; 11–20 = close to page 1 |

## Opportunity Identification Rules

**High impressions, low CTR (< 2%)**
- Cause: title tag not compelling, meta description missing/weak
- Fix: rewrite title (include primary keyword + value prop), add strong meta description

**Positions 11–20 (page 2)**
- These are your highest-ROI optimisation targets
- Fix: improve content depth, add internal links, optimise for featured snippet

**Good position (< 15) + low clicks**
- Cause: result not showing as rich result, no featured snippet, low brand recognition
- Fix: add schema markup (FAQPage, HowTo), optimise meta title for CTR

**Rising impressions, falling clicks**
- Cause: ranking slipped from page 1 to page 2, or a competitor took featured snippet
- Fix: check ranking in Search Console performance by page, identify affected queries
