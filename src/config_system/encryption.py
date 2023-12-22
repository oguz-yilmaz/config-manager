import os
from base64 import b64decode, b64encode
from typing import Optional

from cryptography.fernet import Fernet


class EncryptionManager:
    def __init__(self, key: Optional[bytes] = None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_value(self, value: str) -> str:
        encrypted = self.cipher.encrypt(value.encode())
        return b64encode(encrypted).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        try:
            decoded = b64decode(encrypted_value)
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt value: {str(e)}")

    @classmethod
    def from_environment(cls, env_var: str = "ENCRYPTION_KEY"):
        key = os.environ.get(env_var)
        if not key:
            raise ValueError(
                f"Missing encryption key in environment variable {env_var}"
            )
        return cls(key.encode())
