"""Lightweight HTML form inspection tools for citation sites.

These tools use plain HTTP + HTML parsing (no real browser) to give the
LocalCitation agent a view of form fields without the complexity of a
full browser automation stack.

They are intended for understanding field names/labels only; all actual
submission, logins, and CAPTCHAs remain human-controlled.
"""
from typing import Dict, Any, List

import requests
from bs4 import BeautifulSoup


def inspect_form_fields(url: str) -> Dict[str, Any]:
    """Inspect HTML form fields on a given URL.

    Args:
        url: Page URL that contains the form (e.g., an "add listing" page).

    Returns:
        Dict with status, url, and a list of detected fields with basic metadata.
    """
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Build a simple label lookup: for -> text
        labels = {}
        for label in soup.find_all("label"):
            lab_for = label.get("for")
            if not lab_for:
                continue
            text = label.get_text(strip=True)
            if text:
                labels[lab_for] = text

        fields: List[Dict[str, Any]] = []

        # Inspect input fields
        for inp in soup.find_all("input"):
            field_type = (inp.get("type") or "text").lower()
            if field_type in {"hidden", "submit", "button", "image"}:
                continue

            name = inp.get("name") or ""
            field_id = inp.get("id") or ""
            placeholder = inp.get("placeholder") or ""
            label = labels.get(field_id, "")

            fields.append(
                {
                    "tag": "input",
                    "type": field_type,
                    "name": name,
                    "id": field_id,
                    "label": label,
                    "placeholder": placeholder,
                }
            )

        # Inspect textareas
        for ta in soup.find_all("textarea"):
            name = ta.get("name") or ""
            field_id = ta.get("id") or ""
            placeholder = ta.get("placeholder") or ""
            label = labels.get(field_id, "")

            fields.append(
                {
                    "tag": "textarea",
                    "type": "textarea",
                    "name": name,
                    "id": field_id,
                    "label": label,
                    "placeholder": placeholder,
                }
            )

        # Inspect selects
        for sel in soup.find_all("select"):
            name = sel.get("name") or ""
            field_id = sel.get("id") or ""
            label = labels.get(field_id, "")

            options = [
                opt.get_text(strip=True)
                for opt in sel.find_all("option")
                if opt.get_text(strip=True)
            ]

            fields.append(
                {
                    "tag": "select",
                    "type": "select",
                    "name": name,
                    "id": field_id,
                    "label": label,
                    "options": options,
                }
            )

        return {
            "status": "success",
            "url": url,
            "field_count": len(fields),
            "fields": fields,
            "note": (
                "Form fields inspected via static HTML. JavaScript-rendered "
                "fields may not appear. Use this as a guide for mapping your "
                "business data to field names."
            ),
        }

    except requests.RequestException as exc:
        return {
            "status": "error",
            "error": f"HTTP error: {str(exc)}",
            "url": url,
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "status": "error",
            "error": str(exc),
            "url": url,
        }

