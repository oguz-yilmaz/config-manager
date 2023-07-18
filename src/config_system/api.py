from fastapi import FastAPI
from .config_manager import ConfigManager

app = FastAPI()
@app.get("/config/{path:path}")
async def get_config(path: str):
    return {"path": path}
