"""Tests for robots.txt analysis tools"""

from seo_agent.tools.robots_txt_tools import (
    analyze_robots_txt,
    get_robots_txt_summary,
)


class DummyResponse:
    """Simple stand-in for requests.Response used in tests."""

    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text


def test_analyze_robots_txt_allows_all(monkeypatch):
    """robots.txt with Allow-all rules should parse cleanly."""

    def fake_get(url, timeout=15):
        content = "User-agent: *\nDisallow:\n"
        return DummyResponse(200, content)

    monkeypatch.setattr(
        "seo_agent.tools.robots_txt_tools.requests.get",
        fake_get,
    )

    result = analyze_robots_txt("https://example.com/")
    assert result["status"] == "success"
    assert result["summary"]["has_wildcard_group"] is True
    assert result["summary"]["disallow_all_for_all_agents"] is False
    assert result["parsed"]["groups"]


def test_analyze_robots_txt_disallow_all(monkeypatch):
    """robots.txt that blocks all crawling should be flagged."""

    def fake_get(url, timeout=15):
        content = "User-agent: *\nDisallow: /\n"
        return DummyResponse(200, content)

    monkeypatch.setattr(
        "seo_agent.tools.robots_txt_tools.requests.get",
        fake_get,
    )

    result = analyze_robots_txt("example.com")
    assert result["status"] == "success"
    assert result["summary"]["disallow_all_for_all_agents"] is True
    assert any("blocks all crawling" in issue.lower() for issue in result["issues"])


def test_analyze_robots_txt_missing_file(monkeypatch):
    """404 robots.txt should be treated as missing, not a hard error."""

    def fake_get(url, timeout=15):
        return DummyResponse(404, "")

    monkeypatch.setattr(
        "seo_agent.tools.robots_txt_tools.requests.get",
        fake_get,
    )

    result = analyze_robots_txt("https://missing-robots.example")
    assert result["status"] == "missing"
    assert result["http_status"] == 404


def test_get_robots_txt_summary_basic(monkeypatch):
    """Summary function should expose key fields without full analysis."""

    def fake_get(url, timeout=15):
        content = (
            "User-agent: *\n"
            "Disallow: /admin\n"
            "Sitemap: https://example.com/sitemap.xml\n"
        )
        return DummyResponse(200, content)

    monkeypatch.setattr(
        "seo_agent.tools.robots_txt_tools.requests.get",
        fake_get,
    )

    result = get_robots_txt_summary("example.com/page")
    assert result["status"] == "success"
    assert result["has_wildcard_group"] is True
    assert result["group_count"] >= 1
    assert "https://example.com/sitemap.xml" in result["sitemaps"]
    assert "/admin" in result["sample_disallow"]

