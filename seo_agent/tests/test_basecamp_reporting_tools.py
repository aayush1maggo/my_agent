from datetime import date

from seo_agent.tools.basecamp_reporting_tools import (
    BasecampStructuredSummary,
    build_structured_summary,
    format_structured_summary,
    month_date_range,
)


def test_month_date_range_handles_december():
    start, end = month_date_range(2025, 12)
    assert start == date(2025, 12, 1)
    assert end == date(2025, 12, 31)


def test_build_structured_summary_groups_keywords():
    rows = [
        {
            "title": "Meta titles refreshed",
            "todolist_name": "On-page fixes",
            "completed": True,
            "assignees": ["Alex"],
            "created_at": "2025-01-05",
            "completed_at": "2025-01-06",
            "comments": ["Alex: Completed updates"],
        },
        {
            "title": "Guest post outreach",
            "todolist_name": "Off page",
            "completed": False,
            "assignees": ["Sam"],
            "created_at": "2025-01-07",
            "completed_at": "",
            "comments": [],
        },
        {
            "title": "GBP review replies",
            "todolist_name": "Local tasks",
            "completed": True,
            "assignees": [],
            "created_at": "2025-01-08",
            "completed_at": "2025-01-09",
            "comments": [],
        },
    ]
    summary = build_structured_summary(rows, "January 2025")
    assert "Meta titles refreshed" in summary.on_page_technical[0]
    assert "Guest post outreach" in summary.off_page[0]
    assert "GBP review replies" in summary.local_seo[0]
    assert summary.next_steps == []


def test_format_structured_summary_matches_structure_file():
    summary = BasecampStructuredSummary(
        on_page_technical=["Task A"],
        off_page=["Task B"],
        local_seo=[],
        next_steps=["Next 1", "Next 2"],
        period_label="January 2025",
    )
    text = format_structured_summary(summary)
    expected_sections = ["On Page/Technical", "Off Page", "Local SEO", "Next Steps"]
    for heading in expected_sections:
        assert heading in text
    assert "Task A" in text
    assert "Task B" in text
    assert "Next 1" in text
