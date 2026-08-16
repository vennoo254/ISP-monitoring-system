from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.query_api import QueryApi
from .alerts import evaluate_alerts
from .models import Probe
import jwt

class MetricsView(APIView):
    """POST /api/metrics
    Expects JSON payload from probes. Authentication: header X-API-KEY or Authorization: Bearer <jwt>
    """
    def post(self, request):
        # Simple auth: X-API-KEY or Bearer JWT
        api_key = request.headers.get('X-API-KEY')
        auth = request.headers.get('Authorization')
        authorized = False
        # Check DB-backed Probe keys first
        if api_key:
            try:
                if Probe.objects.filter(api_key=api_key).exists():
                    authorized = True
            except Exception:
                # DB may not be ready in some environments; fall back
                pass
        # fallback to legacy setting
        if not authorized and api_key == settings.PROBE_API_KEY:
            authorized = True
        if not authorized:
            if auth and auth.startswith('Bearer '):
                token = auth.split(' ', 1)[1]
                try:
                    jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    authorized = True
                except Exception:
                    authorized = False
        if not authorized:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        payload = request.data
        target = payload.get('target') or payload.get('target_ip')
        timestamp = payload.get('timestamp')
        if not target or not timestamp:
            return Response({'detail': 'target and timestamp required'}, status=status.HTTP_400_BAD_REQUEST)

        # Write to InfluxDB
        try:
            client = InfluxDBClient(url=settings.INFLUX_URL, token=settings.INFLUX_TOKEN, org=settings.INFLUX_ORG)
            write_api = client.write_api(write_options=SYNCHRONOUS)
            p = Point('probe_metrics').tag('target', str(target)).tag('probe_host', payload.get('probe_host','unknown'))
            if payload.get('avg_ms') is not None:
                p = p.field('latency_ms', float(payload.get('avg_ms')))
            if payload.get('packet_loss_pct') is not None:
                p = p.field('packet_loss_pct', float(payload.get('packet_loss_pct')))
            if payload.get('jitter_ms') is not None:
                p = p.field('jitter_ms', float(payload.get('jitter_ms')))
            if payload.get('bandwidth_mbps') is not None:
                p = p.field('bandwidth_mbps', float(payload.get('bandwidth_mbps')))
            write_api.write(bucket=settings.INFLUX_BUCKET, org=settings.INFLUX_ORG, record=p)
        except Exception as e:
            return Response({'detail': 'failed to write metrics', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Evaluate alerts (now backed by DB rules)
        try:
            evaluate_alerts(payload)
        except Exception:
            pass

        return Response({'status': 'ok'})


class HistoryView(APIView):
    """GET /api/history?target=8.8.8.8&metric=latency_ms&range=1h
    Returns JSON timeseries points [{time: iso, value: float}, ...]
    """
    def get(self, request):
        target = request.query_params.get('target')
        metric = request.query_params.get('metric')
        rng = request.query_params.get('range', '1h')
        if not target or not metric:
            return Response({'detail': 'target and metric are required'}, status=status.HTTP_400_BAD_REQUEST)
        # Map metric to field name used in Influx (same)
        field = metric
        flux = f'from(bucket:"{settings.INFLUX_BUCKET}") |> range(start: -{rng}) |> filter(fn: (r) => r._measurement == "probe_metrics" and r.target == "{target}" and r._field == "{field}") |> aggregateWindow(every: 1m, fn: mean) |> yield()'
        try:
            client = InfluxDBClient(url=settings.INFLUX_URL, token=settings.INFLUX_TOKEN, org=settings.INFLUX_ORG)
            query_api = client.query_api()
            tables = query_api.query(flux)
            pts = []
            for table in tables:
                for record in table.records:
                    pts.append({'time': record.get_time().isoformat(), 'value': record.get_value()})
            pts.sort(key=lambda x: x['time'])
            return Response({'points': pts})
        except Exception as e:
            return Response({'detail': 'failed to query influx', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
