from fastapi import FastAPI, Request

from src.api.routes.routers import router as account_router
from src.db import db
from src.db.db import init_db
from src.internal.config import config
from src.internal.config.config import init_settings
from src.internal.log.log import logger

logger.info("Initializing app")


settings = init_settings()
config.settings = settings
db.db = init_db(settings.db.path)


def init_app_with_dependencies() -> FastAPI:

    app = FastAPI(
        title=settings.server.title,
        docs_url=settings.server.docs_url,
        openapi_url=settings.server.openapi_url,
    )

    app.include_router(account_router)

    logger.info("App initialized")
    return app


app = init_app_with_dependencies()


@app.middleware("http")
async def http_middleware(request: Request, call_next):
    logger.info(
        f"Processing request: path={request.url.path}, method={request.method}, headers={request.headers}"
    )
    response = await call_next(request)
    return response
