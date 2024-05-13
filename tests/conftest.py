import asyncio
import logging
import os
from sqlite3 import Cursor, Connection
from typing import Generator

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.api.routes.routers import router as account_router
from src.db.db import Database
from src.internal.config.config import Settings
from src.internal.log.log import logger as _logger


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["ENV_FILE"] = ".env.test"
    if not os.path.exists(".env.test"):
        raise FileExistsError(".env.test does not exist")


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings(set_env) -> Settings:
    settings = Settings()
    settings.db.path = "database.test.db"
    return settings


@pytest.fixture(scope="session")
def logger() -> logging.Logger:
    return _logger


@pytest.fixture(scope="session")
def database(settings, logger) -> Database:
    db = Database(path=settings.db.path, logger=logger)
    db.drop_tables_with_dynamic_data()
    db.create_tables_and_fill_data()
    return db


@pytest.fixture(scope="session")
def cursor(database) -> Cursor:
    return database.cursor


@pytest.fixture(scope="session")
def connection(database) -> Connection:
    return database.connection


@pytest.fixture(scope="session")
def app(settings, database, logger) -> FastAPI:
    app = FastAPI(
        title=settings.server.title,
        docs_url=settings.server.docs_url,
        openapi_url=settings.server.openapi_url)

    @app.middleware("http")
    async def http_middleware(request: Request, call_next):
        request.state.db = database
        request.state.settings = settings
        request.state.logger = logger

        response = await call_next(request)
        return response

    app.include_router(account_router)

    return app


@pytest.fixture(scope="session")
def client(app, database) -> Generator:
    with TestClient(app) as client:
        yield client
        database.drop_tables_with_dynamic_data()
