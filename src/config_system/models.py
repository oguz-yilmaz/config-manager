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
