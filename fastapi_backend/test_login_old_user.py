import urllib.request
import urllib.error
import json

# Test login with one of the original users (who have argon2 hashes)
payload = json.dumps({
    'username': 'test@example.com',
    'password': 'password'  # Default password from earlier
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/auth/login',
    data=payload,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        print(f'Status Code: {response.status}')
        body = response.read().decode('utf-8')
        result = json.loads(body)
        print(f'Response: SUCCESS')
        print(f'  User ID: {result["user_id"]}')
        print(f'  Email: {result["email"]}')
        print(f'  Token: {result["access_token"][:50]}...')
except urllib.error.HTTPError as e:
    print(f'Status Code: {e.code}')
    response_body = e.read().decode('utf-8')
    print(f'Response: {response_body}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
