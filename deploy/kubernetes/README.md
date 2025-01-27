# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Configuration
Management System. It can be starting point for deploying the application in a
Kubernetes cluster.

## Prerequisites

- Kubernetes cluster
- kubectl configured to connect to your cluster
- Container registry with your application images
- Domain name (for Ingress configuration)

## Configuration

### 1. Prepare Secrets

Generate base64 encoded secrets for sensitive data:
```bash
# Generate auth secret key
echo -n "your-secure-secret-key" | base64
# Output: eW91ci1zZWN1cmUtc2VjcmV0LWtleQ==

# Update secret.yml with the generated values
```

### 2. Update Configurations

Edit `configmap.yml` for environment-specific settings:
```yaml
data:
  ENVIRONMENT: "production"  # or staging, development
  LOG_LEVEL: "INFO"
  ETCD_PORT: "2379"
  # ...
```

### 3. Update Image References

In `deployment.yml`, update the image reference:
```yaml
spec:
  containers:
  - name: config-service
    image: your-registry/config-service:your-tag
```

## Deployment

### 1. Create Namespace
```bash
kubectl apply -f namespace.yml
```

### 2. Deploy Core Components
```bash
kubectl apply -f .
```

### 3. Verify Deployment
```bash
kubectl get all -n config-system
```

## Resource Details

### Deployment
- Runs 3 replicas of the application
- Includes health checks (readiness/liveness probes)
- Resource limits and requests defined
- Rolling update strategy

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

### Accessing the Service

#### Internal Access (from other services)

```python
endpoint = "http://config-service.config-system.svc.cluster.local"
```

#### External Access

```bash
curl https://config.yourdomain.com/config/myapp
```

## Support

For issues or questions:
1. Check the logs using commands provided above
2. Review the application's health endpoint
3. Contact the development team
