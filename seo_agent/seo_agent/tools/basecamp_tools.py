"""Basecamp 3 API Tools for Project Management"""
from typing import Dict, Any, Optional, List
import re
from pathlib import Path

import requests

from ..config import (
    BASECAMP_API_KEY,
    BASECAMP_ACCOUNT_ID,
    BASECAMP_CLIENT_ID,
    BASECAMP_CLIENT_SECRET,
    BASECAMP_REDIRECT_URI,
)

_people_cache: Dict[str, Dict[str, Any]] = {}
MENTION_PATTERN = re.compile(r"@([A-Za-z0-9][A-Za-z0-9 .'\-_/&]+)")


def _basecamp_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {BASECAMP_API_KEY}",
        "User-Agent": "SEO Agent (your-email@example.com)",
        "Content-Type": "application/json",
    }


def _get_next_link(link_header: Optional[str]) -> Optional[str]:
    """Parse RFC5988 Link header and return the URL for rel=\"next\", if present."""
    if not link_header:
        return None

    # The header can contain multiple comma-separated links; find rel=\"next\"
    parts = [part.strip() for part in link_header.split(",") if part.strip()]
    for part in parts:
        # Example part: <https://.../projects.json?page=2>; rel=\"next\"
        if 'rel="next"' not in part:
            continue
        if part.startswith("<") and ">" in part:
            url = part[1 : part.index(">")]
            return url or None
    return None


def _load_people_cache() -> Dict[str, Dict[str, Any]]:
    """Load and cache Basecamp people for mention replacement."""
    global _people_cache

    if _people_cache:
        return _people_cache

    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {}

        url = f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/people.json"
        headers = _basecamp_headers()
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        people = response.json() or []
        cache: Dict[str, Dict[str, Any]] = {}
        for person in people:
            name = person.get("name", "").strip()
            if not name:
                continue
            cache[name.lower()] = {
                "id": person.get("id"),
                "name": name,
            }

        _people_cache = cache
        return _people_cache

    except requests.exceptions.RequestException:
        return {}
    except Exception:
        return {}


def _replace_user_mentions(text: str) -> str:
    """Convert @Name to Basecamp mention hyperlinks when possible."""
    if not text or "@" not in text:
        return text

    people_map = _load_people_cache()
    if not people_map:
        return text

    def repl(match: re.Match) -> str:
        name = match.group(1).strip()
        if not name:
            return match.group(0)
        person = people_map.get(name.lower())
        if not person or not person.get("id"):
            return match.group(0)
        person_id = person["id"]
        display_name = person["name"]
        return f"[{display_name}](https://3.basecamp.com/{BASECAMP_ACCOUNT_ID}/people/{person_id})"

    return MENTION_PATTERN.sub(repl, text)


def get_basecamp_projects() -> Dict[str, Any]:
    """Get all Basecamp projects using Basecamp pagination.

    Follows the Link header (RFC5988) with rel=\"next\" to retrieve all pages.

    Returns: Dict with projects list (id, name, description, status)
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        headers = _basecamp_headers()
        url = f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/projects.json"

        all_projects: List[Dict[str, Any]] = []

        while url:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            page_projects = response.json() or []
            if not isinstance(page_projects, list):
                # Defensive: unexpected payload
                break

            all_projects.extend(page_projects)

            # Follow RFC5988 Link header for next page, if present
            link_header = response.headers.get("Link") or response.headers.get("link")
            url = _get_next_link(link_header)

        return {
            "status": "success",
            "projects": [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "description": p.get("description", ""),
                    "status": p.get("status", "active"),
                    "created_at": p.get("created_at", ""),
                    "updated_at": p.get("updated_at", ""),
                }
                for p in all_projects
            ],
            "count": len(all_projects),
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
        }


def create_basecamp_project(
    name: str,
    description: str = "",
) -> Dict[str, Any]:
    """Create a new Basecamp project.

    Args:
        name: Project name (required)
        description: Optional project description

    Returns: Dict with created project info
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/projects.json"
        headers = _basecamp_headers()

        payload: Dict[str, Any] = {"name": name}
        if description:
            payload["description"] = description

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        project = response.json()

        return {
            "status": "success",
            "project": {
                "id": project["id"],
                "name": project.get("name", ""),
                "description": project.get("description", ""),
                "status": project.get("status", "active"),
                "url": project.get("app_url", ""),
                "created_at": project.get("created_at", ""),
            },
            "message": f"Created project: {name}",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
        }


