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
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/config/{path:path}")
@limiter.limit("100/minute")
async def get_config(request: Request, path: str):
    pass
