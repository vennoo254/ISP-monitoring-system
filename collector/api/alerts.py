import requests
from django.conf import settings
from .models import AlertRule, AlertState, AlertEvent
from django.utils import timezone


def _send_notification(alert):
    url = settings.NOTIFICATION_SERVICE_URL
    try:
        requests.post(url, json=alert, timeout=5)
    except Exception:
        pass


def evaluate_alerts(measure):
    """Evaluate incoming measure against persisted alert rules.
    measure is the probe payload dict. Rules are stored in AlertRule model.
    """
    target = measure.get('target') or measure.get('target_ip')
    if not target:
        return
    # Load enabled rules that either match this target or are global (empty target)
    rules = AlertRule.objects.filter(enabled=True).filter(models.Q(target=target) | models.Q(target=''))
    for rule in rules:
        metric_value = None
        if rule.metric == 'latency_ms':
            metric_value = measure.get('avg_ms')
        elif rule.metric == 'packet_loss_pct':
            metric_value = measure.get('packet_loss_pct')
        elif rule.metric == 'jitter_ms':
            metric_value = measure.get('jitter_ms')
        elif rule.metric == 'bandwidth_mbps':
            metric_value = measure.get('bandwidth_mbps')
        if metric_value is None:
            continue
        violated = False
        if rule.comparison == 'gt' and float(metric_value) > float(rule.threshold):
            violated = True
        if rule.comparison == 'lt' and float(metric_value) < float(rule.threshold):
            violated = True
        # get or create alert state for this rule+target
        state, _ = AlertState.objects.get_or_create(rule=rule, target=target)
        if violated:
            state.consecutive_failures += 1
            state.save()
            if state.consecutive_failures >= rule.consecutive:
                # fire alert
                alert = {
                    'target': target,
                    'metric': rule.metric,
                    'value': metric_value,
                    'severity': rule.severity,
                    'timestamp': measure.get('timestamp')
                }
                # persist event
                try:
                    AlertEvent.objects.create(rule=rule, target=target, metric=rule.metric, value=metric_value, severity=rule.severity, timestamp=measure.get('timestamp'))
                except Exception:
                    pass
                _send_notification(alert)
                # reset counter
                state.consecutive_failures = 0
                state.last_triggered = timezone.now()
                state.save()
        else:
            # reset on healthy reading
            if state.consecutive_failures != 0:
                state.consecutive_failures = 0
                state.save()
