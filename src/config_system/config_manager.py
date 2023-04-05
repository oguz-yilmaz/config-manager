from typing import Optional
from .storage import Storage

class ConfigManager:
    def __init__(self, storage: Storage):
        self.storage = storage
