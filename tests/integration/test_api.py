import time
from datetime import datetime, timedelta

import docker
import etcd3
import pytest
import requests
from fastapi.testclient import TestClient

from config_system.api import ConfigurationAPI
from config_system.models import AppConfig, CORSConfig, SecurityConfig, StorageConfig
from tests.conftest import get_docker_client


@pytest.fixture(scope="session")
def etcd_container(get_docker_client):
    """Fixture to start etcd container for testing"""
    try:
        IMAGE = "bitnami/etcd:latest"
        client = get_docker_client

        print("Pulling etcd image...")
        client.images.pull(IMAGE)

        print("Starting etcd container...")
        container = client.containers.run(
            IMAGE,
            detach=True,
            ports={"2379/tcp": 2379},
            environment={
                "ALLOW_NONE_AUTHENTICATION": "yes",
                "ETCD_LISTEN_CLIENT_URLS": "http://0.0.0.0:2379",
                "ETCD_ADVERTISE_CLIENT_URLS": "http://0.0.0.0:2379",
            },
        )

        def is_container_ready():
            try:
                container.reload()
                response = requests.get("http://localhost:2379/health")
                return response.status_code == 200 and container.status == "running"
            except:
                return False

        timout = datetime.now() + timedelta(seconds=30)
        while datetime.now() < timout:
            if is_container_ready():
                print("etcd container is ready")
                break
            time.sleep(1)
        else:
            pytest.fail("etcd container failed to start")

        print("Waiting for etcd to start...")

        yield container

        print("Cleaning up...")
        container.stop()
        container.remove()
    except docker.errors.DockerException as e:
        pytest.fail(f"Docker error: {e}. Make sure Docker is running.")


@pytest.fixture(scope="module")
def app_config():
    """Create test configuration"""
    return AppConfig(
        security=SecurityConfig(
            secret_key="test-secret-key", token_expiry=3600, min_password_length=8
        ),
        cors=CORSConfig(
            allow_origins=["http://localhost:8000"],
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        ),
        storage=StorageConfig(host="localhost", port=2379),
        rate_limit_read="200/minute",
        rate_limit_write="50/minute",
    )


@pytest.fixture(scope="module")
def config_api_instance(app_config):
    """Create ConfigurationAPI instance"""
    yield ConfigurationAPI(app_config)


@pytest.fixture(scope="module")
def config_api_fastapi_instance(config_api_instance):
    """Create FastAPI application"""
    yield config_api_instance.app


@pytest.fixture(scope="module")
def api_key(config_api_instance):
    """Create test API key"""
    config_api = config_api_instance
    yield config_api.auth_manager.create_api_key(roles=["write", "read"])


@pytest.fixture(scope="function")
def test_client(config_api_fastapi_instance, etcd_container):
    """Create test client"""
    with TestClient(config_api_fastapi_instance) as client:
        yield client


def test_get_config(test_client, api_key):
    print("\nStarting test_get_config")
    print("Test client ready")

    headers = {"X-API-Key": api_key}

    response = test_client.get("/config/health", headers=headers)

    print(f"Response status: {response.status_code}")
    assert response.status_code == 200
