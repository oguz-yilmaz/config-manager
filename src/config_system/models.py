from datetime import datetime
from typing import Dict
from pydantic import BaseModel

class ConfigVersion(BaseModel):
    version: str
    data: Dict
