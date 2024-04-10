import logging
import sys
from typing import Annotated

from fastapi import Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette import status
from starlette.requests import Request

from src.db.db import Database
from src.internal.config.config import Settings
from src.services.account import AccountService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/sign-in")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db(request: Request) -> Database:
    return request.state.db


def get_settings(request: Request) -> Settings:
    return request.state.settings


def get_logger(request: Request) -> logging.Logger:
    return request.state.logger


def decode_token(token: str, settings: Settings) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.security.secret_key,
            algorithms=[settings.security.algorithm],
        )
        id_: int = int(payload.get("sub"))
    except (JWTError, AttributeError, ValueError) as e:
        raise HTTPException(status_code=401, detail="Authorization failed!")

    return id_


async def get_auth_account_id_from_token(
        token: Annotated[str, Depends(oauth2_scheme)], settings=Depends(get_settings)) -> int:
    user = decode_token(token=token, settings=settings)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_account_service(
        logger=Depends(get_logger),
        settings=Depends(get_settings),
        db=Depends(get_db)
) -> AccountService:
    return AccountService(
        db=db,
        pwd_context=pwd_context,
        security=settings.security,
        oauth2_scheme=oauth2_scheme,
        logger=logger
    )


class PagesPaginationParams:
    def __init__(
            self,
            limit: int = Query(50, ge=0, le=1_000),
            offset: int = Query(0, ge=0, alias="skip"),
    ) -> None:
        self.limit = limit
        self.offset = offset
