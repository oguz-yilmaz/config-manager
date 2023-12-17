import etcd3
from typing import Optional

class Storage:
    def __init__(self, host: str = "localhost"):
        self.client = etcd3.client(host=host)
    def get_config(self, path: str) -> Optional[dict]:
        value = self.client.get(f"/config/{path}")
        return value[0] if value[0] else None
    def put_config(self, path: str, data: dict):
        self.client.put(f"/config/{path}", str(data))
class StorageError(Exception):
    pass

def safe_put(self, key: str, value: str) -> bool:
    try:
        self.client.put(key, value)
        return True
    except Exception as e:
        logger.error(f"Storage error: {str(e)}")
        raise StorageError(str(e))
