import os
import requests
from django.conf import settings

# Simple in-memory state for debouncing consecutive failures
_state = {}

# Example thresholds (could be persisted in DB/config service)
DEFAULT_THRESHOLDS = {
    'latency_ms': 150.0,
    'packet_loss_pct': 2.0,
    'jitter_ms': 30.0,
}

def get_thresholds_for(target):
    # Placeholder to load per-target thresholds
    return DEFAULT_THRESHOLDS

def _send_notification(alert):
    url = settings.NOTIFICATION_SERVICE_URL
    try:
        requests.post(url, json=alert, timeout=5)
    except Exception:
        pass

def evaluate_alerts(measure):
    target = measure.get('target') or measure.get('target_ip')
    thr = get_thresholds_for(target)
    fired = []
    if measure.get('packet_loss_pct') is not None and float(measure['packet_loss_pct']) > thr['packet_loss_pct']:
        fired.append(('packet_loss', measure['packet_loss_pct']))
    if measure.get('avg_ms') is not None and float(measure['avg_ms']) > thr['latency_ms']:
        fired.append(('latency', measure['avg_ms']))
    if measure.get('jitter_ms') is not None and float(measure['jitter_ms']) > thr['jitter_ms']:
        fired.append(('jitter', measure['jitter_ms']))

    for kind, val in fired:
        key = f"{target}:{kind}"
        entry = _state.get(key, {'count':0})
        entry['count'] += 1
        _state[key] = entry
        # require 2 consecutive failures before alerting
        if entry['count'] >= 2:
            alert = {
                'target': target,
                'metric': kind,
                'value': val,
                'severity': 'warning',
                'timestamp': measure.get('timestamp'),
            }
            _send_notification(alert)
            entry['count'] = 0
            _state[key] = entry
    # reset counters when metrics healthy
    if not fired:
        # simple scan to reset counters for this target
        for k in list(_state.keys()):
            if k.startswith(f"{target}:"):
                _state.pop(k, None)
