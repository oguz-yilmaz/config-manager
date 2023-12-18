from fastapi import FastAPI
from .config_manager import ConfigManager

app = FastAPI()
@app.get("/config/{path:path}")
async def get_config(path: str):
    return {"path": path}
@app.get("/health")
async def health_check():
    try:
        storage.ping()
        return {"status": "healthy"}
    except:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy"}
        )
