"""Tests for GA4 field validation logic."""
from pathlib import Path

import pytest

from seo_agent.config import GA4_DIMENSION_METRIC_SHEET
from seo_agent.tools.ga4_tools import GA4FieldValidationError, validate_ga4_fields


def _require_sheet():
    """Skip tests when the GA4 catalog sheet is unavailable."""
    sheet_path = Path(GA4_DIMENSION_METRIC_SHEET)
    if not sheet_path.exists():
        pytest.skip(f"GA4 catalog sheet missing at {sheet_path}")


def test_validate_ga4_fields_accepts_known_fields():
    _require_sheet()
    # Known-good values pulled from the provided catalog sheet.
    validate_ga4_fields(
        metrics=['sessions', 'conversions'],
        dimensions=['sessionDefaultChannelGroup', 'sessionSource'],
    )


def test_validate_ga4_fields_rejects_unknown_fields():
    _require_sheet()
    with pytest.raises(GA4FieldValidationError):
        validate_ga4_fields(metrics=['totallyMadeUpMetric'], dimensions=['sessionSource'])


def test_validate_ga4_fields_rejects_unknown_dimensions():
    _require_sheet()
    with pytest.raises(GA4FieldValidationError):
        validate_ga4_fields(metrics=['sessions'], dimensions=['fakeDimension'])
