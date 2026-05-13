"""Keyword Target Resource Tools

Provides lightweight access to the shared client keyword targeting list
stored in 'Client Kwds Targeting - Sheet1.json' at the project root.
"""
from pathlib import Path
from typing import Dict, Any, List
import json


ROOT_DIR = Path(__file__).resolve().parents[2]
TARGETS_PATH = ROOT_DIR / "Client Kwds Targeting - Sheet1.json"


def _load_keyword_targets() -> List[Dict[str, Any]]:
    """Load keyword target JSON into memory."""
    try:
        if not TARGETS_PATH.exists():
            return []

        data = json.loads(TARGETS_PATH.read_text(encoding='utf-8'))
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        return []


def list_keyword_targets() -> Dict[str, Any]:
    """Return all configured keyword targets for every client."""
    data = _load_keyword_targets()

    if not data:
        return {
            'status': 'error',
            'error': 'Keyword target resource not found or empty',
            'path': str(TARGETS_PATH)
        }

    return {
        'status': 'success',
        'client_count': len(data),
        'targets': data,
        'path': str(TARGETS_PATH)
    }


def get_client_keyword_targets(client: str) -> Dict[str, Any]:
    """Return keyword targets for a specific client name."""
    if not client:
        return {
            'status': 'error',
            'error': 'Client name is required'
        }

    data = _load_keyword_targets()
    if not data:
        return {
            'status': 'error',
            'error': 'Keyword target resource not found or empty',
            'path': str(TARGETS_PATH)
        }

    client_lower = client.strip().lower()
    matches = [
        entry for entry in data
        if entry.get('client', '').strip().lower() == client_lower
    ]

    if not matches:
        return {
            'status': 'error',
            'error': f'No keyword targets configured for client: {client}',
            'path': str(TARGETS_PATH)
        }

    return {
        'status': 'success',
        'client': client,
        'targets': matches[0].get('keywords', []),
        'url': matches[0].get('url', ''),
        'path': str(TARGETS_PATH)
    }
