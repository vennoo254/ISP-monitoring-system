from django.db import models

class Probe(models.Model):
    name = models.CharField(max_length=200, blank=True)
    api_key = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.api_key[:8]


class AlertRule(models.Model):
    COMPARISON_CHOICES = (
        ('gt', 'greater_than'),
        ('lt', 'less_than'),
    )
    METRIC_CHOICES = (
        ('latency_ms', 'latency_ms'),
        ('packet_loss_pct', 'packet_loss_pct'),
        ('jitter_ms', 'jitter_ms'),
        ('bandwidth_mbps', 'bandwidth_mbps'),
    )
    name = models.CharField(max_length=200)
    target = models.CharField(max_length=200, blank=True, help_text='Target IP or leave blank for global')
    metric = models.CharField(max_length=50, choices=METRIC_CHOICES)
    comparison = models.CharField(max_length=2, choices=COMPARISON_CHOICES, default='gt')
    threshold = models.FloatField()
    consecutive = models.IntegerField(default=2, help_text='Number of consecutive violations before firing')
    severity = models.CharField(max_length=20, default='warning')
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.metric} {self.comparison} {self.threshold})"


class AlertState(models.Model):
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    target = models.CharField(max_length=200, blank=True)
    consecutive_failures = models.IntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('rule', 'target')

    def __str__(self):
        return f"state:{self.rule_id}:{self.target}"


class AlertEvent(models.Model):
    rule = models.ForeignKey(AlertRule, on_delete=models.SET_NULL, null=True, blank=True)
    target = models.CharField(max_length=200)
    metric = models.CharField(max_length=50)
    value = models.FloatField(null=True, blank=True)
    severity = models.CharField(max_length=20)
    timestamp = models.BigIntegerField()  # epoch ms from probe
    acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert {self.metric} on {self.target} @ {self.created_at}"
