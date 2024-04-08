from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette import status

from src.db.db import init_db, Database
from src.internal.config.config import init_settings
from src.services.account import AccountService

settings = init_settings()
db = init_db(settings.db.path)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/sign-in")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def decode_token(token) -> int:
    payload = jwt.decode(
        token,
        settings.security.secret_key,
        algorithms=[settings.security.algorithm],
    )

    i = payload.get("sub")
    print(i)
    try:
        payload = jwt.decode(
            token,
            settings.security.secret_key,
            algorithms=[settings.security.algorithm],
        )
        id_: int = int(payload.get("sub"))
    except (JWTError, AttributeError, ValueError):
        raise HTTPException(status_code=401, detail="Authorization failed!")

    return id_


async def get_auth_account_id_from_token(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_account_service() -> AccountService:
    return AccountService(
        db=db,
        pwd_context=pwd_context,
        security=settings.security,
        oauth2_scheme=oauth2_scheme,
    )


def get_db() -> Database:
    return db
