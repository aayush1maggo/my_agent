"""Everhour API Tools for Timesheet Management"""
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import requests

from ..config import EVERHOUR_API_KEY, EVERHOUR_BASE_URL


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _headers() -> Dict[str, str]:
    return {
        "X-Api-Key": EVERHOUR_API_KEY,
        "Content-Type": "application/json",
    }


def _check_key() -> Optional[str]:
    """Return an error string if EVERHOUR_API_KEY is missing, else None."""
    if not EVERHOUR_API_KEY:
        return (
            "EVERHOUR_API_KEY is not configured. "
            "Add it to seo_agent/.env — get yours from "
            "Everhour → Settings → My Profile → Application Access."
        )
    return None


def _seconds_to_hm(seconds: int) -> str:
    """Convert integer seconds to a human-readable string like '1h 30m'."""
    if not seconds:
        return "0m"
    hours, remainder = divmod(abs(int(seconds)), 3600)
    minutes = remainder // 60
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return " ".join(parts) if parts else "0m"


def _current_week_dates() -> tuple[str, str]:
    """Return (monday, sunday) of the current ISO week as YYYY-MM-DD strings."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday.isoformat(), sunday.isoformat()


def _handle_response_error(response: requests.Response, context: str) -> Dict[str, Any]:
    """Return a structured error dict for non-2xx responses."""
    if response.status_code == 401:
        return {"status": "error", "error": "Invalid API key — check EVERHOUR_API_KEY in .env"}
    if response.status_code == 404:
        return {"status": "error", "error": f"{context} not found — verify the ID"}
    if response.status_code == 422:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        return {"status": "error", "error": f"Validation error: {detail}"}
    return {
        "status": "error",
        "error": f"HTTP {response.status_code}: {response.text[:200]}",
    }


# ---------------------------------------------------------------------------
# Public tools
# ---------------------------------------------------------------------------

def get_everhour_projects() -> Dict[str, Any]:
    """List all Everhour projects (includes Basecamp-synced projects).

    Returns project IDs, names, and statuses. Use this to discover project IDs
    before filtering task searches.

    Returns:
        Dict with projects list (id, name, status) and count.
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        response = requests.get(
            f"{EVERHOUR_BASE_URL}/projects",
            headers=_headers(),
            timeout=30,
        )
        if not response.ok:
            return _handle_response_error(response, "Projects")

        data = response.json()
        projects = data if isinstance(data, list) else data.get("data", [])

        return {
            "status": "success",
            "projects": [
                {
                    "id": p.get("id"),
                    "name": p.get("name", ""),
                    "status": p.get("status", ""),
                }
                for p in projects
            ],
            "count": len(projects),
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def get_everhour_task(task_id: str) -> Dict[str, Any]:
    """Get full details for a specific Everhour task by ID.

    Use this when you already have a task ID and need full task info.

    Args:
        task_id: The Everhour task ID (e.g. 'bc2:123456789')

    Returns:
        Dict with task details (id, name, project, time_today_hm, time_total_hm, status)
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        response = requests.get(
            f"{EVERHOUR_BASE_URL}/tasks/{task_id}",
            headers=_headers(),
            timeout=30,
        )
        if not response.ok:
            return _handle_response_error(response, "Task")

        t = response.json()
        time_data = t.get("time", {}) if isinstance(t.get("time"), dict) else {}

        return {
            "status": "success",
            "task": {
                "id": t.get("id"),
                "name": t.get("name", ""),
                "project_id": t.get("projectId", ""),
                "project_name": (t.get("projects") or [{}])[0].get("name", "") if t.get("projects") else "",
                "time_today_seconds": time_data.get("today", 0),
                "time_today_hm": _seconds_to_hm(time_data.get("today", 0)),
                "time_total_seconds": time_data.get("total", 0),
                "time_total_hm": _seconds_to_hm(time_data.get("total", 0)),
                "status": t.get("status", ""),
            },
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def add_time_to_task(
    task_id: str,
    hours: float,
    minutes: int = 0,
    date: Optional[str] = None,
    comment: Optional[str] = None,
) -> Dict[str, Any]:
    """Log time to a task. This is the main timesheet tool for recording work.

    Converts hours + minutes to seconds internally.
    Date defaults to today if not provided.

    Args:
        task_id: The Everhour task ID (get from search_everhour_tasks first)
        hours: Number of hours worked (can be fractional e.g. 1.5)
        minutes: Additional minutes (e.g. hours=1, minutes=30 for 1h 30m)
        date: Date in YYYY-MM-DD format. Defaults to today.
        comment: Optional note describing the work done

    Returns:
        Dict with logged time entry details
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        total_seconds = int(hours * 3600) + int(minutes * 60)
        if total_seconds <= 0:
            return {"status": "error", "error": "Time must be greater than 0"}

        log_date = date or date_today_str()
        payload: Dict[str, Any] = {"time": total_seconds, "date": log_date}
        if comment:
            payload["comment"] = comment

        response = requests.post(
            f"{EVERHOUR_BASE_URL}/tasks/{task_id}/time",
            headers=_headers(),
            json=payload,
            timeout=30,
        )
        if not response.ok:
            return _handle_response_error(response, "Task")

        entry = response.json()
        logged_seconds = entry.get("time", total_seconds)

        return {
            "status": "success",
            "entry": {
                "task_id": task_id,
                "date": log_date,
                "time_seconds": logged_seconds,
                "time_hm": _seconds_to_hm(logged_seconds),
                "comment": entry.get("comment", comment or ""),
            },
            "message": f"Logged {_seconds_to_hm(logged_seconds)} to task {task_id} on {log_date}",
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def date_today_str() -> str:
    """Return today's date as YYYY-MM-DD string."""
    return date.today().isoformat()


def get_my_time_records(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """Get my logged time records for a date range (defaults to current week).

    Use this to review what time has been logged: "show me my timesheet", "what did I log this week".

    Args:
        from_date: Start date YYYY-MM-DD (defaults to Monday of current week)
        to_date: End date YYYY-MM-DD (defaults to Sunday of current week)
        limit: Maximum number of records (default 50)

    Returns:
        Dict with time entries (task_name, project_name, date, time_hm, comment)
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        if not from_date or not to_date:
            from_date, to_date = _current_week_dates()

        params: Dict[str, Any] = {
            "from": from_date,
            "to": to_date,
            "limit": limit,
        }

        response = requests.get(
            f"{EVERHOUR_BASE_URL}/users/me/time",
            headers=_headers(),
            params=params,
            timeout=30,
        )
        if not response.ok:
            return _handle_response_error(response, "Time records")

        data = response.json()
        records = data if isinstance(data, list) else data.get("data", [])

        total_seconds = sum(r.get("time", 0) for r in records)

        return {
            "status": "success",
            "entries": [
                {
                    "id": r.get("id"),
                    "task_id": r.get("task", {}).get("id", "") if isinstance(r.get("task"), dict) else r.get("taskId", ""),
                    "task_name": r.get("task", {}).get("name", "") if isinstance(r.get("task"), dict) else "",
                    "project_name": (
                        (r.get("task", {}).get("projects") or [{}])[0].get("name", "")
                        if isinstance(r.get("task"), dict) and r["task"].get("projects")
                        else ""
                    ),
                    "date": r.get("date", ""),
                    "time_seconds": r.get("time", 0),
                    "time_hm": _seconds_to_hm(r.get("time", 0)),
                    "comment": r.get("comment", ""),
                }
                for r in records
            ],
            "count": len(records),
            "total_time_hm": _seconds_to_hm(total_seconds),
            "from_date": from_date,
            "to_date": to_date,
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def update_time_record(
    task_id: str,
    date: str,
    hours: float,
    minutes: int = 0,
    comment: Optional[str] = None,
) -> Dict[str, Any]:
    """Update (overwrite) a time entry for a specific task on a specific date.

    Use this to correct a previously logged time entry.

    Args:
        task_id: The Everhour task ID
        date: Date of the entry to update (YYYY-MM-DD)
        hours: New number of hours
        minutes: Additional minutes
        comment: Optional updated comment

    Returns:
        Dict with updated entry details
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        total_seconds = int(hours * 3600) + int(minutes * 60)
        if total_seconds <= 0:
            return {"status": "error", "error": "Time must be greater than 0"}

        payload: Dict[str, Any] = {"time": total_seconds}
        if comment is not None:
            payload["comment"] = comment

        response = requests.put(
            f"{EVERHOUR_BASE_URL}/tasks/{task_id}/time/{date}",
            headers=_headers(),
            json=payload,
            timeout=30,
        )
        if not response.ok:
            return _handle_response_error(response, "Time record")

        entry = response.json()
        logged_seconds = entry.get("time", total_seconds)

        return {
            "status": "success",
            "entry": {
                "task_id": task_id,
                "date": date,
                "time_seconds": logged_seconds,
                "time_hm": _seconds_to_hm(logged_seconds),
                "comment": entry.get("comment", comment or ""),
            },
            "message": f"Updated time to {_seconds_to_hm(logged_seconds)} for task {task_id} on {date}",
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def delete_time_record(task_id: str, date: str) -> Dict[str, Any]:
    """Delete a time entry for a specific task on a specific date.

    Args:
        task_id: The Everhour task ID
        date: Date of the entry to delete (YYYY-MM-DD)

    Returns:
        Dict with confirmation message
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        response = requests.delete(
            f"{EVERHOUR_BASE_URL}/tasks/{task_id}/time/{date}",
            headers=_headers(),
            timeout=30,
        )
        if response.status_code == 404:
            return {"status": "error", "error": f"No time entry found for task {task_id} on {date}"}
        if not response.ok:
            return _handle_response_error(response, "Time record")

        return {
            "status": "success",
            "message": f"Deleted time entry for task {task_id} on {date}",
            "task_id": task_id,
            "date": date,
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def create_everhour_task(
    project_id: str,
    name: str,
    estimate_seconds: Optional[int] = None,
    assignees: Optional[List[str]] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new task inside an Everhour project.

    Args:
        project_id: The Everhour project ID (get from get_everhour_projects)
        name: Task name
        estimate_seconds: Optional time estimate in seconds (e.g. 3600 for 1h)
        assignees: Optional list of user IDs to assign the task to
        status: Optional task status (e.g. 'open', 'completed')

    Returns:
        Dict with created task details (id, name, project_id, status)
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        payload: Dict[str, Any] = {"name": name}
        if estimate_seconds is not None:
            payload["estimate"] = {"value": estimate_seconds}
        if assignees:
            payload["assignees"] = assignees
        if status:
            payload["status"] = status

        response = requests.post(
            f"{EVERHOUR_BASE_URL}/projects/{project_id}/tasks",
            headers=_headers(),
            json=payload,
            timeout=30,
        )
        if not response.ok:
            return _handle_response_error(response, "Task")

        t = response.json()
        return {
            "status": "success",
            "task": {
                "id": t.get("id"),
                "name": t.get("name", ""),
                "project_id": t.get("projectId", project_id),
                "status": t.get("status", ""),
                "estimate_seconds": (t.get("estimate") or {}).get("value"),
                "estimate_hm": _seconds_to_hm((t.get("estimate") or {}).get("value", 0)),
                "assignees": t.get("assignees", []),
            },
            "message": f"Task '{name}' created in project {project_id}",
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def search_everhour_tasks(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search Everhour tasks by name across all projects.

    Use this to find a task ID when you only know the task name.
    For project-scoped search, use search_everhour_project_tasks instead.

    Args:
        query: Search term (task name or keyword)
        limit: Maximum number of results (default 20)

    Returns:
        Dict with tasks list (id, name, project_name, time_today_hm, time_total_hm, status)
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        response = requests.get(
            f"{EVERHOUR_BASE_URL}/tasks",
            headers=_headers(),
            params={"query": query, "limit": limit},
            timeout=30,
        )
        if not response.ok:
            return _handle_response_error(response, "Tasks")

        data = response.json()
        tasks = data if isinstance(data, list) else data.get("data", [])

        return {
            "status": "success",
            "tasks": [
                {
                    "id": t.get("id"),
                    "name": t.get("name", ""),
                    "project_id": t.get("projectId", ""),
                    "project_name": (t.get("projects") or [{}])[0].get("name", "") if t.get("projects") else "",
                    "time_today_hm": _seconds_to_hm(
                        t.get("time", {}).get("today", 0) if isinstance(t.get("time"), dict) else 0
                    ),
                    "time_total_hm": _seconds_to_hm(
                        t.get("time", {}).get("total", 0) if isinstance(t.get("time"), dict) else 0
                    ),
                    "status": t.get("status", ""),
                }
                for t in tasks
            ],
            "count": len(tasks),
            "query": query,
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def search_everhour_project_tasks(
    project_id: str,
    query: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """Search or list tasks within a specific Everhour project.

    Use this when you already know the project and want to browse or filter its tasks.
    More focused than search_everhour_tasks which searches across all projects.

    Args:
        project_id: The Everhour project ID (get from get_everhour_projects)
        query: Optional search term to filter tasks by name
        limit: Maximum number of results (default 50)

    Returns:
        Dict with tasks list (id, name, status, time_total_hm, estimate_hm)
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        params: Dict[str, Any] = {"limit": limit}
        if query:
            params["query"] = query

        response = requests.get(
            f"{EVERHOUR_BASE_URL}/projects/{project_id}/tasks",
            headers=_headers(),
            params=params,
            timeout=30,
        )
        if not response.ok:
            return _handle_response_error(response, "Project tasks")

        data = response.json()
        tasks = data if isinstance(data, list) else data.get("data", [])

        return {
            "status": "success",
            "project_id": project_id,
            "tasks": [
                {
                    "id": t.get("id"),
                    "name": t.get("name", ""),
                    "status": t.get("status", ""),
                    "time_total_seconds": t.get("time", {}).get("total", 0) if isinstance(t.get("time"), dict) else 0,
                    "time_total_hm": _seconds_to_hm(
                        t.get("time", {}).get("total", 0) if isinstance(t.get("time"), dict) else 0
                    ),
                    "estimate_seconds": (t.get("estimate") or {}).get("value"),
                    "estimate_hm": _seconds_to_hm((t.get("estimate") or {}).get("value", 0)),
                    "assignees": t.get("assignees", []),
                }
                for t in tasks
            ],
            "count": len(tasks),
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def get_current_timer() -> Dict[str, Any]:
    """Check if a timer is currently running.

    Call this before starting a new timer to avoid conflicts.

    Returns:
        Dict with timer info if running, or {"running": false} if no timer is active.
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        response = requests.get(
            f"{EVERHOUR_BASE_URL}/timers/current",
            headers=_headers(),
            timeout=30,
        )

        if response.status_code == 404:
            return {"status": "success", "running": False, "message": "No timer currently running"}

        if not response.ok:
            return _handle_response_error(response, "Timer")

        timer = response.json()
        if not timer or not timer.get("taskId"):
            return {"status": "success", "running": False, "message": "No timer currently running"}

        elapsed = timer.get("duration", 0)
        return {
            "status": "success",
            "running": True,
            "timer": {
                "task_id": timer.get("taskId", ""),
                "task_name": timer.get("task", {}).get("name", "") if isinstance(timer.get("task"), dict) else "",
                "started_at": timer.get("startedAt", ""),
                "elapsed_seconds": elapsed,
                "elapsed_hm": _seconds_to_hm(elapsed),
                "comment": timer.get("comment", ""),
            },
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def start_timer(task_id: str, comment: Optional[str] = None) -> Dict[str, Any]:
    """Start a live timer on a task. Stops any currently running timer automatically.

    Args:
        task_id: The Everhour task ID to track time against
        comment: Optional note for the timer session

    Returns:
        Dict with timer start details
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        payload: Dict[str, Any] = {"task": task_id}
        if comment:
            payload["comment"] = comment

        response = requests.post(
            f"{EVERHOUR_BASE_URL}/timers",
            headers=_headers(),
            json=payload,
            timeout=30,
        )
        if not response.ok:
            return _handle_response_error(response, "Task")

        timer = response.json()
        return {
            "status": "success",
            "timer": {
                "task_id": timer.get("taskId", task_id),
                "task_name": timer.get("task", {}).get("name", "") if isinstance(timer.get("task"), dict) else "",
                "started_at": timer.get("startedAt", ""),
                "comment": timer.get("comment", comment or ""),
            },
            "message": f"Timer started on task {task_id}",
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def stop_current_timer() -> Dict[str, Any]:
    """Stop the currently running timer and convert elapsed time into a time record.

    Returns:
        Dict with the final time logged from the stopped timer.
    """
    err = _check_key()
    if err:
        return {"status": "error", "error": err}

    try:
        response = requests.delete(
            f"{EVERHOUR_BASE_URL}/timers/current",
            headers=_headers(),
            timeout=30,
        )

        if response.status_code == 404:
            return {"status": "error", "error": "No timer currently running"}

        if not response.ok:
            return _handle_response_error(response, "Timer")

        timer = response.json()
        duration = timer.get("duration", 0)

        return {
            "status": "success",
            "timer": {
                "task_id": timer.get("taskId", ""),
                "task_name": timer.get("task", {}).get("name", "") if isinstance(timer.get("task"), dict) else "",
                "duration_seconds": duration,
                "duration_hm": _seconds_to_hm(duration),
                "comment": timer.get("comment", ""),
            },
            "message": f"Timer stopped. Logged {_seconds_to_hm(duration)}.",
        }

    except requests.RequestException as exc:
        return {"status": "error", "error": f"API request failed: {exc}"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
