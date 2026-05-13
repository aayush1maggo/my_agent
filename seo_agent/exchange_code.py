"""Quick script to exchange Basecamp authorization code for access token"""
import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from seo_agent/.env
env_path = Path(__file__).parent / 'seo_agent' / '.env'
load_dotenv(dotenv_path=env_path)

BASECAMP_CLIENT_ID = os.getenv('BASECAMP_CLIENT_ID')
BASECAMP_CLIENT_SECRET = os.getenv('BASECAMP_CLIENT_SECRET')
BASECAMP_REDIRECT_URI = os.getenv('BASECAMP_REDIRECT_URI', 'http://localhost:8000/auth/callback')

# The code from your URL
CODE = "1609d66b"

print("\n🔄 Exchanging authorization code for access token...")
print(f"Code: {CODE}\n")

try:
    token_url = "https://launchpad.37signals.com/authorization/token"

    data = {
        'type': 'web_server',
        'client_id': BASECAMP_CLIENT_ID,
        'client_secret': BASECAMP_CLIENT_SECRET,
        'redirect_uri': BASECAMP_REDIRECT_URI,
        'code': CODE
    }

    response = requests.post(token_url, data=data, timeout=30)
    response.raise_for_status()

    token_data = response.json()

    # Save token to file
    with open('basecamp_token.json', 'w') as f:
        json.dump(token_data, f, indent=2)

    print("✓ Token saved to basecamp_token.json\n")

    # Get account info
    print("🔍 Fetching account information...\n")

    headers = {
        'Authorization': f'Bearer {token_data["access_token"]}',
        'User-Agent': os.getenv('USER_AGENT', 'Basecamp OAuth App')
    }

    auth_response = requests.get('https://launchpad.37signals.com/authorization.json', headers=headers, timeout=30)
    auth_response.raise_for_status()
    auth_info = auth_response.json()

    print("📋 Your Basecamp Accounts:")
    print("="*60)

    for account in auth_info.get('accounts', []):
        print(f"\n  Name: {account.get('name')}")
        print(f"  ID: {account.get('id')}")
        print(f"  URL: {account.get('href')}")

    if auth_info.get('accounts'):
        first_account_id = auth_info['accounts'][0]['id']
        print("\n" + "="*60)
        print("✅ Add these lines to seo_agent/.env:")
        print("="*60)
        print(f"\nBASECAMP_API_KEY={token_data['access_token']}")
        print(f"BASECAMP_ACCOUNT_ID={first_account_id}")
        print("\n")

except requests.exceptions.RequestException as e:
    print(f"❌ Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
