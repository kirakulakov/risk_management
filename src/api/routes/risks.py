from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm

from src.api.response.empty import ResponseEmpty
from src.api.request.risks import RequestRisk
from src.api.response.risks import (
    CommonObj,
    CommonObjFactory,
    ResponseRisk,
    ResponseRiskFactory,
)
from src.db.db import Database
from src.api.depends import (
    get_account_service,
    get_auth_account_id_from_token,
    get_db,
)
from starlette import status
from src.api.request.account import (
    RequestSignUp,
)
from src.api.response.account import ResponseSignUp, Token
from src.services.account import AccountService

router = APIRouter()


@router.get("/types", response_model=list[CommonObj])
async def get_riks_types(
    db: Database = Depends(get_db),
):
    rows: list[tuple] = db.get_risk_types()
    return CommonObjFactory.get_many_from_tuples(rows)


@router.get("/factors", response_model=list[CommonObj])
async def get_riks_factors(
    db: Database = Depends(get_db),
):
    rows: list[tuple] = db.get_risk_factors()
    return CommonObjFactory.get_many_from_tuples(rows)


@router.get("/management-methods", response_model=list[CommonObj])
async def get_riks_management_methods(
    db: Database = Depends(get_db),
):
    rows: list[tuple] = db.get_risk_management_methods()
    return CommonObjFactory.get_many_from_tuples(rows)


@router.post("", response_model=ResponseRisk)
async def create_new_risk(
    request_model: RequestRisk,
    db: Database = Depends(get_db),
    auth_account_id: int = Depends(get_auth_account_id_from_token),
):
    exists = db.risk_id_exists(
        risk_id=request_model.id, auth_account_id=auth_account_id
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Risk id is already exist",
        )
    db.create_risk(
        request_model=request_model, auth_account_id=auth_account_id
    )
    factor = db.get_risk_factor_by_id(request_model.factor_id)
    type = db.get_risk_type_by_id(request_model.type_id)
    method = db.get_risk_management_method_by_id(request_model.method_id)

    new_risk = (
        request_model.id,
        request_model.name,
        request_model.description,
        request_model.comment,
        factor,
        type,
        method,
        request_model.probability,
        request_model.impact,
    )

    return ResponseRiskFactory.get_from_tuple(new_risk)


@router.get("", response_model=list[ResponseRisk])
async def get_risks(
    db: Database = Depends(get_db),
    auth_account_id: int = Depends(get_auth_account_id_from_token),
):
    factors = dict(db.get_risk_factors())
    types = dict(db.get_risk_types())
    methods = dict(db.get_risk_management_methods())
    rows: list[tuple] = db.get_risks(auth_account_id=auth_account_id)
    return ResponseRiskFactory.get_many_from_tuples(
        rows, factors=factors, types=types, methods=methods
    )


@router.delete("/{risk_id}", response_model=ResponseEmpty)
async def delete_risk(
    risk_id: int,
    db: Database = Depends(get_db),
    auth_account_id: int = Depends(get_auth_account_id_from_token),
):
    db.delete_risk(risk_id=risk_id, auth_account_id=auth_account_id)
    return ResponseEmpty()


@router.get("/new-id", response_model=str)
async def create_new_risk_id(
    db: Database = Depends(get_db),
    auth_account_id: int = Depends(get_auth_account_id_from_token),
):
    projectId = db.get_project_id_by_account_id(auth_account_id)
    try:
        last_id = int(
            db.get_last_risk_id(auth_account_id=auth_account_id)[-4::]
        )
    except TypeError:
        last_id = 0
    new_risk_id = f"{str(last_id+1).zfill(4)}"
    return f"{projectId}-{new_risk_id}"
