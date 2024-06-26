import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Callable, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from starlette import status

from src.api.depends import (
    PagesPaginationParams,
    get_auth_account_id_from_token,
    get_db,
)
from src.api.request.risks import RequestRisk, RequestRiskUpdate
from src.api.response.empty import ResponseEmpty
from src.api.response.risks import (
    CommonObj,
    CommonObjFactory,
    ResponseRisk,
    ResponseRiskFactory, CommonObjWithValueFactory, CommonObjWithValue, ResponseRiskHistory, ResponseRiskHistoryFactory,
)
from src.db.db import Database
from src.internal.dto.common_object import CommonObjDTOFactory, CommonObjWithValueDTOFactory
from src.internal.dto.risks import RiskDTOFactory

router = APIRouter()


@router.get("/types", response_model=list[CommonObj])
async def get_risk_types(
        db: Database = Depends(get_db),
):
    rows: list[tuple] = db.get_risk_types()
    return CommonObjFactory.get_many_from_tuples(rows)


@router.get("/factors", response_model=list[CommonObj])
async def get_risk_factors(
        db: Database = Depends(get_db),
):
    rows: list[tuple] = db.get_risk_factors()
    return CommonObjFactory.get_many_from_tuples(rows)


@router.get("/management-methods", response_model=list[CommonObj])
async def get_risk_management_methods(
        db: Database = Depends(get_db),
):
    rows: list[tuple] = db.get_risk_management_methods()
    return CommonObjFactory.get_many_from_tuples(rows)


@router.get("/statuses", response_model=list[CommonObj])
async def get_risk_statuses(
        db: Database = Depends(get_db),
):
    rows: list[tuple] = db.get_risk_statuses()
    return CommonObjFactory.get_many_from_tuples(rows)


@router.get("/probabilities", response_model=list[CommonObjWithValue])
async def get_probabilities(
        db: Database = Depends(get_db),
):
    rows: list[tuple] = db.get_risk_probabilities()
    return CommonObjWithValueFactory.get_many_from_tuples(rows)


@router.get("/impacts", response_model=list[CommonObjWithValue])
async def get_risk_impacts(
        db: Database = Depends(get_db),
):
    rows: list[tuple] = db.get_risk_impacts()
    return CommonObjWithValueFactory.get_many_from_tuples(rows)


@router.post("", response_model=ResponseRisk)
async def create_new_risk(
        request_model: RequestRisk,
        db: Database = Depends(get_db),
        auth_account_id: int = Depends(get_auth_account_id_from_token),
):
    exists = db.risk_id_exists(risk_id=request_model.id, auth_account_id=auth_account_id)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Risk id is already exist",
        )
    # db.create_risk(request_model=request_model, auth_account_id=auth_account_id)
    # factor = db.get_risk_factor_by_id(request_model.factor_id)
    # type = db.get_risk_type_by_id(request_model.type_id)
    # method = db.get_risk_management_method_by_id(request_model.method_id)
    # risk_status = db.get_risk_status_by_id(1)
    # probability = db.get_risk_probability_by_id(request_model.probability_id)
    # impact = db.get_risk_impact_by_id(request_model.impact_id)

    tasks = []
    tasks.append(asyncio.create_task(fetch_data_no_factory(db.get_risk_factor_by_id, request_model.factor_id)))
    tasks.append(asyncio.create_task(fetch_data_no_factory(db.get_risk_type_by_id, request_model.type_id)))
    tasks.append(asyncio.create_task(fetch_data_no_factory(db.get_risk_management_method_by_id, request_model.method_id)))
    tasks.append(asyncio.create_task(fetch_data_no_factory(db.get_risk_status_by_id, 1)))
    tasks.append(asyncio.create_task(fetch_data_no_factory(db.get_risk_probability_by_id, request_model.probability_id)))
    tasks.append(asyncio.create_task(fetch_data_no_factory(db.get_risk_impact_by_id, request_model.impact_id)))
    tasks.append(asyncio.create_task(fetch_data_no_factory(db.create_risk, request_model, auth_account_id)))

    results: tuple = await asyncio.gather(*tasks, return_exceptions=True)
    factor, type, method, risk_status, probability, impact, _ = results

    new_risk = (
        request_model.id,
        request_model.name,
        request_model.description,
        request_model.comment,
        factor,
        type,
        method,
        probability,
        impact,
        risk_status
    )

    return ResponseRiskFactory.get_from_tuple(new_risk)


