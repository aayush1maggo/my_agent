---
name: citation-building
description: >
  Plan and guide a local SEO citation building campaign for a business.
  Covers NAP consistency, business profile preparation, directory prioritisation,
  step-by-step submission guidance, and verification tracking. Always operates
  with human-in-the-loop for logins, CAPTCHAs, and verification steps.
---

## Citation Building Workflow

Read `references/nap-guidelines.md` for NAP formatting rules.
Read `references/directory-tiers.md` for directory priority rankings.

**IMPORTANT: Human-in-the-Loop Required**
This skill never automates logins, form submissions, or CAPTCHA solving.
At every step requiring authentication or human verification, clearly instruct
the user what to do and wait for their confirmation before continuing.

**Step 1 — Gather business information**
Ask the user to confirm (or extract from a provided URL using `fetch_page_content`):
- Business name (exact canonical spelling)
- Street address (canonical format per `references/nap-guidelines.md`)
- Phone number (with area code, consistent format)
- Website URL (no trailing slash, no UTM parameters)
- Business categories (primary + up to 3 secondary)
- Short description (150 chars max for directories with limits)
- Long description (500–750 words, keyword-rich but natural)
- Business hours (all 7 days)
- Service area (if service-area business without a storefront)
- Key photos needed: logo, exterior, interior, team, product/work examples

**Step 2 — Inspect target directory pages (optional)**
If the user provides specific citation site URLs:
- Call `fetch_page_content` on the listing/sign-up page to understand required fields
- Call `inspect_form_fields` on the "add listing" URL to identify field names and options
- Use this to customise the submission guide for each directory

**Step 3 — Prioritise directories**
- Refer to `references/directory-tiers.md` for priority ranking
- Tier 1: Google Business Profile, Bing Places, Apple Maps, Yelp, Facebook
- Tier 2: Industry-specific and national directories
- Tier 3: Local/niche directories
- Confirm with user which directories to target in this campaign

**Step 4 — Prepare submission pack**
For each directory, prepare:
- Exact business name to use
- Category selection (match to that directory's taxonomy)
- Tailored description (same information, different wording for each — avoid duplicate content)
- Phone format for that country/site
- Website URL (add UTM: `?utm_source=[directory]&utm_medium=local-listing`)
- Photo filenames to upload

**Step 5 — Guide step-by-step submission**
For each directory:
1. Tell the user the sign-up/claim URL
2. Walk through each UI step: where to click, what to select, what to paste
3. When a CAPTCHA or verification screen appears: stop, describe what to do, wait for confirmation
4. After listing is submitted: note the status (live / pending verification / needs phone/postcard)

**Step 6 — Verification tracking**
Create a tracking summary for the user:
| Directory | Status | Verification Method | Notes |
|---|---|---|---|
| Google Business Profile | Pending | Postcard (5–14 days) | |
| Bing Places | Live | Email verified | |

**Step 7 — Consistency check (if existing listings found)**
If the user has existing citations to audit:
- Compare each listing's NAP against the canonical format from Step 1
- Flag any inconsistencies: wrong phone format, old address, name variation
- Provide the exact correction to make on each platform
