from fastapi import FastAPI
from .database import engine, Base, SessionLocal
from .routers import targets
from prometheus_client import start_http_server, Summary
import os

app = FastAPI(title="ISP Monitoring Backend")

Base.metadata.create_all(bind=engine)

app.include_router(targets.router, prefix='/api/targets', tags=['targets'])

# Expose basic metrics via prometheus_client on /metrics via Starlette? Simpler: run default server
from starlette.middleware import Middleware
from starlette_prometheus import PrometheusMiddleware, metrics
app.add_middleware(PrometheusMiddleware)
app.add_route('/metrics', metrics)

@app.get('/')
def root():
    return {"status": "ok"}
