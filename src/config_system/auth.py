from typing import List

class AuthManager:
    def __init__(self):
        self.api_keys = {}
    def verify_key(self, api_key: str) -> bool:
        return api_key in self.api_keys
from fastapi.security import APIKeyHeader
from typing import Optional

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    if not is_valid_key(api_key):
        raise HTTPException(status_code=403)
    return api_key
