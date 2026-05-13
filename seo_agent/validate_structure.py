"""Quick validation script for multi-agent structure"""
import os
import ast

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("Multi-Agent Structure Validation")
    print("=" * 60)

    # Check agent files
    agent_files = [
        'seo_agent/agents/__init__.py',
        'seo_agent/agents/analytics_agent.py',
        'seo_agent/agents/keyword_agent.py',
        'seo_agent/agents/technical_agent.py',
        'seo_agent/agents/documentation_agent.py',
        'seo_agent/agents/coordinator.py',
    ]

    print("\nChecking agent files:")
    all_valid = True
    for filepath in agent_files:
        if not os.path.exists(filepath):
            print(f"  [ERROR] Missing: {filepath}")
            all_valid = False
            continue

        valid, error = check_file_syntax(filepath)
        if valid:
            print(f"  [OK] {filepath}")
        else:
            print(f"  [ERROR] Syntax error in {filepath}: {error}")
            all_valid = False

    # Check updated files
    updated_files = [
        'seo_agent/agent.py',
        'seo_agent/__init__.py',
    ]

    print("\nChecking updated files:")
    for filepath in updated_files:
        if not os.path.exists(filepath):
            print(f"  [ERROR] Missing: {filepath}")
            all_valid = False
            continue

        valid, error = check_file_syntax(filepath)
        if valid:
            print(f"  [OK] {filepath}")
        else:
            print(f"  [ERROR] Syntax error in {filepath}: {error}")
            all_valid = False

    # Check test file
    test_file = 'tests/test_multi_agent.py'
    print("\nChecking test file:")
    if os.path.exists(test_file):
        valid, error = check_file_syntax(test_file)
        if valid:
            print(f"  [OK] {test_file}")
        else:
            print(f"  [ERROR] Syntax error in {test_file}: {error}")
            all_valid = False
    else:
        print(f"  [ERROR] Missing: {test_file}")
        all_valid = False

    # Check CLAUDE.md
    print("\nChecking documentation:")
    if os.path.exists('CLAUDE.md'):
        print("  [OK] CLAUDE.md")
    else:
        print("  [ERROR] Missing: CLAUDE.md")
        all_valid = False

    print("\n" + "=" * 60)
    if all_valid:
        print("[SUCCESS] All structure validation checks passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run tests: python -m pytest tests/test_multi_agent.py -v")
        print("3. Test the agent: python run_agent.py")
    else:
        print("[FAILED] Some validation checks failed. Please review errors above.")
    print("=" * 60)

if __name__ == '__main__':
    main()
