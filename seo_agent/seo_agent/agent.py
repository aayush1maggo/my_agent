"""SEO Agent - Multi-Agent System

This module maintains backward compatibility while leveraging the new multi-agent architecture.
The system consists of:
- Neo Coordinator (root agent)
- DataInsight (analytics specialist)
- KeywordMaster (keyword research specialist)
- TechAuditor (technical SEO specialist)
- DocManager (documentation & project management specialist)

For new code, import from .agents directly. This module provides legacy compatibility.
"""

# Import the multi-agent system
from .agents.coordinator import seo_coordinator
from .agents.analytics_agent import analytics_agent
from .agents.keyword_agent import keyword_agent
from .agents.technical_agent import technical_agent
from .agents.documentation_agent import documentation_agent
from .agents.local_seo_agent import local_seo_agent
from .agents.cro_agent import cro_agent
from .agents.basecamp_sequential_agent import basecamp_workflow_agent
from .agents.keyword_mapping_sequential_agent import keyword_mapping_workflow_agent
from .agents.guest_post_sequential_agent import guest_post_workflow_agent

# Main agent - now routes through the coordinator
seo_agent = seo_coordinator

# Backward compatibility alias
root_agent = seo_agent

# Export all agents for direct access if needed
__all__ = [
    'seo_agent',
    'root_agent',
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
]
