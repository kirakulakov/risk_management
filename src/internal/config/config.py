from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

settings = ...


class Server(BaseModel):
    title: str = "Risk Management API"
    host: str
    port: int
    log_level: str
    reload: bool
    workers: int
    docs_url: str
    openapi_url: str
    env: str


class DB(BaseModel):
    path: str


class Security(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="risk_management_",
        env_nested_delimiter="__",
    )

    server: Server
    db: DB
    security: Security


def init_settings() -> Settings:
    return Settings()
