# SEO Agent

An intelligent **multi-agent** SEO system built with Google's Agent Development Kit (ADK) that integrates Google Analytics 4, Google Search Console, and Serper.dev for comprehensive SEO analysis and keyword tracking.

> **🎉 Version 2.0** - Now uses a multi-agent architecture with specialized agents for analytics, keyword research, technical SEO, and documentation! See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details. All existing code remains backward compatible.

## Features

### Date & Time Utilities
- Get current date and time in multiple formats
- Calculate date ranges for API queries
- Parse relative dates ('30daysAgo', 'yesterday', etc.)
- Generate period-over-period comparison dates
- Support for various timezones

### Google Analytics 4 Integration
- Fetch traffic metrics (users, sessions, page views, bounce rate, etc.)
- Analyze page performance and identify high/low performers
- Track traffic sources and channel performance
- Analyze trends over time with intelligent insights

### Google Search Console Integration
- Analyze search queries and their performance (clicks, impressions, CTR, position)
- Evaluate page-level search performance
- Compare performance across different time periods
- Identify SEO opportunities:
  - High impressions + low CTR queries
  - Near page 1 rankings (positions 11-20)
  - Good position but low clicks

### Live Keyword Ranking (Serper.dev)
- Check current rankings for specific keywords
- Batch keyword ranking checks
- Analyze SERP features (featured snippets, PAA, knowledge graphs, etc.)
- Competitive analysis across multiple domains
- SERP feature recommendations

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up OAuth credentials for Google APIs:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Analytics Data API and Google Search Console API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download credentials as `credentials.json` and place in project root

3. Configure environment variables:
   - Copy `.env.example` to `seo_agent/.env`
   - Update with your API keys

## Configuration

Edit `seo_agent/.env`:

```env
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your_google_api_key

# Serper.dev API Key
SERPER_API_KEY=your_serper_api_key

# OAuth Credentials
GOOGLE_OAUTH_CREDENTIALS=credentials.json
GOOGLE_OAUTH_TOKEN=token.json
```

## Usage

### Running the Agent

```python
from seo_agent import seo_agent

# The agent will handle OAuth authentication on first run
# It will open a browser for you to authorize the application

# Start the agent
response = seo_agent.run("Analyze the SEO performance for my website")
```

### Example Queries

#### GA4 Analytics
```python
# Get GA4 metrics
seo_agent.run("Get GA4 metrics for property 123456789 for the last 30 days")

# Analyze page performance
seo_agent.run("Show me the top performing pages in GA4 for property 123456789")

# Traffic sources analysis
seo_agent.run("Analyze traffic sources for GA4 property 123456789")

# Trend analysis
seo_agent.run("Analyze sessions trend for property 123456789 over the last 60 days")
```

#### Search Console
```python
# Get search queries
seo_agent.run("Show me top search queries for https://example.com")

# Page performance
seo_agent.run("Analyze page performance in Search Console for https://example.com")

# Find SEO opportunities
seo_agent.run("Find SEO opportunities for https://example.com")

# Compare periods
seo_agent.run("""
Compare Search Console performance for https://example.com:
Current: 2024-01-01 to 2024-01-31
Previous: 2023-12-01 to 2023-12-31
""")
```

#### Keyword Ranking (Serper.dev)
```python
# Check single keyword ranking
seo_agent.run("What's the current ranking for 'python tutorial' for example.com?")

# Batch check rankings
seo_agent.run("""
Check rankings for example.com for these keywords:
- python tutorial
- web development
- seo optimization
""")

# Analyze SERP features
seo_agent.run("Analyze SERP features for 'machine learning'")

# Competitive analysis
seo_agent.run("""
Compare rankings for keywords ['seo tools', 'seo analysis']
across domains: example.com, competitor1.com, competitor2.com
""")
```

### Direct Tool Usage

You can also use the tools directly:

