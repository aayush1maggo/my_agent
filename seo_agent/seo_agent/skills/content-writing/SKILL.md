---
name: content-writing
description: >
  Research and write SEO-optimised content for a target keyword or topic.
  Covers competitor SERP analysis, content gap identification, content brief
  creation, and full draft writing following E-E-A-T and Google's helpful
  content guidelines. Uses live page data from competitor URLs.
---

## Content Writing Workflow

Read `references/seo-content-framework.md` before writing any content.
Read `references/tone-guidelines.md` to match the writing style.

**Step 1 — Define the target**
- Confirm the primary keyword (the exact phrase the page should rank for)
- Confirm secondary / supporting keywords (2–5 related phrases)
- Confirm the target URL (new page or existing page to rewrite)
- Confirm content type: blog post, service page, landing page, product page, FAQ page

**Step 2 — SERP & competitor analysis**
- Call `analyze_serp_features` on the primary keyword
  - Note: featured snippet present? PAA questions? Top competing domains?
- Call `get_keyword_ranking` to see current client position for this keyword
- Call `fetch_page_content` on the top 3 ranking competitor URLs
  - Extract: H1, H2s, H3s, word count, schema types, content structure
  - Note the average word count of the top 3 — your draft should match or exceed it
- Call `get_keyword_organic_results` to see which specific URLs rank top 10

**Step 3 — FAQ & question mining**
- Call `extract_page_faqs` on the top 2 competitor URLs to capture their Q&A content
- Call `get_question_keywords` on the primary keyword to find all question variants
- These questions become: H2/H3 headings, FAQ schema, or People Also Ask targets

**Step 4 — On-page alignment check (if rewriting existing content)**
- Call `fetch_page_content` on the client's current page for the target keyword
- Call `search_page_text` to confirm whether the primary keyword appears in headings
- Identify gaps: missing keywords, thin sections, no FAQ, no schema

**Step 5 — Create the content brief**
- Follow `references/content-brief-template.md` exactly
- Define: recommended title tag, meta description, H1, H2 structure, target word count,
  internal links to include, CTA, schema type to add

**Step 6 — Write the draft**
- Follow the structure and rules in `references/seo-content-framework.md`
- Apply tone from `references/tone-guidelines.md`
- Primary keyword: in title tag, H1, first 100 words, at least 2–3 more times naturally
- Secondary keywords: in H2s and body paragraphs naturally
- Include an FAQ section using the top 5 questions from Step 3
- End with a clear CTA matching the page's conversion goal
- Add a recommended schema type annotation at the end of the draft
