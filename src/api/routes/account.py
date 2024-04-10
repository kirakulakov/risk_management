from fastapi import APIRouter, Depends

from src.api.depends import get_account_service, get_auth_account_id_from_token
from src.api.request.account import (
    RequestPatchAccount,
    RequestPatchPassword,
)
from src.api.response.account import ResponseAccount
from src.api.response.empty import ResponseEmpty
from src.services.account import AccountService

router = APIRouter()


@router.patch("", response_model=ResponseAccount)
async def update_account(
    request_model: RequestPatchAccount,
    auth_service: AccountService = Depends(get_account_service),
    auth_account_id: int = Depends(get_auth_account_id_from_token),
):

    return await auth_service.update_account(auth_account_id=auth_account_id, request_model=request_model)


@router.patch("/password", response_model=ResponseEmpty)
async def change_password(
    request_model: RequestPatchPassword,
    auth_service: AccountService = Depends(get_account_service),
    auth_account_id: int = Depends(get_auth_account_id_from_token),
):

    await auth_service.patch_passwrod(auth_account_id=auth_account_id, request_model=request_model)
    return ResponseEmpty()
