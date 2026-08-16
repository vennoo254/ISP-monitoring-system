# Architecture and purpose

This repository adds an initial collector (Django) and probe scripts (Python) plus a Node.js notification/websocket service.

Components
- collector/: Django collector API that accepts probe data and writes to InfluxDB. It also evaluates simple alerts and forwards alert events to the notification service.
- probes/: Example probe scripts (ping, traceroute, iperf, snmp) that push metrics to the collector.
- nodejs/notification/: WebSocket + HTTP service that broadcasts alerts to connected dashboard clients and can send email/SMS via SMTP/Twilio.
- docker-compose.yml: Development compose with InfluxDB and Grafana placeholders.

Next steps
- Run `docker compose up --build` to boot services locally after configuring secrets.
- Customize thresholds and persistent storage for alert rules.
- Add frontend (React) to subscribe to WebSocket notifications and query InfluxDB for history.
