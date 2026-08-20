import urllib.request
import urllib.error
import json
import time

print("=" * 60)
print("SMART E-COMMERCE API - AUTH ENDPOINTS TEST")
print("=" * 60)

# Test 1: Signup
print("\n1. Testing SIGNUP endpoint...")
email = f"test{int(time.time())}@example.com"
signup_payload = json.dumps({
    'email': email,
    'password': 'testpassword123'
}).encode('utf-8')

signup_req = urllib.request.Request(
    'http://127.0.0.1:8000/auth/signup',
    data=signup_payload,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(signup_req) as response:
        signup_result = json.loads(response.read().decode('utf-8'))
        user_id = signup_result['user_id']
        access_token = signup_result['access_token']
        print(f"   ✓ Signup successful!")
        print(f"   - User ID: {user_id}")
        print(f"   - Email: {signup_result['email']}")
        print(f"   - Token: {access_token[:40]}...")
except Exception as e:
    print(f"   ✗ Signup failed: {e}")
    exit(1)

# Test 2: Login with same credentials
print("\n2. Testing LOGIN endpoint...")
login_payload = json.dumps({
    'username': email,
    'password': 'testpassword123'
}).encode('utf-8')

login_req = urllib.request.Request(
    'http://127.0.0.1:8000/auth/login',
    data=login_payload,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(login_req) as response:
        login_result = json.loads(response.read().decode('utf-8'))
        print(f"   ✓ Login successful!")
        print(f"   - User ID: {login_result['user_id']}")
        print(f"   - Email: {login_result['email']}")
        print(f"   - Token: {login_result['access_token'][:40]}...")
except Exception as e:
    print(f"   ✗ Login failed: {e}")
    exit(1)

# Test 3: Try duplicate email (should fail)
print("\n3. Testing duplicate email prevention...")
dup_payload = json.dumps({
    'email': email,
    'password': 'anotherpassword'
}).encode('utf-8')

dup_req = urllib.request.Request(
    'http://127.0.0.1:8000/auth/signup',
    data=dup_payload,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(dup_req) as response:
        print(f"   ✗ Should have failed but didn't!")
        exit(1)
except urllib.error.HTTPError as e:
    if e.code == 400:
        error_response = json.loads(e.read().decode('utf-8'))
        if 'already registered' in error_response.get('detail', ''):
            print(f"   ✓ Correctly rejected duplicate email")
        else:
            print(f"   ✗ Wrong error: {error_response}")
            exit(1)
    else:
        print(f"   ✗ Wrong status code: {e.code}")
        exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
