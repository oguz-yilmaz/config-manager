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

Since the app is a FastAPI application, you have different options to run it:

- **Mounting in an Existing FastAPI App**: You can mount the `ConfigurationAPI`
instance in your existing FastAPI app.
- **Running as a Standalone App**: You can run the app using `uvicorn` directly.

In both cases, you need to start an etcd instance for storage. And create an
API key for authentication.

**Start etcd**:
```bash
docker run -d -p 2379:2379 bitnami/etcd:latest -e ALLOW_NONE_AUTHENTICATION=yes
```

**Create an API key**:
```python
from config_system.auth import AuthManager
auth_manager = AuthManager(secret_key="your-secret-key")

read_key = auth_manager.create_api_key(roles=["read"])
print(f"Read API Key: {read_key}")

write_key = auth_manager.create_api_key(roles=["write"])
print(f"Write API Key: {write_key}")

admin_key = auth_manager.create_api_key(roles=["read", "write", "admin"])
print(f"Admin API Key: {admin_key}")
```

We can also go ahead and create the `ConfigurationAPI` instance because in
both cases, we need to mount it or run it.

```python
from config_system import ConfigurationAPI, AppConfig, SecurityConfig, CORSConfig, StorageConfig
from config_system.auth import AuthManager

# Configure with all available options
config = AppConfig(
   security=SecurityConfig(
       secret_key="your-secret-key",
       token_expiry=3600,  # JWT token expiry in seconds
       min_password_length=8
   ),
   cors=CORSConfig(
       allow_origins=["https://yourdomain.com"],
       allow_methods=["GET", "PUT", "POST", "DELETE"],
       allow_headers=["*"],
       allow_credentials=True
   ),
   storage=StorageConfig(
       host="etcd.internal",
       port=2379,
       username="etcd-user",  # Optional
       password="etcd-pass",  # Optional
   ),
   # Rate limiting
   rate_limit_read="200/minute",
   rate_limit_write="50/minute"
)
```

### 1. Direct usage (Standalone App without mounting)

```python
# main.py

# Initialize the API
config_api = ConfigurationAPI(config)

# Export the FastAPI app
app = config_api.app
```

Start the server:

```bash
uvicorn main:app --reload
```

### 2. Mounting in an existing FastAPI app

```python
from fastapi import FastAPI

# Your main application
main_app = FastAPI()


# Initialize the API
config_api = ConfigurationAPI(config)

# Mount configuration system
main_app.mount("/config", config_api.app)
```

### Using the API

#### Basic Usage

```python
import requests

config_data = {
   "database": {
       "host": "db.example.com",
       "port": 5432,
       "max_connections": 100,
       "ssl": True
   }
}

# Schema for validation (optional)
schema = {
   "type": "object",
   "properties": {
       "database": {
           "type": "object",
           "properties": {
               "host": {"type": "string"},
               "port": {"type": "integer", "minimum": 1, "maximum": 65535},
               "max_connections": {"type": "integer", "minimum": 1},
               "ssl": {"type": "boolean"}
           },
           "required": ["host", "port"]
       }
   }
}

# Base URL (depends on how you're running the app)
# For direct usage:
base_url = "http://localhost:8000"
# For mounted usage:
base_url = "http://localhost:8000/config"

# Store configuration
response = requests.put(
   f"{base_url}/myapp/database",
   headers={"X-API-Key": write_key},
   json=config_data,
   params={"schema": schema}  # Optional schema validation
)

# Get configuration
response = requests.get(
   f"{base_url}/myapp/database",
   headers={"X-API-Key": read_key},
   params={"environment": "prod"}  # Environment for template rendering
)

# Health check
response = requests.get(f"{base_url}/health")
```

#### Advanced Usage

```python
# Store configuration with template variables
template_config = {
   "api": {
       "url": "https://{{ env }}.api.example.com",
       "timeout": "{{ '30' if env == 'prod' else '5' }}",
       "retries": "{{ '5' if env == 'prod' else '1' }}"
   }
}

# Store it
response = requests.put(
   f"{base_url}/myapp/api",
   headers={"X-API-Key": write_key},
   json=template_config
)

# Get for different environments
prod_config = requests.get(
   f"{base_url}/myapp/api",
   headers={"X-API-Key": read_key},
   params={"environment": "prod"}
)

dev_config = requests.get(
   f"{base_url}/myapp/api",
   headers={"X-API-Key": read_key},
   params={"environment": "dev"}
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
