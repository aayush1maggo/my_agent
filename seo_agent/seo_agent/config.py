"""Configuration management for SEO Agent"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY', '25293b2a30a699a5fadd7279f32a5b2e9e64e6c0')
SEMRUSH_API_KEY = os.getenv('SEMRUSH_API_KEY')

# Basecamp API Configuration (Direct API, not MCP)
BASECAMP_API_KEY = os.getenv('BASECAMP_API_KEY')
BASECAMP_ACCOUNT_ID = os.getenv('BASECAMP_ACCOUNT_ID')

# Basecamp OAuth Configuration (for getting access token)
BASECAMP_CLIENT_ID = os.getenv('BASECAMP_CLIENT_ID')
BASECAMP_CLIENT_SECRET = os.getenv('BASECAMP_CLIENT_SECRET')
BASECAMP_REDIRECT_URI = os.getenv('BASECAMP_REDIRECT_URI', 'http://localhost:8000/auth/callback')

# OAuth credentials file path
CREDENTIALS_FILE = os.getenv('GOOGLE_OAUTH_CREDENTIALS', 'credentials.json')
TOKEN_FILE = os.getenv('GOOGLE_OAUTH_TOKEN', 'token.json')

# GA4 metadata source (used to validate dimensions/metrics)
GA4_DIMENSION_METRIC_SHEET = Path(
    os.getenv(
        'GA4_DIMENSION_METRIC_SHEET',
        r'c:\Users\hp\Downloads\GA4 Dimensions and Metrics API - Sheet1.csv'
    )
)

# OAuth Scopes
GA4_SCOPES = [
    'https://www.googleapis.com/auth/analytics.readonly'
]

SEARCH_CONSOLE_SCOPES = [
    'https://www.googleapis.com/auth/webmasters.readonly'
]

GOOGLE_DOCS_SCOPES = [
    'https://www.googleapis.com/auth/documents',  # Read and write documents
    'https://www.googleapis.com/auth/drive.readonly'  # List documents
]

GOOGLE_SHEETS_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',  # Read and write spreadsheets
    'https://www.googleapis.com/auth/drive.readonly'  # List spreadsheets (already in Docs)
]

GOOGLE_SLIDES_SCOPES = [
    'https://www.googleapis.com/auth/presentations',  # Read and write presentations
    'https://www.googleapis.com/auth/drive.readonly'  # List presentations (already in Docs)
]

ALL_SCOPES = GA4_SCOPES + SEARCH_CONSOLE_SCOPES + GOOGLE_DOCS_SCOPES + GOOGLE_SHEETS_SCOPES + GOOGLE_SLIDES_SCOPES

# Serper.dev configuration (used for rank tracking tools)
SERPER_URL = "https://google.serper.dev/search"

# DataForSEO configuration (used for competitor content brief SERP lookups)
DATAFORSEO_LOGIN = os.getenv('DATAFORSEO_LOGIN', '')
DATAFORSEO_PASSWORD = os.getenv('DATAFORSEO_PASSWORD', '')
DATAFORSEO_SERP_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"

# Everhour API configuration (timesheet management)
EVERHOUR_API_KEY = os.getenv('EVERHOUR_API_KEY', '')
EVERHOUR_BASE_URL = "https://api.everhour.com"

# DataForSEO location codes reference CSV (maps location names/ISO codes → integer codes)
DATAFORSEO_LOCATION_CODES_CSV = Path(
    os.getenv('DATAFORSEO_LOCATION_CODES_CSV', r'c:\Users\hp\code\adk_agents\location_codes.csv')
)

# MCP Server Configuration (DEPRECATED - keeping for reference)
# Note: MCP toolsets were removed due to token explosion (37k+ tokens)
# Now using direct API calls for Basecamp instead
#
# # Basecamp MCP Server (DEPRECATED)
# MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'https://basecamp-mcp-server-by-aayush.fastmcp.app/mcp')
# MCP_SERVER_NAME = os.getenv('MCP_SERVER_NAME', 'basecamp')
# MCP_AUTH_TOKEN = os.getenv('MCP_AUTH_TOKEN')
#
# # SEMrush MCP Server (DEPRECATED)
# SEMRUSH_MCP_URL = os.getenv('SEMRUSH_MCP_URL', 'https://mcp.semrush.com/v1/mcp')
# SEMRUSH_MCP_NAME = os.getenv('SEMRUSH_MCP_NAME', 'semrush')
#
# # Chrome DevTools MCP Server (REMOVED)
# CHROME_DEVTOOLS_MCP_NAME = os.getenv('CHROME_DEVTOOLS_MCP_NAME', 'chrome-devtools')
# CHROME_DEVTOOLS_COMMAND = os.getenv('CHROME_DEVTOOLS_COMMAND', 'npx')
# CHROME_DEVTOOLS_ARGS = ['chrome-devtools-mcp@latest']

# ADK Configuration
USE_VERTEX_AI = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '0') == '1'
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemini-3-flash-preview')

# Screaming Frog CLI configuration
SCREAMING_FROG_CLI_PATH = os.getenv(
    'SCREAMING_FROG_CLI_PATH',
    r'C:\Program Files (x86)\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe'
)
SCREAMING_FROG_OUTPUT_DIR = Path(
    os.getenv('SCREAMING_FROG_OUTPUT_DIR', 'analysis_charts/screaming_frog_reports')
).resolve()
