"""
Simple ping-based probe. Requires system `ping` utility.
Sends: target, timestamp, probe_host, avg_ms, min_ms, max_ms, packet_loss_pct, jitter_ms
"""
import subprocess, re, statistics, time, json, os
from probes.common import push


def run_ping(target, count=10, timeout=2):
    cmd = ["ping", "-c", str(count), "-W", str(timeout), target]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout
    m_loss = re.search(r"(\d+)% packet loss", out)
    loss = float(m_loss.group(1)) if m_loss else None
    m_rtt = re.search(r"rtt min/avg/max/mdev = ([\d\.]+)/([\d\.]+)/([\d\.]+)/([\d\.]+) ms", out)
    if m_rtt:
        min_rtt, avg_rtt, max_rtt, mdev = map(float, m_rtt.groups())
    else:
        min_rtt = avg_rtt = max_rtt = mdev = None
    rtts = [float(x.split("time=")[1].replace(" ms","")) for x in re.findall(r"time=[\d\.]+ ms", out)]
    jitter = statistics.pstdev(rtts) if len(rtts) > 1 else 0.0
    return {"target": target, "count": count, "packet_loss_pct": loss,
            "min_ms": min_rtt, "avg_ms": avg_rtt, "max_ms": max_rtt, "jitter_ms": jitter, "samples": rtts}

if __name__ == '__main__':
    target = os.environ.get('PROBE_TARGET', '8.8.8.8')
    interval = int(os.environ.get('PROBE_INTERVAL', '30'))
    probe_host = os.environ.get('PROBE_HOST', 'probe-1')
    while True:
        res = run_ping(target, count=10)
        payload = res
        payload['probe_host'] = probe_host
        payload['timestamp'] = int(time.time()*1000)
        code, text = push(payload)
        print('pushed', code, text)
        time.sleep(interval)
