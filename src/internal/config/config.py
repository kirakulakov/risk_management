import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Server(BaseModel):
    title: str = "Risk Management API"
    host: str
    port: int
    log_level: str | None = "info"
    reload: bool = False
    workers: int = 1
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    env: str = "local"


class DB(BaseModel):
    path: str


class Security(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_prefix="risk_management_",
        env_nested_delimiter="__",
    )

    server: Server
    db: DB
    security: Security
