# ISP Monitoring System

This repository contains a scaffold for an ISP/network performance monitoring system using Prometheus + Grafana, a simple Python ping exporter, a FastAPI backend (with Postgres), and a minimal frontend.

Quick start (requires Docker & Docker Compose):

1. Copy .env.example to .env and adjust values (POSTGRES_PASSWORD, etc.)
2. docker-compose up --build
3. Visit:
   - Grafana: http://localhost:3000 (default admin:admin)
   - Prometheus: http://localhost:9090
   - Frontend: http://localhost:8080

Components
- prometheus: scrapes exporters (node_exporter, ping_exporter) and backend metrics
- grafana: dashboards (import manually)
- ping_exporter: small Python service that pings targets and exposes Prometheus metrics
- backend: FastAPI server that stores monitoring targets in Postgres and exposes an API
- frontend: minimal single-page UI to manage targets

See docs/architecture.md for design decisions and alerting suggestions.
