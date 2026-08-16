from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from .alerts import evaluate_alerts
import jwt

class MetricsView(APIView):
    """POST /api/metrics
    Expects JSON payload from probes. Authentication: header X-API-KEY or Authorization: Bearer <jwt>
    """
    def post(self, request):
        # Simple auth: X-API-KEY or Bearer JWT
        api_key = request.headers.get('X-API-KEY')
        auth = request.headers.get('Authorization')
        if api_key != settings.PROBE_API_KEY:
            if auth and auth.startswith('Bearer '):
                token = auth.split(' ', 1)[1]
                try:
                    jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                except Exception:
                    return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        payload = request.data
        # Validate minimal fields
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

        # Evaluate alerts asynchronously / sync simple
        try:
            evaluate_alerts(payload)
        except Exception:
            # don't fail the request due to alert delivery
            pass

        return Response({'status': 'ok'})
