import datetime
import logging
from dataclasses import dataclass

from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from starlette import status

from src.api.request.account import (
    RequestPatchAccount,
    RequestPatchPassword,
    RequestSignUp,
)
from src.api.response.account import ResponseAccount, ResponseSignUp, Token
from src.db.db import Database
from src.internal.config.config import Security


@dataclass
class User:
    id: int
    email: str
    name: str
    password: str
    project_name: str
    project_id: str
    description: str | None = None


class AccountService:
    def __init__(
            self,
            db: Database,
            pwd_context: CryptContext,
            security: Security,
            logger: logging.Logger,
            oauth2_scheme,
    ) -> None:
        self.database = db
        self.pwd_context = pwd_context
        self.access_token_expire_minutes = security.access_token_expire_minutes
        self.secret_key = security.secret_key
        self.algorithm = security.algorithm
        self.oauth2_scheme = oauth2_scheme
        self.logger = logger

    def get_account_from_db(self, email: str):

        account = self.database.fetch_account_by_email(email)
        if account:
            return ResponseAccount(**account)

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify(self, *, password: str, user_hashed_password: str) -> bool:
        if not self.pwd_context.verify(password, user_hashed_password):
            return False

        return True

    def create_access_token(self, data: dict, expires_delta: datetime.timedelta | None = None) -> str:
        expire = datetime.datetime.now(datetime.timezone.utc) + (
                expires_delta or datetime.timedelta(minutes=self.access_token_expire_minutes)
        )
        to_encode = data | {"exp": expire}
        encoded_jwt = jwt.encode(to_encode, self.secret_key, self.algorithm)
        return encoded_jwt

    async def sign_in(self, email: str, password: str) -> Token:
        user = await self.get_user_by_email(email=email)

        if not self.verify(password=password, user_hashed_password=user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        access_token_expires = datetime.timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
        return Token(access_token=access_token, token_type="bearer")

    async def sign_up(self, account_in_db: RequestSignUp) -> ResponseSignUp:

        email_already_registered = self.database.fetch_account_by_email(email=account_in_db.email)
        if email_already_registered:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Login is already registered in the system!",
            )

        hashed_password = self.hash_password(account_in_db.password)
        account_id = self.database.create_account(
            name=account_in_db.name,
            email=account_in_db.email,
            project_name=account_in_db.projectName,
            project_id=account_in_db.projectId,
            description=account_in_db.description,
            password=hashed_password,
        )
        access_token_expires = datetime.timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": str(account_id)},
            expires_delta=access_token_expires,
        )
        return ResponseSignUp(
            id=account_id,
            email=account_in_db.email,
            name=account_in_db.name,
            projectName=account_in_db.projectName,
            projectId=account_in_db.projectId,
            description=account_in_db.description,
            password=hashed_password,
            access_token=access_token,
        )

    async def update_account(self, request_model: RequestPatchAccount, auth_account_id: int) -> ResponseAccount:
        if request_model.email is not None:
            email_already_registered = self.database.fetch_account_by_email(email=request_model.email)

            if email_already_registered:
                email_by_id = self.database.fetch_email_by_id(auth_account_id)
                if email_by_id[0] != request_model.email:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Login is already registered in the system!",
                    )

        self.database.update_account(
            account_id=auth_account_id,
            email=request_model.email,
            name=request_model.name,
            projectName=request_model.projectName,
            projectId=request_model.projectId,
            description=request_model.description,
        )
        user = await self.get_user_by_id(auth_account_id=auth_account_id)
        return ResponseAccount(
            id=auth_account_id,
            email=user.email,
            name=user.name,
            projectName=user.project_name,
            projectId=user.project_id,
            description=user.description,
        )

    async def get_user_by_id(self, auth_account_id: int) -> User:
        user = self.database.fetch_account_by_id(account_id=auth_account_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return User(
            id=user[0],
            email=user[1],
            name=user[2],
            password=user[3],
            project_name=user[4],
            project_id=user[5],
            description=user[6],
        )

    async def get_user_by_email(self, email: str) -> User:
        user = self.database.fetch_account_by_email(email=email)
        if not user:
            self.logger.warning("User not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return User(
            id=user[0],
            email=user[1],
            name=user[2],
            password=user[3],
            project_name=user[4],
            project_id=user[5],
            description=user[6],
        )

    async def patch_password(self, request_model: RequestPatchPassword, auth_account_id: int) -> None:
        user = await self.get_user_by_id(auth_account_id=auth_account_id)

        if not self.verify(
                password=request_model.currentPassword,
                user_hashed_password=user.password,
        ):
            raise HTTPException(status_code=400, detail="Incorrect current password")

        hashed_new_password = self.hash_password(request_model.newPassword)
        self.database.update_account_password(account_id=auth_account_id, password=hashed_new_password)
        return
