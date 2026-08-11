from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess
import threading
import time
from prometheus_client import Gauge, generate_latest

TARGETS_ENV = os.environ.get('TARGETS', '8.8.8.8').split(',')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', '10'))
PORT = int(os.environ.get('PORT', '9115'))

# Metrics
latency_gauge = Gauge('ping_latency_seconds', 'Ping latency in seconds', ['target'])
loss_gauge = Gauge('ping_packet_loss_percent', 'Packet loss percent', ['target'])

results = {}

lock = threading.Lock()

def ping_target(target):
    # use system ping: sends 1 packet, wait up to 2 seconds
    try:
        proc = subprocess.run(['ping', '-c', '1', '-W', '2', target], capture_output=True, text=True)
        out = proc.stdout
        if proc.returncode == 0:
            # parse time=XX ms
            for part in out.split():
                if 'time=' in part:
                    val = part.split('time=')[-1]
                    val = val.replace('ms','')
                    latency_ms = float(val)
                    return latency_ms/1000.0, 0.0
            return 0.0, 0.0
        else:
            return 0.0, 100.0
    except Exception:
        return 0.0, 100.0


def worker():
    while True:
        for t in TARGETS_ENV:
            t = t.strip()
            lat, loss = ping_target(t)
            with lock:
                results[t] = (lat, loss, time.time())
            latency_gauge.labels(target=t).set(lat)
            loss_gauge.labels(target=t).set(loss)
        time.sleep(POLL_INTERVAL)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            data = generate_latest()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; version=0.0.4')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"Ping exporter listening on {PORT}, targets={TARGETS_ENV}")
    server.serve_forever()
