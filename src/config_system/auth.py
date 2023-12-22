from datetime import datetime, timedelta
from typing import List, Optional

import jwt
from fastapi import HTTPException


class AuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.api_keys = {}
        self.token_blacklist = set()

    def create_api_key(self, roles: List[str]) -> str:
        api_key = jwt.encode(
            {"roles": roles, "exp": datetime.utcnow() + timedelta(days=30)},
            self.secret_key,
            algorithm="HS256",
        )
        self.api_keys[api_key] = roles
        return api_key

    def verify_api_key(
        self, api_key: str, required_roles: Optional[List[str]] = None
    ) -> bool:
        try:
            if api_key in self.token_blacklist:
                return False

            decoded = jwt.decode(api_key, self.secret_key, algorithms=["HS256"])
            roles = decoded.get("roles", [])

            if not required_roles:
                return True

            return any(role in roles for role in required_roles)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="API key has expired")
        except jwt.InvalidTokenError:
            return False

    def revoke_api_key(self, api_key: str):
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            self.token_blacklist.add(api_key)
