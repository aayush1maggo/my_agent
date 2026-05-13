# Monthly Report — Slides Layout

Slide-by-slide guide for the Google Slides presentation version of the monthly report.
Use add_slide + add_title_to_slide + add_bullet_points_to_slide for each slide.

---

## Slide 1: Cover Slide
- Layout: TITLE
- Title: "[Client Name] SEO Report"
- Subtitle: "[Month YYYY] | Prepared by [Agency Name]"

## Slide 2: Highlights (Executive Summary)
- Layout: TITLE_AND_BODY
- Title: "This Month's Highlights"
- Bullets (4–5 max):
  - Organic traffic: [+X% / -X%] vs last month
  - Top win: [one sentence]
  - Key concern: [one sentence]
  - Focus for next month: [one sentence]

## Slide 3: Traffic Overview (GA4)
- Layout: TITLE_AND_BODY
- Title: "Traffic Performance — [Month]"
- Use add_table_to_slide for metrics:
  - Columns: Metric | This Month | Last Month | Change
  - Rows: Organic Sessions, Users, Engagement Rate, Conversions
- Add brief 1-line callout using add_text_to_slide below the table

## Slide 4: Search Visibility (Search Console)
- Layout: TITLE_AND_BODY
- Title: "Search Console — [Month]"
- Table: Metric | This Month | Last Month | Change
  - Rows: Clicks, Impressions, Avg CTR, Avg Position
- Bullet list: Top 3 queries by clicks this month

## Slide 5: Top Pages
- Layout: TITLE_AND_BODY
- Title: "Top Pages by Organic Traffic"
- Table: Page | Sessions | vs Last Month
  - Top 5 organic pages

## Slide 6: Work Completed
- Layout: TITLE_AND_BODY
- Title: "Work Completed This Month"
- Bullets grouped by:
  - On Page / Technical (2–4 items)
  - Off Page (1–3 items)
  - Local SEO (if applicable)

## Slide 7: Keyword Rankings
- Layout: TITLE_AND_BODY
- Title: "Keyword Rankings Update"
- Table: Keyword | Previous | Current | Change
  - Top 8–10 tracked keywords
  - Use ↑ ↓ → symbols for change column

## Slide 8: Opportunities
- Layout: TITLE_AND_BODY
- Title: "Key Opportunities"
- Bullets (3–4 max):
  - Each bullet: [opportunity] — [expected impact]
  - Focus on quick wins and high-ROI actions

## Slide 9: Next Steps
- Layout: TITLE_AND_BODY
- Title: "Next Month's Focus"
- Bullets (3–5 items):
  - [Action] — [Owner] — [Timing]

## Slide 10: Thank You / Contact
- Layout: TITLE
- Title: "Thank You"
- Subtitle: "[Agency contact details or website]"

---

## Positioning Notes (for add_text_to_slide / add_table_to_slide)
- Table starts: x=50, y=130, width=610, height=250 (points)
- Callout text box: x=50, y=395, width=610, height=60
- Bullet list body: x=50, y=120, width=610, height=320
- All measurements in points (internally converted to EMU by the API)
