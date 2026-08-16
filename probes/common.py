# Common helper for probe scripts
import requests
import time
import os

COLLECTOR_URL = os.environ.get('COLLECTOR_URL', 'http://collector:8000/api/metrics')
API_KEY = os.environ.get('PROBE_API_KEY', 'default-probe-key')

HEADERS = {
    'Content-Type': 'application/json',
    'X-API-KEY': API_KEY,
}


def push(payload):
    try:
        resp = requests.post(COLLECTOR_URL, json=payload, headers=HEADERS, timeout=5)
        return resp.status_code, resp.text
    except Exception as e:
        return None, str(e)
