import requests
import time

API = "http://127.0.0.1:8000"

# give server a bit to start
time.sleep(1)

print('Testing signup...')
try:
    r = requests.post(API + '/signup', json={"username": "testuser", "password": "testpass"}, timeout=5)
    print('/signup', r.status_code, r.text)
except Exception as e:
    print('/signup error', e)

print('\nTesting login...')
try:
    r = requests.post(API + '/login', json={"username": "testuser", "password": "testpass"}, timeout=5)
    print('/login', r.status_code, r.text)
    token = r.json().get('token') if r.status_code == 200 else None
except Exception as e:
    print('/login error', e)
    token = None

print('\nTesting add expense...')
try:
    payload = {"username": "testuser", "amount": 9.99, "category": "Food", "description": "Snack", "date": "2026-05-21T12:00:00"}
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    r = requests.post(API + '/expense', json=payload, timeout=5, headers=headers)
    print('/expense', r.status_code, r.text)
except Exception as e:
    print('/expense error', e)

print('\nTesting get expenses...')
try:
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    r = requests.get(API + '/expenses/testuser', timeout=5, headers=headers)
    print('/expenses/testuser', r.status_code, r.text)
except Exception as e:
    print('/expenses error', e)
