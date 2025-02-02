from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ConfigVersion(BaseModel):
    version: str
    data: Dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
    comment: Optional[str] = None
    user: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class AuditLog(BaseModel):
    id: Optional[int] = None
    action: str
    path: str
    user: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ConfigSchema(BaseModel):
    type: str
    properties: Dict
    required: List[str] = Field(default_factory=list)
    additionalProperties: bool = False


# Configuration models


class CORSConfig(BaseModel):
    allow_origins: List[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


class StorageConfig(BaseModel):
    host: str = "localhost"
    port: int = 2379
    username: Optional[str] = None
    password: Optional[str] = None


class SecurityConfig(BaseModel):
    secret_key: str
    token_expiry: int = 3600  # seconds
    min_password_length: int = 8


class AppConfig(BaseModel):
    cors: CORSConfig = CORSConfig()
    storage: StorageConfig = StorageConfig()
    security: SecurityConfig
    rate_limit_read: str = "100/minute"
    rate_limit_write: str = "20/minute"
