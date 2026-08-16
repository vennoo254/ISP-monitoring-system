from django.contrib import admin
from .models import Probe, AlertRule, AlertState, AlertEvent

@admin.register(Probe)
class ProbeAdmin(admin.ModelAdmin):
    list_display = ('id','name','api_key','created_at')
    readonly_fields = ('created_at',)

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('id','name','target','metric','comparison','threshold','consecutive','severity','enabled')
    list_filter = ('metric','severity','enabled')

@admin.register(AlertState)
class AlertStateAdmin(admin.ModelAdmin):
    list_display = ('id','rule','target','consecutive_failures','last_triggered')

@admin.register(AlertEvent)
class AlertEventAdmin(admin.ModelAdmin):
    list_display = ('id','rule','target','metric','value','severity','timestamp','acknowledged','created_at')
    list_filter = ('severity','acknowledged')
    readonly_fields = ('created_at',)
