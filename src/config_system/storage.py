import etcd3
from typing import Optional

class Storage:
    def __init__(self, host: str = "localhost"):
        self.client = etcd3.client(host=host)
