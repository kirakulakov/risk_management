from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.depends import get_account_service
from src.api.request.account import (
    RequestSignUp
)
from src.api.response.account import ResponseSignUp, Token
from src.services.account import AccountService

router = APIRouter()


@router.post("/sign-up", response_model=ResponseSignUp)
async def sign_up(
        request_model: RequestSignUp,
        auth_service: AccountService = Depends(get_account_service),
):
    return await auth_service.sign_up(account_in_db=request_model)


@router.post("/sign-in", response_model=Token)
async def signin(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: AccountService = Depends(get_account_service)
):
    return await auth_service.sign_in(email=form_data.username, password=form_data.password)
