#!/usr/bin/env python3

import os

from config_system.auth import AuthManager


def generate_api_key():
    """Generate a new API key"""
    secret_key = os.getenv("SECRET_KEY") or "your-secure-secret-key"
    auth_manager = AuthManager(secret_key=secret_key)
    api_key = auth_manager.create_api_key(roles=["read", "write"])
    print(f"Generated API key: {api_key}")


if __name__ == "__main__":
    generate_api_key()
