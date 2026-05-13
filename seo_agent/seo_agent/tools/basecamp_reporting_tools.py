"""Basecamp monthly reporting helpers with structured summary output."""
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pydantic import BaseModel, Field

from .basecamp_tools import (
    get_basecamp_comments,
    get_basecamp_projects,
    get_basecamp_todolists,
    get_basecamp_todos,
)


class BasecampStructuredSummary(BaseModel):
    """Structured grouping of Basecamp activities."""

    on_page_technical: List[str] = Field(default_factory=list)
    off_page: List[str] = Field(default_factory=list)
    local_seo: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    period_label: str


def month_date_range(target_year: Optional[int], target_month: Optional[int]) -> Tuple[date, date]:
    today = date.today()
    year = target_year or today.year
    month = target_month or today.month
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def _coerce_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.date()
    except ValueError:
        return None


def _strip_html(value: str) -> str:
    inside = False
    cleaned = []
    for char in value:
        if char == "<":
            inside = True
            continue
        if char == ">":
            inside = False
            continue
        if not inside:
            cleaned.append(char)
    return "".join(cleaned)


def collect_basecamp_activity(
    project_ids: List[int],
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    """Collect todos/comments for provided Basecamp projects in a date range."""
    project_lookup: Dict[int, str] = {}
    projects_result = get_basecamp_projects()
    if projects_result.get("status") == "success":
        for project in projects_result.get("projects", []):
            project_lookup[project["id"]] = project.get("name", f"Project {project['id']}")

    rows: List[Dict[str, Any]] = []
    for project_id in project_ids:
        todolists_result = get_basecamp_todolists(project_id)
        if todolists_result.get("status") != "success":
            continue
        todolists = todolists_result.get("todolists") or []
        for todolist in todolists:
            todos_result = get_basecamp_todos(project_id, todolist_id=todolist.get("id"))
            if todos_result.get("status") != "success":
                continue
            todos = todos_result.get("todos") or []
            for todo in todos:
                created = _coerce_date(todo.get("created_at"))
                completed = _coerce_date(todo.get("completed_at"))
                in_range = (
                    (created and start_date <= created <= end_date)
                    or (completed and start_date <= completed <= end_date)
                )
                if not in_range:
                    continue

                comments: List[str] = []
                comments_result = get_basecamp_comments(project_id, todo["id"])
                if comments_result.get("status") == "success":
                    for comment in comments_result.get("comments") or []:
                        body = _strip_html(comment.get("content", "")).strip()
                        if not body:
                            continue
                        comments.append(body)

                rows.append(
                    {
                        "project_id": project_id,
                        "project_name": project_lookup.get(project_id, f"Project {project_id}"),
                        "todolist_name": todolist.get("name") or todolist.get("title", ""),
                        "title": todo.get("content", ""),
                        "completed": todo.get("completed", False),
                        "assignees": todo.get("assignees", []),
                        "created_at": created.isoformat() if created else "",
                        "completed_at": completed.isoformat() if completed else "",
                        "comments": comments,
                    }
                )
    return rows


def _guess_category(item: Dict[str, Any]) -> str:
    title = f"{item.get('title','')} {item.get('todolist_name','')}".lower()
    on_page_kw = ["content", "blog", "meta", "internal", "technical", "audit", "page", "schema", "core web", "performance"]
    off_page_kw = ["backlink", "guest", "link", "pr", "outreach", "mention", "digital"]
    local_kw = ["gbp", "google business", "local", "citation", "review", "map", "gmb"]
    if any(keyword in title for keyword in off_page_kw):
        return "off_page"
    if any(keyword in title for keyword in local_kw):
        return "local_seo"
    if any(keyword in title for keyword in on_page_kw):
        return "on_page_technical"
    # fall back to todolist hints
    list_name = (item.get("todolist_name") or "").lower()
    if "local" in list_name or "gbp" in list_name:
        return "local_seo"
    if "link" in list_name or "off page" in list_name:
        return "off_page"
    return "on_page_technical"


def _dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for text in items:
        clean = text.strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        ordered.append(clean)
    return ordered


def build_structured_summary(rows: List[Dict[str, Any]], period_label: str) -> BasecampStructuredSummary:
    categorized: Dict[str, List[str]] = {
        "on_page_technical": [],
        "off_page": [],
        "local_seo": [],
    }
    for row in rows:
        title = row.get("title") or "Untitled Basecamp Task"
        snippet = ""
        if row.get("comments"):
            snippet = row["comments"][0]
        elif row.get("todolist_name"):
            snippet = f"From {row['todolist_name']}"
        elif row.get("completed"):
            snippet = "Completed this month"
        else:
            snippet = "In progress"
        snippet = snippet.rstrip(".")
        bullet = f"{title} - {snippet}."
        category = _guess_category(row)
        categorized.setdefault(category, []).append(bullet)

    return BasecampStructuredSummary(
        on_page_technical=_dedupe(categorized.get("on_page_technical", [])),
        off_page=_dedupe(categorized.get("off_page", [])),
        local_seo=_dedupe(categorized.get("local_seo", [])),
        next_steps=[],
        period_label=period_label,
    )


def format_structured_summary(summary: BasecampStructuredSummary) -> str:
    sections = [
        ("On Page/Technical", summary.on_page_technical),
        ("Off Page", summary.off_page),
        ("Local SEO", summary.local_seo),
        ("Next Steps", summary.next_steps),
    ]
    lines = []
    for heading, items in sections:
        lines.append(heading)
        if items:
            lines.extend(items)
        else:
            lines.append("No items captured for this section.")
    return "\n".join(lines)


def generate_basecamp_structured_summary(
    project_ids: List[int],
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> Dict[str, Any]:
    """Generate structured Basecamp activity summary for the requested month."""
    start, end = month_date_range(year, month)
    rows = collect_basecamp_activity(project_ids, start, end)
    label = f"{start.strftime('%B %Y')}"
    summary = build_structured_summary(rows, label)
    result = summary.model_dump()
    result["formatted_text"] = format_structured_summary(summary)
    result["project_ids"] = list(project_ids)
    result["start_date"] = start.isoformat()
    result["end_date"] = end.isoformat()
    result["total_tasks"] = len(rows)
    return result
