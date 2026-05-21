import requests

try:
    r = requests.post('http://127.0.0.1:8000/signup', json={'username':'test_error_user','password':'pass123'}, timeout=5)
    print('STATUS', r.status_code, r.text)
except Exception as e:
    print('REQ ERROR', e)
