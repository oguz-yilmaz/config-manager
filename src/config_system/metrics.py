import time

from prometheus_client import Counter, Gauge, Histogram


class Metrics:
    config_updates = Counter(
        "config_updates_total", "Number of configuration updates", ["path", "status"]
    )

    request_duration = Histogram(
        "request_duration_seconds", "Request latency in seconds", ["endpoint"]
    )

    active_connections = Gauge("active_connections", "Number of active connections")


def track_request_duration(endpoint: str, duration: float):
    Metrics.request_duration.labels(endpoint=endpoint).observe(duration)


def increment_config_updates(path: str, status: str):
    Metrics.config_updates.labels(path=path, status=status).inc()


def track_connection(active: bool = True):
    if active:
        Metrics.active_connections.inc()
    else:
        Metrics.active_connections.dec()
