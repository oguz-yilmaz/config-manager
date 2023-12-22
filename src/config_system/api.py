import logging
from datetime import datetime
from typing import Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config_manager import ConfigManager
from .metrics import increment_config_updates, track_request_duration
from .models import AuditLog, ConfigVersion
from .storage import Storage
from .validation import validate_config_schema

logger = logging.getLogger(__name__)

app = FastAPI(title="Configuration Management System")
limiter = Limiter(key_func=get_remote_address)
api_key_header = APIKeyHeader(name="X-API-Key")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_and_track_request(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start_time).total_seconds()
    track_request_duration(request.url.path, duration)
    return response


@app.get("/config/{path:path}")
@limiter.limit("100/minute")
async def get_config(
    request: Request,
    path: str,
    environment: str = "prod",
    api_key: str = Depends(api_key_header),
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


@app.put("/config/{path:path}")
@limiter.limit("20/minute")
async def update_config(
    request: Request,
    path: str,
    config: Dict,
    schema: Optional[Dict] = None,
    api_key: str = Depends(api_key_header),
):
    try:
        if not request.app.state.config_manager.verify_api_key(api_key, ["write"]):
            raise HTTPException(status_code=403, detail="Invalid API key")

        if schema and not validate_config_schema(config, schema):
            raise HTTPException(status_code=400, detail="Invalid configuration format")

        request.app.state.config_manager.update_config(path, config, api_key)
        increment_config_updates(path, "success")
        return {"status": "success"}
    except Exception as e:
        increment_config_updates(path, "error")
        logger.error(f"Error updating config {path}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    try:
        app.state.config_manager.storage.ping()
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy"}
