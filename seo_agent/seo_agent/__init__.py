"""SEO Agent - Multi-Agent AI-powered SEO analysis

This package now uses a multi-agent architecture:
- seo_agent/root_agent: Main coordinator (Neo)
- analytics_agent: DataInsight - GA4 and Search Console analytics
- keyword_agent: KeywordMaster - Keyword research and competitive analysis
- technical_agent: TechAuditor - Technical SEO and performance
- documentation_agent: DocManager - Reports and project management
- local_seo_agent: LocalCitation - Local SEO and citation planning
"""

# Import main agent (backward compatible)
from .agent import (
    seo_agent,
    root_agent,
    seo_coordinator,
    analytics_agent,
    keyword_agent,
    technical_agent,
    documentation_agent,
    local_seo_agent,
    cro_agent,
    basecamp_workflow_agent,
    keyword_mapping_workflow_agent,
    guest_post_workflow_agent,
)

from .config import (
    GOOGLE_API_KEY,
    SERPER_API_KEY,
    GA4_SCOPES,
    SEARCH_CONSOLE_SCOPES,
)

__version__ = '2.0.0'  # Updated for multi-agent architecture
__all__ = [
    # Main agents (backward compatible)
    'seo_agent',
    'root_agent',
    # Multi-agent system
    'seo_coordinator',
    'analytics_agent',
    'keyword_agent',
    'technical_agent',
    'documentation_agent',
    'local_seo_agent',
    'cro_agent',
    'basecamp_workflow_agent',
    'keyword_mapping_workflow_agent',
    'guest_post_workflow_agent',
    # Config
    'GOOGLE_API_KEY',
    'SERPER_API_KEY',
    'GA4_SCOPES',
    'SEARCH_CONSOLE_SCOPES',
]
