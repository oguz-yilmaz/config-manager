from prometheus_client import Counter, Histogram
config_updates = Counter('config_updates_total', 'Number of configuration updates')
request_duration = Histogram('request_duration_seconds', 'Request latency')
