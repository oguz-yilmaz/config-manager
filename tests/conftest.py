import os
from pathlib import Path

import docker
import pytest
import yaml


@pytest.fixture(scope="session")
def load_config():
    config_path = Path(__file__).parent.parent / "config" / "environments.yml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    return config["development"]


@pytest.fixture(scope="session")
def get_docker_client(load_config):
    config = load_config
    uses = config["docker"]["uses"]

    if uses == "orbstack":
        home = os.path.expanduser("~")
        return docker.DockerClient(base_url=f"unix://{home}/.orbstack/run/docker.sock")
    else:
        return docker.from_env()
