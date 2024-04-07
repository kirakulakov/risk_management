import uvicorn

from src.internal.config.config import init_settings

settings = init_settings()

if __name__ == "__main__":
    uvicorn.run(
        "src.api.app.app:app",
        host=settings.server.host,
        port=settings.server.port,
        log_level=settings.server.log_level,
        reload=settings.server.reload,
        workers=settings.server.workers,
    )
