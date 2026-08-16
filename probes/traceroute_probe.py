# traceroute probe (Linux `traceroute` required)
import subprocess, re, time, os
from probes.common import push

def run_traceroute(target, max_hops=30):
    cmd = ["traceroute", "-n", "-m", str(max_hops), target]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout
    return out

if __name__ == '__main__':
    target = os.environ.get('PROBE_TARGET', '8.8.8.8')
    probe_host = os.environ.get('PROBE_HOST', 'probe-1')
    result = run_traceroute(target)
    payload = {'target': target, 'probe_host': probe_host, 'timestamp': int(time.time()*1000), 'traceroute': result}
    code, text = push(payload)
    print('traceroute pushed', code)
