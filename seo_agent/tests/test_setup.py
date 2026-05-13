"""
Test script to verify SEO Agent setup
Run this to check if all components are properly configured
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import sys
from pathlib import Path


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)


def check_dependencies():
    """Check if all required packages are installed"""
    print_section("Checking Dependencies")

    required_packages = [
        'google.adk',
        'google.auth',
        'google_auth_oauthlib',
        'google.analytics.data_v1beta',
        'googleapiclient',
        'requests',
        'dotenv'
    ]

    all_good = True
    for package in required_packages:
        try:
            __import__(package.replace('.', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_good = False

    return all_good


def check_environment():
    """Check environment variables"""
    print_section("Checking Environment Variables")

    from seo_agent import config

    checks = {
        'GOOGLE_API_KEY': config.GOOGLE_API_KEY,
        'SERPER_API_KEY': config.SERPER_API_KEY,
        'CREDENTIALS_FILE': config.CREDENTIALS_FILE,
        'TOKEN_FILE': config.TOKEN_FILE,
    }

    all_good = True
    for name, value in checks.items():
        if value:
            print(f"✓ {name} is set")
        else:
            print(f"✗ {name} - NOT SET")
            all_good = False

    return all_good


def check_credentials_file():
    """Check if OAuth credentials file exists"""
    print_section("Checking OAuth Credentials")

    from seo_agent import config

    cred_path = Path(config.CREDENTIALS_FILE)
    if cred_path.exists():
        print(f"✓ credentials.json found at: {cred_path}")
        return True
    else:
        print(f"✗ credentials.json NOT FOUND at: {cred_path}")
        print("  Download from Google Cloud Console")
        return False


def check_oauth_token():
    """Check if OAuth token exists"""
    from seo_agent import config

    token_path = Path(config.TOKEN_FILE)
    if token_path.exists():
        print(f"✓ token.json found (already authenticated)")
        return True
    else:
        print(f"⚠ token.json not found (will authenticate on first run)")
        return True  # Not an error, just info


def test_serper():
    """Test Serper.dev connection"""
    print_section("Testing Serper.dev Connection")

    try:
        from seo_agent.tools.serper_tools import get_keyword_ranking

        result = get_keyword_ranking(
            keyword='test',
            target_domain='example.com',
            location='us',
            num_results=10
        )

        if 'error' in result:
            print(f"✗ Serper API Error: {result['error']}")
            return False
        else:
            print(f"✓ Serper API working")
            print(f"  Test query returned {len(result.get('top_results', []))} results")
            return True

    except Exception as e:
        print(f"✗ Serper test failed: {str(e)}")
        return False


def test_oauth_ready():
    """Test if OAuth is ready (doesn't trigger auth flow)"""
    print_section("Checking OAuth Setup")

    try:
        from seo_agent.auth import auth_manager
        import os

        if os.path.exists(auth_manager.token_file):
            print("✓ OAuth token exists")
            try:
                creds = auth_manager.get_credentials()
                print("✓ OAuth credentials are valid")
                return True
            except Exception as e:
                print(f"⚠ OAuth credentials need refresh: {str(e)}")
                return False
        else:
            print("⚠ OAuth not yet configured (will prompt on first use)")
            return True  # Not an error

    except Exception as e:
        print(f"✗ OAuth check failed: {str(e)}")
        return False


def test_agent_load():
    """Test if agent can be loaded"""
    print_section("Testing Agent Load")

    try:
        from seo_agent import seo_agent
        print(f"✓ Agent loaded successfully")
        print(f"  Agent name: {seo_agent.name}")
        print(f"  Model: {seo_agent.model}")
        print(f"  Number of tools: {len(seo_agent.tools)}")
        return True
    except Exception as e:
        print(f"✗ Failed to load agent: {str(e)}")
        return False


def print_tool_summary():
    """Print summary of available tools"""
    print_section("Available Tools")

    try:
        from seo_agent import seo_agent

        print("\nGA4 Tools:")
        print("  - get_ga4_metrics")
        print("  - get_ga4_page_performance")
        print("  - get_ga4_traffic_sources")
        print("  - analyze_ga4_trends")

        print("\nSearch Console Tools:")
        print("  - get_search_console_raw")
        print("  - get_search_console_queries")
        print("  - get_search_console_pages")
        print("  - get_search_console_performance")
        print("  - analyze_search_opportunities")
        print("  - compare_periods")
        print("  - get_keyword_landing_pages")

        print("\nSerper Tools:")
        print("  - get_keyword_ranking")
        print("  - batch_keyword_rankings")
        print("  - analyze_serp_features")
        print("  - compare_rankings")

    except Exception as e:
        print(f"Could not load tools: {str(e)}")


def print_next_steps(results):
    """Print next steps based on test results"""
    print_section("Next Steps")

    if all(results.values()):
        print("✓ All checks passed! You're ready to use the SEO Agent.")
        print("\nTry running:")
        print("  python run_agent.py")
        print("\nOr in Python:")
        print("  from seo_agent import seo_agent")
        print("  seo_agent.run('Check ranking for example.com')")
    else:
        print("Some checks failed. Please address the issues above.")
        print("\nCommon fixes:")

        if not results['dependencies']:
            print("  - Run: pip install -r requirements.txt")

        if not results['environment']:
            print("  - Update seo_agent/.env with your API keys")

        if not results['credentials']:
            print("  - Download credentials.json from Google Cloud Console")
            print("  - See SETUP.md for detailed instructions")

        if not results['serper']:
            print("  - Check SERPER_API_KEY in .env")
            print("  - Verify API key is valid at serper.dev")


def main():
    """Run all tests"""
    print("="*60)
    print("SEO Agent - Setup Verification")
    print("="*60)

    results = {
        'dependencies': check_dependencies(),
        'environment': check_environment(),
        'credentials': check_credentials_file(),
        'oauth_token': check_oauth_token(),
        'serper': test_serper(),
        'oauth_ready': test_oauth_ready(),
        'agent': test_agent_load(),
    }

    print_tool_summary()
    print_next_steps(results)

    # Summary
    print_section("Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nPassed: {passed}/{total} checks")

    if passed == total:
        print("\n✓ Setup complete! Ready to analyze SEO data.")
        return 0
    else:
        print(f"\n⚠ {total - passed} checks need attention. See above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
