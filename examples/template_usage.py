import json

import requests
import uvicorn
from fastapi import FastAPI

from config_system import AppConfig, ConfigurationAPI, SecurityConfig


def template_example():
    # Configure the system
    config = AppConfig(security=SecurityConfig(secret_key="your-secure-secret-key"))

    # Create and mount the config system
    main_app = FastAPI()
    config_api = ConfigurationAPI(config)
    main_app.mount("/config", config_api.app)

    # Generate API key
    api_key = config_api.auth_manager.create_api_key(roles=["write"])
    print(f"Generated API key: {api_key}")

    # Template configuration
    template_config = {
        "database": {
            "host": "{{ env }}.database.com",
            "readonly": "{{ 'true' if env == 'prod' else 'false' }}",
        }
    }

    @main_app.on_event("startup")
    async def startup():
        # Store template config
        response = requests.put(
            "http://localhost:8000/config/config/myapp/database",
            headers={"X-API-Key": api_key},
            json=template_config,
        )
        print("Store template response:", response.json())

        # Get config for different environments
        for env in ["dev", "prod"]:
            response = requests.get(
                "http://localhost:8000/config/config/myapp/database",
                headers={"X-API-Key": api_key},
                params={"environment": env},
            )
            print(f"{env.upper()} config:", json.dumps(response.json(), indent=2))

    return main_app


if __name__ == "__main__":
    app = template_example()
    uvicorn.run(app, host="0.0.0.0", port=8000)
