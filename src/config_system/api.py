import logging
from datetime import datetime
from functools import partial
from typing import Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

from .auth import AuthManager
from .config_manager import ConfigManager
from .metrics import increment_config_updates, track_request_duration
from .models import AppConfig
from .storage import Storage
from .validation import validate_config_schema

logger = logging.getLogger(__name__)


class ConfigurationAPI:
    def __init__(self, config: AppConfig):
        """
        Initialize the Configuration Management System API.

        Args:
            config: AppConfig instance containing all configuration options
        """
        self.config = config
        self.app = FastAPI(title="Configuration Management System")

        self.auth_manager = AuthManager(secret_key=self.config.security.secret_key)

        self._setup_middleware()
        self._setup_routes()
        self._setup_startup()

    def _setup_middleware(self):
        """Configure middleware based on provided configuration"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors.allow_origins,
            allow_credentials=self.config.cors.allow_credentials,
            allow_methods=self.config.cors.allow_methods,
            allow_headers=self.config.cors.allow_headers,
        )

        @self.app.middleware("http")
        async def log_and_track_request(request: Request, call_next):
            start_time = datetime.now()
            response = await call_next(request)
            duration = (datetime.now() - start_time).total_seconds()
            track_request_duration(request.url.path, duration)
            return response

        # Rate limiting with configured values
        self.limiter = Limiter(key_func=get_remote_address)
        self.api_key_header = APIKeyHeader(name="X-API-Key")

    def _setup_startup(self):
        @self.app.on_event("startup")
        async def startup_event():
            storage = Storage(
                host=self.config.storage.host,
                port=self.config.storage.port,
                username=self.config.storage.username,
                password=self.config.storage.password,
            )

            config_manager = ConfigManager(storage, self.auth_manager)
            self.app.state.config_manager = config_manager

            logger.info("Application components initialized successfully")

    def _setup_routes(self):
        @self.app.get("/config/health")
        async def health_check():
            try:
                self.app.state.config_manager.storage.ping()
                return {"status": "healthy"}
            except Exception as e:
                logger.error(f"Health check failed: {str(e)}")
                return {"status": "unhealthy"}

        @self.app.get("/config/{path:path}")
        @self.limiter.limit(self.config.rate_limit_read)
        async def get_config(
            request: Request,
            path: str,
            environment: str = "prod",
            api_key: str = Depends(self.api_key_header),
        ) -> Dict:
            return await self._get_config(request, path, environment, api_key)

        @self.app.put("/config/{path:path}")
        @self.limiter.limit(self.config.rate_limit_write)
        async def update_config(
            request: Request,
            path: str,
            config: Dict,
            schema: Optional[Dict] = None,
            api_key: str = Depends(self.api_key_header),
        ):
            # print(f"api:VALIDATING CONFIG SCHEMA {schema}")
            # print(f"api:VALIDATING CONFIG DATA {config}")
            return await self._update_config(request, path, config, schema, api_key)

    async def _get_config(
        self, request: Request, path: str, environment: str, api_key: str
    ) -> Dict:
        try:
            if not request.app.state.config_manager.verify_api_key(api_key, ["read"]):
                raise HTTPException(status_code=403, detail="Invalid API key")

            config = request.app.state.config_manager.get_config(path, environment)
            if not config:
                raise HTTPException(status_code=404, detail="Configuration not found")
            return config
        except Exception as e:
            logger.error(f"Error getting config {path}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def _update_config(
        self,
        request: Request,
        path: str,
        config: Dict,
        schema: Optional[Dict],
        api_key: str,
    ):
        try:
            if not request.app.state.config_manager.verify_api_key(api_key, ["write"]):
                raise HTTPException(status_code=403, detail="Invalid API key")

            if schema and not validate_config_schema(config, schema):
                raise HTTPException(
                    status_code=400, detail="Invalid configuration format"
                )

            request.app.state.config_manager.update_config(path, config, api_key)
            increment_config_updates(path, "success")
            return {"status": "success"}
        except Exception as e:
            increment_config_updates(path, "error")
            logger.error(f"Error updating config {path}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
