import requests

try:
    r = requests.post('http://https://finance-tracker-mv0i.onrender.com/signup', json={'username':'test_error_user','password':'pass123'}, timeout=5)
    print('STATUS', r.status_code, r.text)
except Exception as e:
    print('REQ ERROR', e)
