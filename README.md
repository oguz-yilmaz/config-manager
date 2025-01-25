# Configuration Management System

A distributed configuration management system built with FastAPI and etcd,
designed for managing application configurations across different environments
with version control, security, and monitoring capabilities.

## Features

- **Distributed Storage**: Uses etcd as a reliable, distributed key-value store
- **Version Control**: Track all configuration changes with rollback capability
- **Environment Support**: Manage configs across dev/staging/prod environments
- **Security**:
  - API key authentication
  - Role-based access control
  - Configuration encryption
  - Audit logging
- **Validation & Templates**:
  - JSON schema validation
  - Template support with variable substitution
  - Environment-specific variables
- **Monitoring**:
  - Prometheus metrics integration
  - Health check endpoints
  - Request rate limiting
- **Deployment**:
  - Docker support
  - Kubernetes manifests
  - Multiple environment configurations

## Prerequisites

- Python 3.8+
- etcd v3.4+
- Docker (optional)
- Kubernetes (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/config-manager.git
cd config-manager
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Start etcd (using Docker):
```bash
docker run -d -p 2379:2379 bitnami/etcd:latest -e ALLOW_NONE_AUTHENTICATION=yes
```

2. Start the service:
```bash
python -m uvicorn src.config_system.api:app --reload
```

3. Create an API key:
```python
from config_system.auth import AuthManager
auth_manager = AuthManager()
api_key = auth_manager.create_api_key(roles=["write"])
print(f"Your API key: {api_key}")
```

4. Usage
```python
# 1. Configure and create the API
from config_system import ConfigurationAPI, AppConfig, SecurityConfig, CORSConfig
from config_system.auth import AuthManager
from fastapi import FastAPI

config = AppConfig(
    security=SecurityConfig(
        secret_key="your-secret-key"
    ),
    cors=CORSConfig(
        allow_origins=["https://yourdomain.com"],
        allow_methods=["GET", "PUT"]
    ),
    storage=StorageConfig(
        host="etcd.internal",
        port=2379
    ),
    rate_limit_read="200/minute",
    rate_limit_write="50/minute"
)

# Create your main application
main_app = FastAPI()

# Initialize config system and mount it
config_api = ConfigurationAPI(config)
main_app.mount("/config", config_api.app)

# 2. Start your application
# uvicorn your_app:main_app --reload

# 3. Generate API key (in a separate script/management command)
auth_manager = AuthManager(secret_key=config.security.secret_key)
api_key = auth_manager.create_api_key(roles=["write"])
print(f"Your API key: {api_key}")

# 3. Use the API:
import requests

# Store configuration
config_data = {
    "database": {
        "host": "{{ env }}.db.example.com",
        "port": 5432
    }
}

# Note that now we use /config prefix because we mounted it there

# Update config
response = requests.put(
    "http://localhost:8000/config/myapp/database",
    headers={"X-API-Key": api_key},
    json=config_data
)

# Get config
response = requests.get(
    "http://localhost:8000/config/myapp/database",
    headers={"X-API-Key": api_key},
    params={"environment": "prod"}
)
```

## Docker Deployment

1. Build and run using Docker Compose:
```bash
docker-compose up -d
```

## Kubernetes Deployment

1. Apply the Kubernetes manifests:
```bash
kubectl apply -f deploy/kubernetes/
```

## API Reference

### Endpoints

- `GET /config/{path}` - Retrieve configuration
  - Query params:
    - `environment`: Environment name (default: "prod")
  - Headers:
    - `X-API-Key`: API key with read access

- `PUT /config/{path}` - Update configuration
  - Body: Configuration JSON
  - Headers:
    - `X-API-Key`: API key with write access

- `GET /health` - Health check endpoint

### Rate Limits
- Read operations: 100 requests per minute
- Write operations: 20 requests per minute

## Schema Validation

Example schema:
```json
{
    "type": "object",
    "properties": {
        "database": {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer"}
            },
            "required": ["host", "port"]
        }
    }
}
```

## Monitoring

### Metrics

Available at `/metrics`:
- `config_updates_total`: Counter of configuration updates
- `request_duration_seconds`: Request latency histogram

### Prometheus Integration

Example Prometheus configuration:
```yaml
scrape_configs:
  - job_name: 'config-service'
    static_configs:
      - targets: ['localhost:8000']
```

## Security Considerations

1. API Key Management:
   - Rotate keys regularly
   - Use separate keys for different applications
   - Monitor key usage

2. Network Security:
   - Enable TLS in production
   - Use network policies in Kubernetes
   - Configure proper firewall rules

3. etcd Security:
   - Enable authentication
   - Use TLS certificates
   - Regular backups

## Production Checklist

- [ ] Configure proper API key management
- [ ] Set up TLS certificates
- [ ] Configure etcd authentication
- [ ] Set up monitoring and alerting
- [ ] Implement backup strategy
- [ ] Configure proper logging
- [ ] Set resource limits
- [ ] Plan for high availability

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
