from fastapi import FastAPI, Request

from src.api.routes.routers import router as account_router
from src.db.db import Database
from src.internal.config.config import Settings
from src.internal.log.log import logger as _logger

logger = _logger

settings = Settings()

db = Database(path=settings.db.path, logger=logger)

app = FastAPI(
    title=settings.server.title,
    docs_url=settings.server.docs_url,
    openapi_url=settings.server.openapi_url
)

@app.middleware("http")
async def http_middleware(request: Request, call_next):
    logger.info(
        f"Processing request:"
        f" path={request.url.path},"
        f" method={request.method},"
        f" headers={request.headers}"
    )

    request.state.db = db
    request.state.settings = settings
    request.state.logger = logger

    response = await call_next(request)
    return response


app.include_router(account_router)

logger.info("API initialized")
