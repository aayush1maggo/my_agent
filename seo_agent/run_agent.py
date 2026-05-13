"""
Simple script to run the SEO Agent interactively
"""
from seo_agent import seo_agent


def main():
    """Run the SEO Agent interactively"""
    print("=" * 60)
    print("SEO Agent - Powered by Google ADK")
    print("=" * 60)
    print("\nIntegrations:")
    print("  - Google Analytics 4")
    print("  - Google Search Console")
    print("  - Serper.dev (Live Keyword Ranking)")
    print("\nType your query or 'quit' to exit")
    print("=" * 60)

    while True:
        try:
            # Get user input
            query = input("\nYour query: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if not query:
                continue

            # Run the agent
            print("\nProcessing...\n")
            response = seo_agent.run(query)
            print("\n" + "=" * 60)
            print("Response:")
            print("=" * 60)
            print(response)
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again or check your setup.")


if __name__ == "__main__":
    main()
