from typing import List

class AuthManager:
    def __init__(self):
        self.api_keys = {}
    def verify_key(self, api_key: str) -> bool:
        return api_key in self.api_keys
