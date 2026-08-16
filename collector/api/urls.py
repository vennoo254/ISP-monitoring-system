from django.urls import path
from .views import MetricsView, HistoryView

urlpatterns = [
    path('metrics', MetricsView.as_view(), name='metrics'),
    path('history', HistoryView.as_view(), name='history'),
]
