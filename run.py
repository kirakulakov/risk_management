import uvicorn

from src.internal.config.config import Settings

settings = Settings()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        port=settings.server.port,
        reload=settings.server.reload,
        workers=settings.server.workers,
        log_level=settings.server.log_level
    )
