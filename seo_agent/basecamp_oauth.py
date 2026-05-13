"""Basecamp OAuth Authentication Helper

This script helps you obtain a Basecamp OAuth access token.

Usage:
    python basecamp_oauth.py

This will:
1. Start a local web server on http://localhost:8000
2. Open your browser to authorize the app
3. Save the access token to basecamp_token.json
4. Display the account ID and token for you to add to .env
"""

import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from seo_agent/.env
env_path = Path(__file__).parent / 'seo_agent' / '.env'
load_dotenv(dotenv_path=env_path)

BASECAMP_CLIENT_ID = os.getenv('BASECAMP_CLIENT_ID')
BASECAMP_CLIENT_SECRET = os.getenv('BASECAMP_CLIENT_SECRET')
BASECAMP_REDIRECT_URI = os.getenv('BASECAMP_REDIRECT_URI', 'http://localhost:8000/auth/callback')

TOKEN_FILE = 'basecamp_token.json'

# Global variable to store the authorization code
auth_code = None
server_should_stop = False


class OAuthHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from Basecamp"""

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

    def do_GET(self):
        global auth_code, server_should_stop

        parsed_path = urlparse(self.path)

        if parsed_path.path == '/auth/callback':
            # Extract authorization code from callback
            query_params = parse_qs(parsed_path.query)

            if 'code' in query_params:
                auth_code = query_params['code'][0]

                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                success_html = """
                <html>
                <head><title>Basecamp OAuth Success</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: green;">✓ Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <script>setTimeout(function(){ window.close(); }, 3000);</script>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode())
                server_should_stop = True

            elif 'error' in query_params:
                error = query_params.get('error', ['Unknown error'])[0]

                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                error_html = f"""
                <html>
                <head><title>Basecamp OAuth Error</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">✗ Authorization Failed</h1>
                    <p>Error: {error}</p>
                    <p>Please close this window and try again.</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode())
                server_should_stop = True
        else:
            self.send_response(404)
            self.end_headers()


def get_authorization_url():
    """Generate Basecamp authorization URL"""
    auth_url = (
        f"https://launchpad.37signals.com/authorization/new?"
        f"type=web_server&"
        f"client_id={BASECAMP_CLIENT_ID}&"
        f"redirect_uri={BASECAMP_REDIRECT_URI}"
    )
    return auth_url


def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    token_url = "https://launchpad.37signals.com/authorization/token"

    data = {
        'type': 'web_server',
        'client_id': BASECAMP_CLIENT_ID,
        'client_secret': BASECAMP_CLIENT_SECRET,
        'redirect_uri': BASECAMP_REDIRECT_URI,
        'code': code
    }

    response = requests.post(token_url, data=data, timeout=30)
    response.raise_for_status()

    return response.json()


def get_authorization():
    """Get user authorization from Basecamp"""
    global auth_code, server_should_stop

    print("\n" + "="*60)
    print("Basecamp OAuth Authorization")
    print("="*60)

    # Validate configuration
    if not BASECAMP_CLIENT_ID or not BASECAMP_CLIENT_SECRET:
        print("\n❌ Error: BASECAMP_CLIENT_ID and BASECAMP_CLIENT_SECRET must be set in .env")
        print("\nCreate your OAuth app at: https://launchpad.37signals.com/integrations")
        return None

    print(f"\nClient ID: {BASECAMP_CLIENT_ID}")
    print(f"Redirect URI: {BASECAMP_REDIRECT_URI}")

    # Try multiple ports if 8000 is in use
    ports_to_try = [8000, 8080, 8888, 9000, 3000]
    httpd = None

    for port in ports_to_try:
        try:
            server_address = ('localhost', port)
            httpd = HTTPServer(server_address, OAuthHandler)
            print(f"\n✓ Started local server on port {port}")
            break
        except OSError:
            if port == ports_to_try[-1]:
                print(f"\n❌ Error: Could not start server on any port {ports_to_try}")
                print("Please close any applications using these ports and try again.")
                return None
            continue

    if not httpd:
        return None

    print("\n📝 Opening browser for authorization...")
    print("   Please authorize the application in your browser.\n")

    # Open browser
    auth_url = get_authorization_url()
    webbrowser.open(auth_url)

    # Wait for callback
    print("⏳ Waiting for authorization callback...")

    while not server_should_stop:
        httpd.handle_request()

    httpd.server_close()

    if auth_code:
        print("\n✓ Authorization code received!")
        return auth_code
    else:
        print("\n❌ Authorization failed or was cancelled.")
        return None


def main():
    """Main OAuth flow"""
    print("\n🚀 Basecamp OAuth Token Generator")
    print("="*60)

    # Step 1: Get authorization
    code = get_authorization()

    if not code:
        print("\n❌ Failed to get authorization code.")
        return

    # Step 2: Exchange code for token
    print("\n🔄 Exchanging authorization code for access token...")

    try:
        token_data = exchange_code_for_token(code)

        # Save token to file
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)

        print(f"\n✓ Token saved to {TOKEN_FILE}")

        # Display token information
        print("\n" + "="*60)
        print("✅ SUCCESS! Add these to your .env file:")
        print("="*60)
        print(f"\nBASECAMP_API_KEY={token_data['access_token']}")
        print(f"BASECAMP_ACCOUNT_ID=<your_account_id>")

        # Get account info
        print("\n🔍 Fetching account information...")

        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
            'User-Agent': os.getenv('USER_AGENT', 'Basecamp OAuth App')
        }

        auth_response = requests.get('https://launchpad.37signals.com/authorization.json', headers=headers, timeout=30)
        auth_response.raise_for_status()
        auth_info = auth_response.json()

        print("\n📋 Your Basecamp Accounts:")
        print("="*60)

        for account in auth_info.get('accounts', []):
            print(f"\n  Name: {account.get('name')}")
            print(f"  ID: {account.get('id')}")
            print(f"  URL: {account.get('href')}")

        if auth_info.get('accounts'):
            first_account_id = auth_info['accounts'][0]['id']
            print("\n" + "="*60)
            print("✅ Add this to your .env file:")
            print("="*60)
            print(f"\nBASECAMP_API_KEY={token_data['access_token']}")
            print(f"BASECAMP_ACCOUNT_ID={first_account_id}")
            print("\n")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error exchanging code for token: {e}")
        return
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return


if __name__ == '__main__':
    main()
