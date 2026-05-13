"""Standalone Basecamp API Test"""
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables - try multiple locations
env_paths = [
    Path('seo_agent/.env'),  # Most likely location
    Path('.env'),             # Current directory
    Path('../.env'),          # Parent directory
]

loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f'Loaded .env from: {env_path.absolute()}')
        loaded = True
        break

if not loaded:
    print('WARNING: No .env file found in expected locations')
    print(f'Searched: {[str(p.absolute()) for p in env_paths]}')

BASECAMP_API_KEY = os.getenv('BASECAMP_API_KEY')
BASECAMP_ACCOUNT_ID = os.getenv('BASECAMP_ACCOUNT_ID')

print('=== Basecamp API Configuration ===')
print(f'Account ID: {BASECAMP_ACCOUNT_ID}')
print(f'API Key present: {"Yes" if BASECAMP_API_KEY else "No"}')
print(f'API Key length: {len(BASECAMP_API_KEY) if BASECAMP_API_KEY else 0}')
print()

if not BASECAMP_API_KEY or not BASECAMP_ACCOUNT_ID:
    print('ERROR: BASECAMP_API_KEY and BASECAMP_ACCOUNT_ID must be set in .env')
    exit(1)

headers = {
    'Authorization': f'Bearer {BASECAMP_API_KEY}',
    'User-Agent': 'SEO Agent Test (testing@example.com)',
    'Content-Type': 'application/json'
}

# Test 1: Get projects
print('=== Test 1: Get Projects ===')
url = f'https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/projects.json'
try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        projects = response.json()
        print(f'Found {len(projects)} projects:')
        for p in projects[:10]:
            print(f'  - {p["name"]} (ID: {p["id"]})')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Exception: {e}')

print()
print('=' * 60)
print()

# Test 2: Get Todolists for Project 43527235
print('=== Test 2: Get Todosets for Project 43527235 ===')
url = f'https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/43527235/todosets.json'
try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f'Status Code: {response.status_code}')
    print(f'URL: {url}')
    if response.status_code == 200:
        todoset = response.json()
        print(f'Todoset ID: {todoset.get("id")}')
        print(f'Todoset Name: {todoset.get("name")}')
        todolists = todoset.get('todolists', [])
        print(f'Found {len(todolists)} todolists:')
        for tl in todolists:
            print(f'  - {tl["title"]} (ID: {tl["id"]}, Todos: {tl.get("todos_count", 0)}, Completed: {tl.get("completed_count", 0)})')

        # Test 3: Get todos from first todolist if available
        if todolists:
            print()
            print('=' * 60)
            print()
            first_list = todolists[0]
            print(f'=== Test 3: Get Todos from "{first_list["title"]}" (ID: {first_list["id"]}) ===')
            url = f'https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}/buckets/43527235/todolists/{first_list["id"]}.json'
            response = requests.get(url, headers=headers, timeout=30)
            print(f'Status Code: {response.status_code}')
            if response.status_code == 200:
                todolist_data = response.json()
                remaining = todolist_data.get('todos', {}).get('remaining', [])
                completed = todolist_data.get('todos', {}).get('completed', [])
                print(f'Remaining todos: {len(remaining)}')
                print(f'Completed todos: {len(completed)}')

                all_todos = remaining + completed
                print(f'\nShowing first 10 todos:')
                for i, todo in enumerate(all_todos[:10], 1):
                    status = '✓' if todo.get('completed') else '○'
                    content = todo.get('content', '')[:60]
                    print(f'  {status} {content}...')
            else:
                print(f'Error: {response.text}')
    elif response.status_code == 404:
        print('ERROR 404: Not Found')
        print('\nMost likely cause: The "To-dos" tool is not enabled in this Basecamp project')
        print('\nOther possible causes:')
        print('  1. The project ID 43527235 does not exist in your account')
        print('  2. The account ID is incorrect')
        print('  3. Your API token does not have access to this project')
        print('\nTo fix: Go to Basecamp → Fulfillio project → Settings → Enable "To-dos" tool')
        print(f'\nAPI Response: {response.text}')
    else:
        print(f'Error Response: {response.text}')
except Exception as e:
    print(f'Exception: {e}')
    import traceback
    traceback.print_exc()
