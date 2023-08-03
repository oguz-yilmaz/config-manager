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
