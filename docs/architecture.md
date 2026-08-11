# Architecture

This document explains the proposed components and how they fit together.

Components
- Prometheus: scrape exporters and backend metrics, run queries, store recent time series.
- Grafana: visualize latency, packet loss, throughput. Create dashboards (per target, per region).
- Ping exporter: lightweight pinger that collects latency and packet loss and exposes Prometheus metrics.
- Node exporter: basic host metrics for monitoring servers.
- Backend (FastAPI): stores monitoring targets, serves API for frontend and optional dynamic target provisioning.
- Frontend: minimal UI to manage targets.
- Postgres: persistent storage for targets and historical metadata.

Metrics to collect
- ping_latency_seconds{target}
- ping_packet_loss_percent{target}
- node_exporter metrics (interface errors, CPU, memory)
- backend app metrics

Alert ideas
- ping_packet_loss_percent > 50% for 5m
- ping_latency_seconds > 0.5s for 1m

Security
- Don't expose DB directly to the internet; use firewall / VPN.
- Secure Grafana with a strong admin password and enable HTTPS in production.

Next steps
- Add Grafana provisioning/dashboards
- Add SNMP or IPERF-based throughput collectors
- Add authentication and RBAC to backend/frontend