@router.get("", response_model=list[ResponseRisk])
async def get_risks(
        db: Database = Depends(get_db),
        auth_account_id: int = Depends(get_auth_account_id_from_token),
        pagination_params: PagesPaginationParams = Depends(),
):
    db_methods = [
        db.get_risk_factors,
        db.get_risk_types,
        db.get_risk_management_methods,
        db.get_risk_statuses,
        db.get_risk_probabilities,
        db.get_risk_impacts
    ]
    factory_methods = [CommonObjDTOFactory.get_many_from_tuples] * (len(db_methods) - 2)
    factory_methods.append(CommonObjWithValueDTOFactory.get_many_from_tuples)
    factory_methods.append(CommonObjWithValueDTOFactory.get_many_from_tuples)

    tasks = [asyncio.create_task(fetch_data(method, factory)) for method, factory in zip(db_methods, factory_methods)]

    tasks.append(
        asyncio.create_task(
            fetch_data(
                db.get_risks,
                RiskDTOFactory.get_many_from_tuples,
                auth_account_id=auth_account_id,
                limit=pagination_params.limit,
                offset=pagination_params.offset
            )
        )
    )

    results: tuple = await asyncio.gather(*tasks)

    factors, types, methods, statuses, probabilities, impacts, risks = results

    return ResponseRiskFactory.get_many_from_tuples(
        risks=risks, factors=factors, types=types, methods=methods,
        statuses=statuses, probabilities=probabilities, impacts=impacts)


@router.get("/{risk_id}/history", response_model=ResponseRiskHistory)
async def get_risk_history(
        risk_id: str,
        db: Database = Depends(get_db),
        auth_account_id: int = Depends(get_auth_account_id_from_token),
        pagination_params: PagesPaginationParams = Depends(),
):
    risk_exist = db.risk_id_exists(risk_id=risk_id, auth_account_id=auth_account_id)
    if not risk_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found",
        )

    risk_created_at: tuple[str] = db.get_risk_created_at_by_id(risk_id=risk_id, auth_account_id=auth_account_id)
    risk_created_at_timestamp = int(datetime.strptime(risk_created_at[0], "%Y-%m-%d %H:%M:%S").timestamp())

    history = db.get_risk_history_by_risk_id(
        risk_id=risk_id, limit=pagination_params.limit, offset=pagination_params.offset)

    return ResponseRiskHistoryFactory.get_from_tuple(risk_created_at=risk_created_at_timestamp, history=history)


async def fetch_data(db_method: Callable[..., Any], factory_method: Callable[[Any], Any], *args, **kwargs) -> Any:
    with ThreadPoolExecutor() as executor:
        future = executor.submit(db_method, *args, **kwargs)
        data = future.result()
        result = factory_method(data)
    return result


async def fetch_data_no_factory(db_method: Callable[..., Any], *args, **kwargs) -> Any:
    with ThreadPoolExecutor() as executor:
        future = executor.submit(db_method, *args, **kwargs)
        data = future.result()
    return data


@router.patch("", response_model=ResponseRisk)
async def patch_risk(
        request_model: RequestRiskUpdate,
        db: Database = Depends(get_db),
        auth_account_id: int = Depends(get_auth_account_id_from_token),
):
    risk_exist = db.risk_id_exists(risk_id=request_model.id, auth_account_id=auth_account_id)
    if not risk_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found",
        )
    db.update_risk_by_request_model(request_model=request_model, auth_account_id=auth_account_id)
    updated_risk = db.get_risk_by_id(risk_id=request_model.id, auth_account_id=auth_account_id)
    risk = RiskDTOFactory.from_tuple(updated_risk)

    db_methods = [
        db.get_risk_factors,
        db.get_risk_types,
        db.get_risk_management_methods,
        db.get_risk_statuses,
        db.get_risk_probabilities,
        db.get_risk_impacts
    ]
    factory_methods = [CommonObjDTOFactory.get_many_from_tuples] * (len(db_methods) - 2)
    factory_methods.append(CommonObjWithValueDTOFactory.get_many_from_tuples)
    factory_methods.append(CommonObjWithValueDTOFactory.get_many_from_tuples)
    tasks = [fetch_data(method, factory) for method, factory in zip(db_methods, factory_methods)]
    results: tuple = await asyncio.gather(*tasks)

    factors, types, methods, statuses, probabilities, impacts = results

    return ResponseRiskFactory.get_from_tuple_with_dict(
        risk=risk, factors=factors, types=types, methods=methods,
        statuses=statuses, probabilities=probabilities, impacts=impacts)


@router.delete("/{risk_id}", response_model=ResponseEmpty)
async def delete_risk(
        risk_id: str,
        background_tasks: BackgroundTasks,
        db: Database = Depends(get_db),
        auth_account_id: int = Depends(get_auth_account_id_from_token),
):
    background_tasks.add_task(db.delete_risk, risk_id=risk_id, auth_account_id=auth_account_id)
    return ResponseEmpty()


@router.get("/new-id", response_model=str)
async def create_new_risk_id(
        db: Database = Depends(get_db),
        auth_account_id: int = Depends(get_auth_account_id_from_token),
):
    projectId = db.get_project_id_by_account_id(auth_account_id)
    try:
        last_id = int(db.get_last_risk_id(auth_account_id=auth_account_id)[-4::])
    except TypeError:
        last_id = 0
    new_risk_id = f"{str(last_id + 1).zfill(4)}"
    return f"{projectId}-{new_risk_id}"
