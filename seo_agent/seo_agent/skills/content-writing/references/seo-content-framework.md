# SEO Content Framework

## Core Principles (Google's Helpful Content Guidelines)

1. **Write for people first** — content should answer the user's query completely
2. **Demonstrate E-E-A-T** — Experience, Expertise, Authoritativeness, Trustworthiness
3. **Avoid AI padding** — no filler phrases, no excessive repetition, no vague generalities
4. **One page, one primary intent** — don't mix informational and transactional goals on the same page

---

## Page Structure by Content Type

### Service Page
```
[Title Tag — 50–60 chars] Primary keyword + location + brand
[H1] Primary keyword — clear and descriptive
[Intro paragraph — 80–120 words] Problem + solution + CTA mention
[H2] What is [service]? OR Why choose [brand] for [service]?
  [Body — 150–200 words] Value proposition
[H2] Our [Service] Process
  [H3] Step 1... Step 2... Step 3...
[H2] [Service] in [Location] — Who We Help
  [Body + list]
[H2] Pricing / What's Included
[H2] Frequently Asked Questions
  [H3] Question 1... [Answer]
  [H3] Question 2... [Answer]
  (5–8 questions from question keyword research)
[H2] Get a Free Quote / Book Now [CTA Section]
```

### Blog Post / Article
```
[Title Tag] Primary keyword + hook (numbers, "how to", "guide")
[H1] Same as or variation of title tag
[Intro — 100–150 words] Hook + problem + what reader will learn
[H2] Section 1 — foundational concept
[H2] Section 2 — deeper detail
[H2] Section 3 — practical steps / how-to
[H2] Section 4 — examples or case study
[H2] Frequently Asked Questions
[Conclusion — 80–100 words] Summary + CTA (related service or next post)
```

### Landing Page (Lead Gen)
```
[H1] Primary keyword — outcome focused ("Get X in Y")
[Hero section — 60–80 words] One-liner benefit + trust signal + CTA button
[H2] The Problem We Solve
[H2] Our Solution / How It Works
[H2] Why [Brand] (social proof, credentials)
[H2] What's Included / Features
[H2] Results / Case Studies
[H2] FAQ
[Final CTA] Strong action-oriented button
```

---

## Keyword Placement Rules

| Location | Primary Keyword | Secondary Keywords |
|---|---|---|
| Title tag | Must include | Optional |
| H1 | Must include | Optional |
| First 100 words | Must include | 1–2 natural mentions |
| H2 headings | 1–2 headings | Distribute naturally |
| Body paragraphs | 2–4 more occurrences | Throughout |
| Meta description | Must include | Optional |
| Image alt text | 1 occurrence | 1 occurrence |
| URL slug | Must include (hyphenated) | N/A |

**Keyword density**: Aim for 1–2% — do NOT stuff. If it reads awkwardly, it's over-optimised.

---

## Word Count Benchmarks

| Page Type | Minimum | Target | Notes |
|---|---|---|---|
| Service page | 600 | 900–1,200 | Match top 3 competitors ± 20% |
| Blog post | 800 | 1,500–2,500 | Longer = more keyword coverage |
| Landing page | 400 | 600–900 | Conversions > length |
| FAQ page | 300 | 600–1,000 | Each answer: 40–100 words |

---

## Schema Markup Recommendations

| Page Type | Schema to Add |
|---|---|
| Service page | `LocalBusiness` + `Service` |
| Blog post | `Article` or `BlogPosting` |
| FAQ section | `FAQPage` |
| How-to post | `HowTo` |
| Review/case study | `Review` or `ItemReviewed` |
| Product page | `Product` + `Offer` |

Always recommend adding schema at the end of the draft with a note for the developer.

---

## Internal Linking Rules
- Each page should include 2–5 internal links to related content
- Anchor text should be descriptive (not "click here")
- Link to: parent service page (from blog), related services, location pages, contact/quote page
- Never link to the page itself (self-referential links have no value)

---

## Featured Snippet Optimisation
If `analyze_serp_features` shows a featured snippet exists:
- Add a clear definition or answer in the first 100 words (40–60 words, one paragraph)
- Format it as a direct answer starting with: "A [term] is..." or "[Term] means..."
- Use a numbered list or table if the snippet is currently a list/table format

---

## Content Quality Checklist (before finalising)
- [ ] Primary keyword in title, H1, first 100 words
- [ ] Meta description written (under 160 chars, includes primary keyword, has CTA)
- [ ] All H2s are descriptive and contain secondary keywords where natural
- [ ] FAQ section with 5+ questions from question keyword research
- [ ] No paragraph longer than 5 lines
- [ ] Active voice used throughout
- [ ] At least 2–3 internal links with descriptive anchor text
- [ ] CTA present (contact, quote, book, learn more)
- [ ] Schema type annotated at end of draft
