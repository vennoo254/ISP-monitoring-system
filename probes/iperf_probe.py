# iperf3 wrapper (requires iperf3 client installed)
import subprocess, json, time, os
from probes.common import push


def run_iperf(server, duration=10):
    cmd = ["iperf3", "-c", server, "-J", "-t", str(duration)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        out = json.loads(p.stdout)
        # extract bits per second
        bw = None
        if 'end' in out and 'sum_received' in out['end']:
            bw = out['end']['sum_received']['bits_per_second']
        return out, bw
    except Exception:
        return p.stdout, None

if __name__ == '__main__':
    server = os.environ.get('IPERF_SERVER', 'iperf3-server')
    probe_host = os.environ.get('PROBE_HOST', 'probe-1')
    out, bw = run_iperf(server)
    payload = {'target': server, 'probe_host': probe_host, 'timestamp': int(time.time()*1000), 'iperf_result': out}
    if bw:
        payload['bandwidth_mbps'] = bw/1e6
    code, text = push(payload)
    print('iperf pushed', code)