```python
from seo_agent.tools import (
    get_ga4_metrics,
    get_search_console_queries,
    get_keyword_ranking
)

# GA4 metrics
metrics = get_ga4_metrics(
    property_id='123456789',
    start_date='30daysAgo',
    end_date='today'
)

# Search Console queries
queries = get_search_console_queries(
    site_url='https://example.com',
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# Keyword ranking
ranking = get_keyword_ranking(
    keyword='python tutorial',
    target_domain='example.com',
    location='us'
)
```

## Authentication Flow

On first run, the agent will:
1. Check for existing OAuth tokens
2. If not found, initiate OAuth flow
3. Open browser for Google authorization
4. Save token for future use

The token is saved in `token.json` and will be automatically refreshed when expired.

## Available Tools

### Utility Tools
- `get_current_datetime` - Get current date/time with multiple formats
- `calculate_date_range` - Calculate date ranges for queries
- `parse_relative_date` - Convert relative to absolute dates
- `get_time_period_comparison_dates` - Get dates for period comparison

### GA4 Tools
- `get_ga4_metrics` - Fetch GA4 metrics with custom dimensions
- `get_ga4_page_performance` - Analyze page-level performance
- `get_ga4_traffic_sources` - Analyze traffic sources
- `analyze_ga4_trends` - Trend analysis for metrics

### Search Console Tools
- `get_search_console_raw` - Fetch raw performance rows for custom dimensions
- `get_search_console_queries` - Fetch query performance
- `get_search_console_pages` - Fetch page performance
- `get_search_console_performance` - Multi-dimension analysis
- `analyze_search_opportunities` - Identify quick wins
- `compare_periods` - Period-over-period comparison
- `get_keyword_landing_pages` - Map keywords to landing pages with metrics

### Serper Tools
- `get_keyword_ranking` - Single keyword ranking
- `batch_keyword_rankings` - Multiple keyword rankings
- `analyze_serp_features` - SERP feature analysis
- `compare_rankings` - Multi-domain comparison

## Data Formats

### GA4 Property ID
- Format: `properties/123456789` or just `123456789`
- Find it in GA4: Admin > Property Settings

### Search Console Site URL
- Format: Full URL like `https://example.com`
- Must match property in Search Console exactly

### Dates
- Absolute: `YYYY-MM-DD` (e.g., `2024-01-15`)
- Relative: `NdaysAgo` (e.g., `30daysAgo`, `7daysAgo`)
- Today: `today`
- Yesterday: `yesterday`

## Tips for Best Results

1. **Be Specific**: Provide property IDs, site URLs, and date ranges
2. **Ask for Insights**: The agent provides analysis, not just raw data
3. **Compare Periods**: Use period comparison to track progress
4. **Check Opportunities**: Regularly run opportunity analysis
5. **Monitor Trends**: Use trend analysis to catch issues early

## Troubleshooting

### OAuth Issues
- Delete `token.json` and re-authenticate
- Ensure credentials.json is in the correct location
- Check that APIs are enabled in Google Cloud Console

### API Rate Limits
- GA4: 25,000 requests per day
- Search Console: 600 requests per minute
- Serper.dev: Check your plan limits

### Common Errors
- **Property not found**: Check property ID format
- **Insufficient permissions**: Ensure OAuth user has proper access
- **No data returned**: Check date ranges and property settings

## Project Structure

```
seo_agent/
├── seo_agent/
│   ├── __init__.py
│   ├── agent.py          # Main agent definition
│   ├── auth.py           # OAuth authentication
│   ├── config.py         # Configuration management
│   ├── .env              # Environment variables
│   └── tools/
│       ├── __init__.py
│       ├── ga4_tools.py          # GA4 integration
│       ├── search_console_tools.py  # Search Console integration
│       └── serper_tools.py       # Serper.dev integration
├── requirements.txt
├── README.md
└── credentials.json      # OAuth credentials (not in repo)
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [GA4 Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Search Console API](https://developers.google.com/webmaster-tools)
- [Serper.dev Documentation](https://serper.dev/docs)
