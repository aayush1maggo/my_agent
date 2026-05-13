"""Tests for multi-agent system architecture"""
import pytest
from seo_agent import (
    seo_agent,
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


class TestAgentImports:
    """Test that all agents can be imported correctly"""

    def test_import_main_agent(self):
        """Test that main seo_agent can be imported"""
        assert seo_agent is not None
        assert seo_agent.name == 'neo_coordinator'

    def test_import_coordinator(self):
        """Test that coordinator can be imported"""
        assert seo_coordinator is not None
        assert seo_coordinator.name == 'neo_coordinator'

    def test_import_analytics_agent(self):
        """Test that analytics agent can be imported"""
        assert analytics_agent is not None
        assert analytics_agent.name == 'data_insight'

    def test_import_keyword_agent(self):
        """Test that keyword agent can be imported"""
        assert keyword_agent is not None
        assert keyword_agent.name == 'keyword_master'

    def test_import_technical_agent(self):
        """Test that technical agent can be imported"""
        assert technical_agent is not None
        assert technical_agent.name == 'tech_auditor'

    def test_import_documentation_agent(self):
        """Test that documentation agent can be imported"""
        assert documentation_agent is not None
        assert documentation_agent.name == 'doc_manager'

    def test_import_local_seo_agent(self):
        """Test that local SEO agent can be imported"""
        assert local_seo_agent is not None
        assert local_seo_agent.name == 'local_citation'

    def test_import_cro_agent(self):
        """Test that CRO agent can be imported"""
        assert cro_agent is not None
        assert cro_agent.name == 'conversion_optimizer'

    def test_import_keyword_mapping_workflow_agent(self):
        """Test that keyword mapping workflow agent can be imported"""
        assert keyword_mapping_workflow_agent is not None
        assert keyword_mapping_workflow_agent.name == 'keyword_mapping_workflow'

    def test_import_guest_post_workflow_agent(self):
        """Test that guest post workflow agent can be imported"""
        assert guest_post_workflow_agent is not None
        assert guest_post_workflow_agent.name == 'guest_post_workflow'


class TestAgentStructure:
    """Test the structure of the multi-agent system"""

    def test_coordinator_has_sub_agents(self):
        """Test that coordinator has 9 sub-agents"""
        assert hasattr(seo_coordinator, 'sub_agents')
        assert len(seo_coordinator.sub_agents) == 9

    def test_coordinator_has_minimal_tools(self):
        """Test that coordinator only has utility tools"""
        # Coordinator should have minimal tools (just datetime utilities)
        assert hasattr(seo_coordinator, 'tools')
        # 3 utility tools
        assert len(seo_coordinator.tools) == 3

    def test_analytics_agent_tool_count(self):
        """Test that analytics agent has correct number of tools"""
        # Datetime: 1, GA4 core: 4, GA4 viz: 2, Search Console: 7, Sheets: 10, Content extraction: 4, Exploratory analysis: 3 = 31 total
        assert len(analytics_agent.tools) == 31

    def test_keyword_agent_tool_count(self):
        """Test that keyword agent has correct number of tools"""
        # Skills: 1, Datetime: 1, Serper: 4, SEMrush Keywords: 6, Keyword targets: 2, SEMrush Backlinks: 7,
        # Content extraction: 4, Browser tools: 2, Competitor content brief: 2 = 29 total
        assert len(keyword_agent.tools) == 29

    def test_technical_agent_tool_count(self):
        """Test that technical agent has correct number of tools"""
        # Datetime: 1, Sitemap: 2, robots.txt: 2, Content extraction: 4,
        # Browser tools: 8, Screaming Frog: 2 = 19 total
        assert len(technical_agent.tools) == 19

    def test_documentation_agent_tool_count(self):
        """Test that documentation agent has correct number of tools"""
        # Datetime: 1, Docs: 8, Slides: 14, Sheets: 10, Basecamp: 9, Structured summary: 1, Keyword targets: 2, Content extraction: 4 = 49 total
        assert len(documentation_agent.tools) == 49

    def test_local_seo_agent_tool_count(self):
        """Test that local SEO agent has correct number of tools"""
        # HTML form inspector: 1, fetch_page_content: 1 = 2 total
        assert len(local_seo_agent.tools) == 2

    def test_cro_agent_tool_count(self):
        """Test that CRO agent has correct number of tools"""
        # CRO: datetime: 1, GA4: 4, Search Console: 7, Sheets: 10, Form inspector: 1,
        # Browser tools: 2 (fetch_page_content, extract_all_links) = 25 total
        assert len(cro_agent.tools) == 25

    def test_basecamp_workflow_agent_sub_agents(self):
        """Test that Basecamp workflow agent chains DocManager and KeywordMaster"""
        assert hasattr(basecamp_workflow_agent, 'sub_agents')
        sub_names = [agent.name for agent in basecamp_workflow_agent.sub_agents]
        assert sub_names == ['basecamp_doc_manager', 'basecamp_keyword_master']

    def test_keyword_mapping_workflow_agent_sub_agents(self):
        """Test that keyword mapping workflow chains KeywordMaster and DocManager clones"""
        assert hasattr(keyword_mapping_workflow_agent, 'sub_agents')
        sub_names = [agent.name for agent in keyword_mapping_workflow_agent.sub_agents]
        assert sub_names == ['keyword_mapping_researcher', 'keyword_mapping_doc_manager']

    def test_guest_post_workflow_agent_sub_agents(self):
        """Test that guest post workflow chains KeywordMaster, DataInsight, and DocManager clones"""
        assert hasattr(guest_post_workflow_agent, 'sub_agents')
        sub_names = [agent.name for agent in guest_post_workflow_agent.sub_agents]
        assert sub_names == [
            'guest_post_keyword_master',
            'guest_post_search_console',
            'guest_post_doc_manager',
        ]


class TestAgentDescriptions:
    """Test that agents have proper descriptions for routing"""

    def test_coordinator_description(self):
        """Test coordinator has routing description"""
        assert seo_coordinator.description is not None
        assert 'coordinator' in seo_coordinator.description.lower() or 'neo' in seo_coordinator.description.lower()

    def test_analytics_agent_description(self):
        """Test analytics agent has clear domain description"""
        desc = analytics_agent.description.lower()
        assert 'analytics' in desc or 'ga4' in desc or 'search console' in desc

    def test_keyword_agent_description(self):
        """Test keyword agent has clear domain description"""
        desc = keyword_agent.description.lower()
        assert 'keyword' in desc or 'research' in desc or 'ranking' in desc

    def test_technical_agent_description(self):
        """Test technical agent has clear domain description"""
        desc = technical_agent.description.lower()
        assert 'technical' in desc or 'performance' in desc or 'sitemap' in desc

    def test_documentation_agent_description(self):
        """Test documentation agent has clear domain description"""
        desc = documentation_agent.description.lower()
        assert 'doc' in desc or 'report' in desc or 'project' in desc

    def test_local_seo_agent_description(self):
        """Test local SEO agent has clear domain description"""
        desc = local_seo_agent.description.lower()
        assert 'local' in desc or 'citation' in desc


class TestBackwardCompatibility:
    """Test backward compatibility with old import patterns"""

    def test_seo_agent_is_coordinator(self):
        """Test that seo_agent is the coordinator"""
        assert seo_agent is seo_coordinator

    def test_old_import_pattern_works(self):
        """Test that old import pattern still works"""
        from seo_agent import seo_agent, root_agent
        assert seo_agent is not None
        assert root_agent is not None
        assert seo_agent is root_agent


class TestAgentNames:
    """Test that agent names are unique and correct"""

    def test_unique_agent_names(self):
        """Test that all agent names are unique"""
        names = [
            seo_coordinator.name,
            analytics_agent.name,
            keyword_agent.name,
            technical_agent.name,
            documentation_agent.name,
            local_seo_agent.name,
            cro_agent.name,
            basecamp_workflow_agent.name,
            keyword_mapping_workflow_agent.name,
        ]
        assert len(names) == len(set(names)), "Agent names must be unique"

    def test_coordinator_name(self):
        """Test coordinator has correct name"""
        assert seo_coordinator.name == 'neo_coordinator'

    def test_specialist_names(self):
        """Test specialists have correct names"""
        assert analytics_agent.name == 'data_insight'
        assert keyword_agent.name == 'keyword_master'
        assert technical_agent.name == 'tech_auditor'
        assert documentation_agent.name == 'doc_manager'
        assert local_seo_agent.name == 'local_citation'
        assert cro_agent.name == 'conversion_optimizer'
        assert basecamp_workflow_agent.name == 'basecamp_workflow'
        assert keyword_mapping_workflow_agent.name == 'keyword_mapping_workflow'


class TestAgentInstructions:
    """Test that agents have appropriate instructions"""

    def test_all_agents_have_instructions(self):
        """Test that all LlmAgents have non-empty instructions"""
        # Note: SequentialAgents (basecamp_workflow_agent, keyword_mapping_workflow_agent,
        # guest_post_workflow_agent) do not have an 'instruction' attribute — only LlmAgents do.
        llm_agents = [
            seo_coordinator,
            analytics_agent,
            keyword_agent,
            technical_agent,
            documentation_agent,
            local_seo_agent,
            cro_agent,
        ]
        for agent in llm_agents:
            assert hasattr(agent, 'instruction'), f"{agent.name} missing instruction"
            assert agent.instruction is not None
            assert len(agent.instruction) > 0

    def test_coordinator_mentions_transfer(self):
        """Test that coordinator instruction mentions agent transfer"""
        instruction = seo_coordinator.instruction.lower()
        assert 'transfer' in instruction or 'delegate' in instruction


# Note: Integration tests that actually run the agents would require:
# - Valid OAuth credentials
# - API keys
# - MCP server connections
# These should be run separately in a configured environment

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
