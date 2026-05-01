import requests
import time

url = 'http://localhost:5000/api/login'
for i in range(6):
    try:
        r = requests.post(url, json={'role':'admin','username':'admin','password':'admin'}, timeout=5)
        print('STATUS', r.status_code)
        print('BODY', r.text)
        break
    except Exception as e:
        print('Attempt', i+1, 'failed:', e)
        time.sleep(1)
