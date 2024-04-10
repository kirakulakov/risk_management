from pydantic import BaseModel, Field

from src.internal.dto.common_object import CommonObjDTO
from src.internal.dto.risks import RiskDTO


class CommonObj(BaseModel):
    id: int = Field(...)
    name: str = Field(...)


class CommonObjFactory:
    @staticmethod
    def get_from_tuple(tuple_: tuple) -> CommonObj:
        return CommonObj(
            id=tuple_[0],
            name=tuple_[1],
        )

    @staticmethod
    def get_from_dto(dto: CommonObjDTO) -> CommonObj:
        return CommonObj(id=dto.id, name=dto.name)

    @classmethod
    def get_many_from_tuples(cls, tuples: list[tuple]) -> list[CommonObj]:
        return [cls.get_from_tuple(tuple_) for tuple_ in tuples]


class ResponseRisk(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: str | None = Field(None)
    comment: str | None = Field(None)
    factor: CommonObj = Field(...)
    type: CommonObj = Field(...)
    method: CommonObj = Field(...)
    probability: int = Field(ge=0, le=10)
    impact: int = Field(ge=0, le=10)


class ResponseRiskFactory:
    @staticmethod
    def get_from_tuple(tuple_: tuple) -> ResponseRisk:
        return ResponseRisk(
            id=tuple_[0],
            name=tuple_[1],
            description=tuple_[2],
            comment=tuple_[3],
            factor=CommonObjFactory.get_from_tuple(tuple_[4]),
            type=CommonObjFactory.get_from_tuple(tuple_[5]),
            method=CommonObjFactory.get_from_tuple(tuple_[6]),
            probability=tuple_[7],
            impact=tuple_[8],
        )

    @staticmethod
    def get_from_tuple_with_dict(
            risk: RiskDTO, factors: list[CommonObjDTO], types: list[CommonObjDTO], methods: list[CommonObjDTO]
    ) -> ResponseRisk:
        factor_ = None
        type_ = None
        method_ = None

        for factor in factors:
            if factor.id == risk.factor_id:
                factor_ = factor
                break

        for type in types:
            if type.id == risk.type_id:
                type_ = type
                break

        for method in methods:
            if method.id == risk.method_id:
                method_ = method
                break

        return ResponseRisk(
            id=risk.id,
            name=risk.name,
            description=risk.description,
            comment=risk.comment,
            factor=CommonObjFactory.get_from_dto(factor_),
            type=CommonObjFactory.get_from_dto(type_),
            method=CommonObjFactory.get_from_dto(method_),
            probability=risk.probability,
            impact=risk.impact,
        )

    @classmethod
    def get_many_from_tuples(
            cls, risks: list[RiskDTO], factors: list[CommonObjDTO], types: list[CommonObjDTO],
            methods: list[CommonObjDTO]
    ) -> list[ResponseRisk]:
        return [
            cls.get_from_tuple_with_dict(risk=risk, factors=factors, types=types, methods=methods) for risk in risks
        ]
