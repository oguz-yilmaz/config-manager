from datetime import datetime
from typing import Dict
from pydantic import BaseModel

class ConfigVersion(BaseModel):
    version: str
    data: Dict
class AuditLog(BaseModel):
    action: str
    timestamp: datetime
    user: str
class Version:
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
