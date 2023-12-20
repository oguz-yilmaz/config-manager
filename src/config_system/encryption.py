from cryptography.fernet import Fernet
from base64 import b64encode, b64decode

def encrypt_value(key: bytes, value: str) -> str:
    f = Fernet(key)
    return b64encode(f.encrypt(value.encode())).decode()
