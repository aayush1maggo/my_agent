---
name: monthly-report
description: >
  Produce a structured monthly SEO summary directly in the conversation.
  Pulls all Basecamp tasks touched during the reporting month (completed and
  in-progress), groups them by category, and combines Basecamp-planned next
  steps with current SEO trends relevant to the client. No Google Docs,
  Slides, or analytics tool data required.
---

## Monthly Report Workflow

**Do NOT create any Google Doc or Google Slides presentation.**
**Do NOT query GA4, Search Console, SEMrush, or any analytics tool.**
Output the entire summary as formatted text directly in the conversation.

---

**Step 1 — Confirm reporting details**
Ask the user (or confirm from context):
- Client name
- Reporting month and year (e.g. February 2026)
- Client's industry/niche (needed for Step 3 SEO trends)

---

**Step 2 — Pull all Basecamp activity for the month**
- Call `get_basecamp_projects` to locate the client project
- Call `get_basecamp_todolists` to get all todolists
- Call `get_basecamp_todos` (without todolist_id) to retrieve ALL todos

Include todos that were:
- **Completed** during the reporting month
- **Created** during the reporting month (even if still open)
- **Commented on** during the reporting month

For each todo that is still open / not yet completed, append **(In progress)** after the task description line.

Group the todos into the following categories using your best judgement based on the task title and description:
- **On Page / Technical** — content updates, meta data, site structure, audits, blog work, CRO, Core Web Vitals, plugins
- **Off Page** — link building, guest posts, outreach, PR, citations
- **Local SEO** — GMB, local citations, local content, NAP, service area pages
- **Other** — anything that does not clearly fit the above

Write each item as a short plain-English sentence summarising what was done. Do not list raw Basecamp todo titles verbatim — rewrite them into readable sentences. Group related tasks into a single sentence where it makes sense.

---

**Step 3 — Research current SEO trends relevant to the client**
Using your knowledge and the client's industry/niche, identify 2–3 current SEO opportunities or best practices that are trending and directly applicable to this client. These supplement the Basecamp-planned items in Next Steps.

Examples of trend-based next steps:
- AI Overview / SGE optimisation for high-intent queries
- FAQ schema / People Also Ask targeting
- E-E-A-T signals (author bios, trust pages)
- Core Web Vitals / INP metric improvements
- Local pack optimisation strategies
- Topical authority and content clustering

Only include trends that are genuinely relevant to the client's niche and situation.

---

**Step 4 — Compile Next Steps**
Next Steps = combination of:
1. Tasks still **in progress** or **planned** from Basecamp (from Step 2)
2. Trend-based SEO opportunities from Step 3

Write each Next Step as:
`[Short Label] — [One sentence explaining the action and why it matters for this client]`

Maximum 6–8 next steps total. Prioritise by potential impact.

---

**Step 5 — Output the summary in this exact format**

```
------------------------

Please find the summary below


On Page / Technical


[bullet items — one per line, no dashes or symbols]


Off Page


[bullet items]


Local SEO


[bullet items, or omit section if nothing to report]


Next Steps

[Label] - [Action and why it matters.]
[Label] - [Action and why it matters.]
...
```

Rules for formatting:
- Use a blank line between each section heading and its content
- Use a blank line between each bullet item
- No Markdown bullet symbols (no `-`, `*`, `•`)
- No bold, no asterisks, no hashtags in the output
- Section headings on their own line
- Append **(In progress)** inline on lines for tasks not yet completed
- The opening line is always: `Please find the summary below`
- The separator `------------------------` appears once at the very top
