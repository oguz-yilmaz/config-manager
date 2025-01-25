import requests
import uvicorn
from fastapi import FastAPI

from config_system import AppConfig, ConfigurationAPI, SecurityConfig


def basic_config_example():
    # Configure the system
    config = AppConfig(
        security=SecurityConfig(
            secret_key="your-secure-secret-key"  # In prod, use env vars
        )
    )

    # Create and mount the config system
    main_app = FastAPI()
    config_api = ConfigurationAPI(config)
    main_app.mount("/config", config_api.app)

    # Generate API key
    api_key = config_api.auth_manager.create_api_key(roles=["write"])
    print(f"Generated API key: {api_key}")

    # Example configuration data
    config_data = {
        "database": {
            "host": "{{ env }}.db.example.com",
            "port": 5432,
            "max_connections": 100,
        }
    }

    # Start the server (in a real app, this would be separate)
    @main_app.on_event("startup")
    async def startup():
        # Store config using API
        response = requests.put(
            "http://localhost:8000/config/config/myapp/database",
            headers={"X-API-Key": api_key},
            json=config_data,
        )
        print("Store config response:", response.json())

        # Retrieve config
        response = requests.get(
            "http://localhost:8000/config/config/myapp/database",
            headers={"X-API-Key": api_key},
            params={"environment": "prod"},
        )
        print("Retrieved config:", response.json())

    return main_app


if __name__ == "__main__":
    app = basic_config_example()
    uvicorn.run(app, host="0.0.0.0", port=8000)