def trash_basecamp_project(
    project_id: int,
) -> Dict[str, Any]:
    """Trash (soft-delete) a Basecamp project.

    Moves the project to trash. It can be recovered from trash in Basecamp.

    Args:
        project_id: Basecamp project ID to trash

    Returns: Dict with status confirmation
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/projects/{project_id}.json"
        )
        headers = _basecamp_headers()

        response = requests.delete(url, headers=headers, timeout=30)
        response.raise_for_status()

        return {
            "status": "success",
            "message": f"Project {project_id} moved to trash.",
            "project_id": project_id,
            "note": "The project can be recovered from trash in Basecamp.",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "project_id": project_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "project_id": project_id,
        }


def get_basecamp_people() -> Dict[str, Any]:
    """Get all Basecamp people.

    Returns: Dict with people list (id, name, email, title)
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/people.json"
        headers = _basecamp_headers()

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        people = response.json()

        return {
            "status": "success",
            "people": [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "email": p.get("email_address", ""),
                    "title": p.get("title", ""),
                    "admin": p.get("admin", False),
                    "owner": p.get("owner", False),
                }
                for p in people
            ],
            "count": len(people),
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
        }


def get_basecamp_todolists(project_id: int) -> Dict[str, Any]:
    """Get all todolists from a Basecamp project.

    Args:
        project_id: Basecamp project ID (bucket ID)

    Returns: Dict with todolists (id, name, todos_count, completed_count)
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        headers = _basecamp_headers()

        # 1) Get the project so we can find the todoset tool in the dock
        project_url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/projects/{project_id}.json"
        )
        project_response = requests.get(project_url, headers=headers, timeout=30)

        if project_response.status_code == 404:
            return {
                "status": "success",
                "todolists": [],
                "count": 0,
                "project_id": project_id,
                "message": "Project not found or not accessible.",
                "suggestion": "Verify the project ID and your Basecamp permissions.",
            }

        project_response.raise_for_status()
        project = project_response.json()

        dock = project.get("dock", [])
        todoset_entry = next(
            (
                item
                for item in dock
                if item.get("name") == "todoset" and item.get("enabled")
            ),
            None,
        )

        if not todoset_entry:
            return {
                "status": "success",
                "todolists": [],
                "count": 0,
                "project_id": project_id,
                "message": (
                    'No To-dos tool found in this project. The "To-dos" feature may '
                    "not be enabled in Basecamp project settings."
                ),
                "suggestion": (
                    'To enable: Go to Basecamp Project Settings and enable the "To-dos" tool.'
                ),
            }

        # 2) Follow the todoset URL from the dock
        todoset_url = todoset_entry.get("url")
        if not todoset_url:
            return {
                "status": "error",
                "error": "Todoset URL not found in project dock.",
                "project_id": project_id,
            }

        todoset_response = requests.get(todoset_url, headers=headers, timeout=30)
        todoset_response.raise_for_status()
        todoset = todoset_response.json()

        # 3) Use the official todolists endpoint from the todoset
        todolists_url = todoset.get("todolists_url")
        if not todolists_url:
            return {
                "status": "error",
                "error": "todolists_url not found on todoset resource.",
                "project_id": project_id,
            }

        todolists_response = requests.get(todolists_url, headers=headers, timeout=30)
        todolists_response.raise_for_status()

        todolists = todolists_response.json()

        return {
            "status": "success",
            "todolists": [
                {
                    "id": tl["id"],
                    "name": tl["title"],
                    "description": tl.get("description", ""),
                    "completed": tl.get("completed", False),
                    "todos_count": tl.get("todos_count", 0),
                    "completed_count": tl.get("completed_count", 0),
                    "todos_url": tl.get("todos_url", ""),
                    "url": tl.get("app_url", ""),
                }
                for tl in todolists
            ],
            "count": len(todolists),
            "project_id": project_id,
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "project_id": project_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "project_id": project_id,
        }


def _fetch_todos_for_list(
    todos_url: str, headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Fetch both pending and completed todos for a list using the official todos endpoint."""
    todos: List[Dict[str, Any]] = []

    # Pending (active) todos
    response = requests.get(todos_url, headers=headers, timeout=30)
    if response.status_code != 404:
        response.raise_for_status()
        todos.extend(response.json())

    # Completed todos
    response_completed = requests.get(
        todos_url, headers=headers, params={"completed": "true"}, timeout=30
    )
    if response_completed.status_code != 404:
        response_completed.raise_for_status()
        todos.extend(response_completed.json())

    return todos


def get_basecamp_todos(
    project_id: int,
    todolist_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get todos from a Basecamp project.

    Args:
        project_id: Basecamp project ID (bucket ID)
        todolist_id: Optional specific todolist ID. If not provided, returns all
            todos from all todolists in the project.

    Returns: Dict with todos list (id, content, status, assignees)
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        headers = _basecamp_headers()

        if todolist_id is not None:
            # Use the official todos endpoint for a single list
            base_todos_url = (
                f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/"
                f"{project_id}/todolists/{todolist_id}/todos.json"
            )
            todos = _fetch_todos_for_list(base_todos_url, headers)
        else:
            # Get all todolists first
            todolists_result = get_basecamp_todolists(project_id)

            if todolists_result.get("status") != "success":
                return todolists_result

            if todolists_result.get("count", 0) == 0:
                return {
                    "status": "success",
                    "todos": [],
                    "count": 0,
                    "project_id": project_id,
                    "message": todolists_result.get(
                        "message", "No todolists found in this project."
                    ),
                    "suggestion": todolists_result.get(
                        "suggestion",
                        "Enable the To-dos tool in Basecamp project settings.",
                    ),
                }

            todos = []
            for todolist in todolists_result["todolists"]:
                todos_url = todolist.get("todos_url") or (
                    f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/"
                    f"{project_id}/todolists/{todolist['id']}/todos.json"
                )
                todos.extend(_fetch_todos_for_list(todos_url, headers))

        return {
            "status": "success",
            "todos": [
                {
                    "id": t["id"],
                    "content": t.get("content", ""),
                    "completed": t.get("completed", False),
                    "assignees": [
                        a["name"]
                        for a in t.get("assignees", [])
                        if isinstance(a, dict) and "name" in a
                    ],
                    "due_on": t.get("due_on", ""),
                    "created_at": t.get("created_at", ""),
                    "url": t.get("app_url", ""),
                }
                for t in todos
            ],
            "count": len(todos),
            "project_id": project_id,
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "project_id": project_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "project_id": project_id,
        }


def create_basecamp_todo(
    project_id: int,
    todolist_id: int,
    content: str,
    description: str = "",
    assignee_ids: Optional[List[int]] = None,
    due_on: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a Basecamp todo.

    Args:
        project_id: Basecamp project ID (bucket)
        todolist_id: Todolist ID
        content: Todo title/content
        description: Optional description (rich text HTML allowed)
        assignee_ids: Optional list of people IDs
        due_on: Optional due date (YYYY-MM-DD)

    Returns: Dict with created todo info
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/"
            f"{project_id}/todolists/{todolist_id}/todos.json"
        )
        headers = _basecamp_headers()

        payload: Dict[str, Any] = {
            "content": content,
        }
        description = _replace_user_mentions(description)
        content = _replace_user_mentions(content)
        if description:
            payload["description"] = description
        if assignee_ids:
            payload["assignee_ids"] = assignee_ids
        if due_on:
            payload["due_on"] = due_on

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        todo = response.json()

        return {
            "status": "success",
            "todo": {
                "id": todo["id"],
                "content": todo.get("content", ""),
                "description": todo.get("description", ""),
                "completed": todo.get("completed", False),
                "url": todo.get("app_url", ""),
                "created_at": todo.get("created_at", ""),
            },
            "message": f"Created todo: {content}",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "content": content,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "content": content,
        }


def update_basecamp_todo(
    project_id: int,
    todo_id: int,
    content: Optional[str] = None,
    description: Optional[str] = None,
    assignee_ids: Optional[List[int]] = None,
    due_on: Optional[str] = None,
    starts_on: Optional[str] = None,
    completion_subscriber_ids: Optional[List[int]] = None,
    notify: Optional[bool] = None,
    completed: Optional[bool] = None,  # kept for backward compatibility, not used directly
) -> Dict[str, Any]:
    """Update a Basecamp todo using the official update endpoint.

    All existing fields are preserved unless explicitly overridden — the API
    clears any omitted parameter, so we fetch the todo first and merge.

    Args:
        project_id: Basecamp project ID (bucket)
        todo_id: Todo ID to update
        content: Optional new title/content
        description: Optional new rich-text description (HTML supported)
        assignee_ids: Optional new assignees (list of person IDs)
        due_on: Optional due date (YYYY-MM-DD)
        starts_on: Optional start date (YYYY-MM-DD) — defines a date range with due_on
        completion_subscriber_ids: Optional list of person IDs notified on completion
        notify: When True, notifies assignees of their assignment
        completed: Optional completion status (handled via dedicated completion endpoint;
            currently ignored here)

    Returns: Dict with updated todo info
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/"
            f"{project_id}/todos/{todo_id}.json"
        )
        headers = _basecamp_headers()

        # Fetch existing todo so we can preserve unspecified fields, as recommended
        # by the official Basecamp API.
        existing_response = requests.get(url, headers=headers, timeout=30)
        existing_response.raise_for_status()
        existing = existing_response.json()

        existing_assignees = existing.get("assignees") or []
        existing_completion_subs = existing.get("completion_subscribers") or []

        payload: Dict[str, Any] = {
            "content": existing.get("content", ""),
            "description": existing.get("description", ""),
            "due_on": existing.get("due_on"),
            "starts_on": existing.get("starts_on"),
            "assignee_ids": [
                a["id"]
                for a in existing_assignees
                if isinstance(a, dict) and "id" in a
            ],
            "completion_subscriber_ids": [
                s["id"]
                for s in existing_completion_subs
                if isinstance(s, dict) and "id" in s
            ],
        }

        if content is not None:
            content = _replace_user_mentions(content)
            payload["content"] = content
        if description is not None:
            description = _replace_user_mentions(description)
            payload["description"] = description
        if assignee_ids is not None:
            payload["assignee_ids"] = assignee_ids
        if due_on is not None:
            payload["due_on"] = due_on
        if starts_on is not None:
            payload["starts_on"] = starts_on
        if completion_subscriber_ids is not None:
            payload["completion_subscriber_ids"] = completion_subscriber_ids
        if notify is not None:
            payload["notify"] = notify

        response = requests.put(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        todo = response.json()

        return {
            "status": "success",
            "todo": {
                "id": todo["id"],
                "content": todo.get("content", ""),
                "description": todo.get("description", ""),
                "completed": todo.get("completed", False),
                "url": todo.get("app_url", ""),
                "updated_at": todo.get("updated_at", ""),
            },
            "message": "Todo updated successfully",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "todo_id": todo_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "todo_id": todo_id,
        }


def get_basecamp_comments(
    project_id: int,
    recording_id: int,
) -> Dict[str, Any]:
    """Get comments for a given recording (e.g., todo, todolist, message)."""
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/"
            f"{project_id}/recordings/{recording_id}/comments.json"
        )
        headers = _basecamp_headers()

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        comments = response.json()

        return {
            "status": "success",
            "comments": [
                {
                    "id": c["id"],
                    "content": c.get("content", ""),
                    "created_at": c.get("created_at", ""),
                    "updated_at": c.get("updated_at", ""),
                    "creator": c.get("creator", {}).get("name"),
                    "url": c.get("app_url", ""),
                }
                for c in comments
            ],
            "count": len(comments),
            "project_id": project_id,
            "recording_id": recording_id,
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "project_id": project_id,
            "recording_id": recording_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "project_id": project_id,
            "recording_id": recording_id,
        }


def create_basecamp_comment(
    project_id: int,
    recording_id: int,
    content: str,
) -> Dict[str, Any]:
    """Create a comment on a given recording (e.g., todo, todolist, message)."""
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/"
            f"{project_id}/recordings/{recording_id}/comments.json"
        )
        headers = _basecamp_headers()

        content = _replace_user_mentions(content)
        payload = {
            "content": content,
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        comment = response.json()

        return {
            "status": "success",
            "comment": {
                "id": comment["id"],
                "content": comment.get("content", ""),
                "created_at": comment.get("created_at", ""),
                "updated_at": comment.get("updated_at", ""),
                "creator": comment.get("creator", {}).get("name"),
                "url": comment.get("app_url", ""),
            },
            "project_id": project_id,
            "recording_id": recording_id,
            "message": "Comment created successfully",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "project_id": project_id,
            "recording_id": recording_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "project_id": project_id,
            "recording_id": recording_id,
        }


def get_basecamp_auth_url() -> Dict[str, Any]:
    """Generate the Basecamp OAuth authorization URL so the user can authenticate.

    Use this when Basecamp is not authenticated or the token has expired.
    Returns a URL for the user to open in their browser.

    After visiting the URL and authorizing:
    1. The browser redirects to the redirect URI with a 'code=' parameter in the URL.
    2. If no local server is running, the browser will show an error page — that is fine.
    3. The user must copy the code value from the browser address bar and supply it
       to exchange_basecamp_auth_code().

    Returns: Dict with auth_url and step-by-step instructions.
    """
    try:
        if not BASECAMP_CLIENT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_CLIENT_ID is not set in the .env file.",
                "instructions": (
                    "Create an OAuth application at https://launchpad.37signals.com/integrations "
                    "and add BASECAMP_CLIENT_ID and BASECAMP_CLIENT_SECRET to your .env file."
                ),
            }

        auth_url = (
            f"https://launchpad.37signals.com/authorization/new?"
            f"type=web_server&"
            f"client_id={BASECAMP_CLIENT_ID}&"
            f"redirect_uri={BASECAMP_REDIRECT_URI}"
        )

        return {
            "status": "success",
            "auth_url": auth_url,
            "redirect_uri": BASECAMP_REDIRECT_URI,
            "instructions": (
                "STEP 1: Open the auth_url in your browser and click 'Allow access'.\n"
                "STEP 2: After authorizing, your browser will attempt to redirect to "
                f"{BASECAMP_REDIRECT_URI}.\n"
                "STEP 3: If that page cannot load (no local server running), that is expected. "
                "Look at the URL in your browser's address bar — it will contain "
                "'?code=XXXXXX' at the end.\n"
                "STEP 4: Copy the code value (the part after '?code=') and give it to me "
                "so I can call exchange_basecamp_auth_code() to complete the login."
            ),
        }

    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
        }


def exchange_basecamp_auth_code(code: str) -> Dict[str, Any]:
    """Exchange a Basecamp OAuth authorization code for an access token and save it.

    After the user has visited the auth URL from get_basecamp_auth_url() and authorized
    the application, they receive a one-time code in the redirect URL. This function
    exchanges that code for a permanent access token, saves it to the .env file, and
    activates it immediately so all other Basecamp tools work without a restart.

    Args:
        code: The authorization code from the browser address bar after OAuth redirect.
              It appears as the value of the 'code' query parameter, e.g. '?code=XXXXX'.

    Returns: Dict with success status, discovered account info, and confirmation message.
    """
    global BASECAMP_API_KEY, BASECAMP_ACCOUNT_ID, _people_cache

    try:
        if not BASECAMP_CLIENT_ID or not BASECAMP_CLIENT_SECRET:
            return {
                "status": "error",
                "error": (
                    "BASECAMP_CLIENT_ID and BASECAMP_CLIENT_SECRET must be set in .env "
                    "before exchanging an authorization code."
                ),
            }

        # Exchange authorization code for an access token
        token_response = requests.post(
            "https://launchpad.37signals.com/authorization/token",
            data={
                "type": "web_server",
                "client_id": BASECAMP_CLIENT_ID,
                "client_secret": BASECAMP_CLIENT_SECRET,
                "redirect_uri": BASECAMP_REDIRECT_URI,
                "code": code.strip(),
            },
            timeout=30,
        )
        token_response.raise_for_status()
        token_data = token_response.json()

        access_token = token_data.get("access_token")
        if not access_token:
            return {
                "status": "error",
                "error": f"No access_token in response. Response was: {token_data}",
            }

        # Fetch account info to discover the account ID
        auth_headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "SEO Agent (your-email@example.com)",
        }
        auth_info_response = requests.get(
            "https://launchpad.37signals.com/authorization.json",
            headers=auth_headers,
            timeout=30,
        )
        auth_info_response.raise_for_status()
        auth_info = auth_info_response.json()

        accounts = auth_info.get("accounts", [])
        # Use the first Basecamp 3 account found
        bc3_accounts = [a for a in accounts if "basecamp3" in a.get("product", "").lower() or "3.basecamp" in a.get("href", "")]
        chosen_account = bc3_accounts[0] if bc3_accounts else (accounts[0] if accounts else None)
        account_id = str(chosen_account["id"]) if chosen_account else None

        # Persist to .env file
        env_path = Path(__file__).parent.parent / ".env"
        _update_env_file(env_path, access_token, account_id)

        # Activate in-memory so all tools work immediately without a restart
        BASECAMP_API_KEY = access_token
        if account_id:
            BASECAMP_ACCOUNT_ID = account_id
        _people_cache = {}  # Reset people cache so it reloads with new credentials

        return {
            "status": "success",
            "message": "Basecamp authentication successful! Token saved to .env and activated.",
            "accounts": [
                {"id": a.get("id"), "name": a.get("name"), "href": a.get("href")}
                for a in accounts
            ],
            "account_id_saved": account_id,
            "env_file_updated": str(env_path),
            "note": (
                "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID are now active. "
                "You can immediately use any Basecamp tool (get_basecamp_projects, etc.)."
            ),
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
        }


def _update_env_file(env_path: Path, access_token: str, account_id: Optional[str]) -> None:
    """Write BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID into the .env file."""
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    api_key_updated = False
    account_id_updated = False

    for i, line in enumerate(lines):
        if line.startswith("BASECAMP_API_KEY="):
            lines[i] = f"BASECAMP_API_KEY={access_token}"
            api_key_updated = True
        elif account_id and line.startswith("BASECAMP_ACCOUNT_ID="):
            lines[i] = f"BASECAMP_ACCOUNT_ID={account_id}"
            account_id_updated = True

    if not api_key_updated:
        lines.append(f"BASECAMP_API_KEY={access_token}")
    if account_id and not account_id_updated:
        lines.append(f"BASECAMP_ACCOUNT_ID={account_id}")

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_basecamp_todolist(
    project_id: int,
    name: str,
    description: str = "",
) -> Dict[str, Any]:
    """Create a new to-do list in a Basecamp project.

    Finds the project's todoset automatically and creates the list there.

    Args:
        project_id: Basecamp project ID (bucket ID)
        name: Name/title of the to-do list (required)
        description: Optional description (HTML supported)

    Returns: Dict with created todolist info
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        headers = _basecamp_headers()

        # Get the project to find the todoset
        project_url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/projects/{project_id}.json"
        )
        project_response = requests.get(project_url, headers=headers, timeout=30)
        project_response.raise_for_status()
        project = project_response.json()

        dock = project.get("dock", [])
        todoset_entry = next(
            (
                item
                for item in dock
                if item.get("name") == "todoset" and item.get("enabled")
            ),
            None,
        )

        if not todoset_entry:
            return {
                "status": "error",
                "error": "No To-dos tool found in this project. Enable it in Basecamp project settings.",
                "project_id": project_id,
            }

        # Get the todoset to find todolists_url
        todoset_url = todoset_entry.get("url")
        todoset_response = requests.get(todoset_url, headers=headers, timeout=30)
        todoset_response.raise_for_status()
        todoset = todoset_response.json()

        todolists_url = todoset.get("todolists_url")
        if not todolists_url:
            return {
                "status": "error",
                "error": "todolists_url not found on todoset resource.",
                "project_id": project_id,
            }

        payload: Dict[str, Any] = {"name": name}
        if description:
            payload["description"] = description

        response = requests.post(todolists_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        todolist = response.json()

        return {
            "status": "success",
            "todolist": {
                "id": todolist["id"],
                "name": todolist.get("title", ""),
                "description": todolist.get("description", ""),
                "todos_url": todolist.get("todos_url", ""),
                "groups_url": todolist.get("groups_url", ""),
                "url": todolist.get("app_url", ""),
                "created_at": todolist.get("created_at", ""),
            },
            "message": f"Created todolist: {name}",
            "project_id": project_id,
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "project_id": project_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "project_id": project_id,
        }


def update_basecamp_todolist(
    project_id: int,
    todolist_id: int,
    name: str,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Update an existing to-do list in a Basecamp project.

    Args:
        project_id: Basecamp project ID (bucket ID)
        todolist_id: ID of the todolist to update
        name: New name/title (required, cannot be blank)
        description: New description (HTML supported). Omitting clears the value.

    Returns: Dict with updated todolist info
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/"
            f"{project_id}/todolists/{todolist_id}.json"
        )
        headers = _basecamp_headers()

        payload: Dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description

        response = requests.put(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        todolist = response.json()

        return {
            "status": "success",
            "todolist": {
                "id": todolist["id"],
                "name": todolist.get("title", ""),
                "description": todolist.get("description", ""),
                "todos_url": todolist.get("todos_url", ""),
                "groups_url": todolist.get("groups_url", ""),
                "url": todolist.get("app_url", ""),
                "updated_at": todolist.get("updated_at", ""),
            },
            "message": "Todolist updated successfully",
            "project_id": project_id,
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "project_id": project_id,
            "todolist_id": todolist_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "project_id": project_id,
            "todolist_id": todolist_id,
        }


def get_basecamp_todolist_groups(
    project_id: int,
    todolist_id: int,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """Get to-do list groups (sections) within a Basecamp todolist.

    Groups are organizational sections within a to-do list that contain todos.

    Args:
        project_id: Basecamp project ID (bucket ID)
        todolist_id: ID of the todolist to get groups from
        status: Optional filter - 'archived' or 'trashed'

    Returns: Dict with groups list (id, title, position, todos_url)
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/"
            f"{project_id}/todolists/{todolist_id}/groups.json"
        )
        headers = _basecamp_headers()

        params = {}
        if status:
            params["status"] = status

        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        groups = response.json()

        return {
            "status": "success",
            "groups": [
                {
                    "id": g["id"],
                    "title": g.get("title", ""),
                    "status": g.get("status", "active"),
                    "position": g.get("position"),
                    "todos_url": g.get("todos_url", ""),
                    "group_position_url": g.get("group_position_url", ""),
                    "url": g.get("app_url", ""),
                    "created_at": g.get("created_at", ""),
                }
                for g in groups
            ],
            "count": len(groups),
            "project_id": project_id,
            "todolist_id": todolist_id,
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "project_id": project_id,
            "todolist_id": todolist_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "project_id": project_id,
            "todolist_id": todolist_id,
        }


def create_basecamp_todolist_group(
    project_id: int,
    todolist_id: int,
    name: str,
    color: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a to-do list group (section) within a Basecamp todolist.

    Groups act as sections/categories within a to-do list to organize todos.

    Args:
        project_id: Basecamp project ID (bucket ID)
        todolist_id: ID of the todolist to create the group in
        name: Name/title of the group (required)
        color: Optional color - one of: white, red, orange, yellow, green,
               blue, aqua, purple, gray, pink, brown

    Returns: Dict with created group info
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/"
            f"{project_id}/todolists/{todolist_id}/groups.json"
        )
        headers = _basecamp_headers()

        payload: Dict[str, Any] = {"name": name}
        if color:
            payload["color"] = color

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        group = response.json()

        return {
            "status": "success",
            "group": {
                "id": group["id"],
                "title": group.get("title", ""),
                "status": group.get("status", "active"),
                "position": group.get("position"),
                "todos_url": group.get("todos_url", ""),
                "group_position_url": group.get("group_position_url", ""),
                "url": group.get("app_url", ""),
                "created_at": group.get("created_at", ""),
            },
            "message": f"Created todolist group: {name}",
            "project_id": project_id,
            "todolist_id": todolist_id,
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "project_id": project_id,
            "todolist_id": todolist_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "project_id": project_id,
            "todolist_id": todolist_id,
        }


def update_basecamp_comment(
    project_id: int,
    comment_id: int,
    content: str,
) -> Dict[str, Any]:
    """Update an existing Basecamp comment."""
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/"
            f"{project_id}/comments/{comment_id}.json"
        )
        headers = _basecamp_headers()

        content = _replace_user_mentions(content)
        payload = {
            "content": content,
        }

        response = requests.put(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        comment = response.json()

        return {
            "status": "success",
            "comment": {
                "id": comment["id"],
                "content": comment.get("content", ""),
                "created_at": comment.get("created_at", ""),
                "updated_at": comment.get("updated_at", ""),
                "creator": comment.get("creator", {}).get("name"),
                "url": comment.get("app_url", ""),
            },
            "project_id": project_id,
            "comment_id": comment_id,
            "message": "Comment updated successfully",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "project_id": project_id,
            "comment_id": comment_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "project_id": project_id,
            "comment_id": comment_id,
        }


# ---------------------------------------------------------------------------
# Template Management
# ---------------------------------------------------------------------------


def get_basecamp_templates(
    status: str = "active",
) -> Dict[str, Any]:
    """Get all Basecamp project templates.

    Args:
        status: Filter by status — "active" (default), "archived", or "trashed"

    Returns: Dict with list of templates (id, name, description, status, url)
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/templates.json"
        headers = _basecamp_headers()
        params: Dict[str, str] = {}
        if status and status != "active":
            params["status"] = status

        all_templates: List[Dict[str, Any]] = []

        while url:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            templates = response.json() or []

            for t in templates:
                all_templates.append(
                    {
                        "id": t["id"],
                        "name": t.get("name", ""),
                        "description": t.get("description", ""),
                        "status": t.get("status", ""),
                        "url": t.get("app_url", ""),
                    }
                )

            url = _get_next_link(response.headers.get("Link"))
            params = {}  # params only on first request

        return {
            "status": "success",
            "templates": all_templates,
            "count": len(all_templates),
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
        }


def create_basecamp_template(
    name: str,
    description: str = "",
) -> Dict[str, Any]:
    """Create a new Basecamp project template.

    Args:
        name: Template name (required)
        description: Optional template description

    Returns: Dict with created template info (id, name, description, url)
    """
    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/templates.json"
        headers = _basecamp_headers()

        payload: Dict[str, Any] = {"name": name}
        if description:
            payload["description"] = description

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        template = response.json()

        return {
            "status": "success",
            "template": {
                "id": template["id"],
                "name": template.get("name", ""),
                "description": template.get("description", ""),
                "status": template.get("status", "active"),
                "url": template.get("app_url", ""),
                "created_at": template.get("created_at", ""),
            },
            "message": f"Created template: {name}",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
        }


def create_project_from_template(
    template_id: int,
    name: str,
    description: str = "",
) -> Dict[str, Any]:
    """Create a new Basecamp project from an existing template.

    Starts a project construction from a template and polls until complete
    (max ~30 seconds). The new project will contain all todolists, todos,
    and structure defined in the template.

    Args:
        template_id: ID of the template to use
        name: Name for the new project (required)
        description: Optional project description

    Returns: Dict with the newly created project info (id, name, url)
    """
    import time

    try:
        if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
            return {
                "status": "error",
                "error": "BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env file",
            }

        url = (
            f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}"
            f"/templates/{template_id}/project_constructions.json"
        )
        headers = _basecamp_headers()

        payload: Dict[str, Any] = {"project": {"name": name}}
        if description:
            payload["project"]["description"] = description

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        construction = response.json()

        # Poll for completion (max 30 attempts, 1 second apart)
        poll_url = construction.get("url")
        if not poll_url:
            return {
                "status": "success",
                "message": "Project construction started but no poll URL returned.",
                "construction": construction,
            }

        for _ in range(30):
            time.sleep(1)
            poll_resp = requests.get(poll_url, headers=headers, timeout=30)
            poll_resp.raise_for_status()
            result = poll_resp.json()

            if result.get("status") == "completed":
                project = result.get("project", {})
                return {
                    "status": "success",
                    "project": {
                        "id": project.get("id"),
                        "name": project.get("name", ""),
                        "description": project.get("description", ""),
                        "url": project.get("app_url", ""),
                    },
                    "template_id": template_id,
                    "message": f"Created project '{name}' from template {template_id}",
                }

        # Timed out waiting
        return {
            "status": "pending",
            "message": "Project construction is still in progress. Check Basecamp manually.",
            "template_id": template_id,
            "construction_id": construction.get("id"),
        }

    except requests.exceptions.RequestException as exc:
        return {
            "status": "error",
            "error": f"API request failed: {str(exc)}",
            "template_id": template_id,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "template_id": template_id,
        }
