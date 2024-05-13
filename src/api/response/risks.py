from pydantic import BaseModel, Field

from src.internal.dto.common_object import CommonObjDTO, CommonObjWithValueDTO
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


class CommonObjWithValue(CommonObj):
    value: int | float = Field(...)


class CommonObjWithValueFactory:
    @staticmethod
    def get_from_tuple(tuple_: tuple) -> CommonObjWithValue:
        return CommonObjWithValue(
            id=tuple_[0],
            name=tuple_[1],
            value=tuple_[2],
        )

    @staticmethod
    def get_from_dto(dto: CommonObjWithValueDTO) -> CommonObjWithValue:
        return CommonObjWithValue(id=dto.id, name=dto.name, value=dto.value)

    @classmethod
    def get_many_from_tuples(cls, tuples: list[tuple]) -> list[CommonObjWithValue]:
        return [cls.get_from_tuple(tuple_) for tuple_ in tuples]


class ResponseRisk(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: str | None = Field(None)
    comment: str | None = Field(None)
    factor: CommonObj = Field(...)
    type: CommonObj = Field(...)
    method: CommonObj = Field(...)
    probability: CommonObjWithValue | None = Field(None)
    impact: CommonObjWithValue | None = Field(None)
    status: CommonObj = Field(...)


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
            probability=CommonObjWithValueFactory.get_from_tuple(tuple_[7]) if tuple_[7] else None,
            impact=CommonObjWithValueFactory.get_from_tuple(tuple_[8]) if tuple_[8] else None,
            status=CommonObjFactory.get_from_tuple(tuple_[9]),
        )

    @staticmethod
    def get_from_tuple_with_dict(
            risk: RiskDTO, factors: list[CommonObjDTO], types: list[CommonObjDTO], methods: list[CommonObjDTO],
            statuses: list[CommonObjDTO], probabilities: list[CommonObjWithValueDTO],
            impacts: list[CommonObjWithValueDTO]
    ) -> ResponseRisk:
        factor_ = None
        type_ = None
        method_ = None
        status_ = None
        probability_ = None
        impact_ = None

        for status in statuses:
            if status.id == risk.status_id:
                status_ = status
                break

        for probability in probabilities:
            if risk.probability_id is None:
                break
            if probability.id == risk.probability_id:
                probability_ = probability
                break

        for impact in impacts:
            if risk.impact_id is None:
                break
            if impact.id == risk.impact_id:
                impact_ = impact
                break


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
            probability=CommonObjWithValueFactory.get_from_dto(probability_) if probability_ else None,
            impact=CommonObjWithValueFactory.get_from_dto(impact_) if impact_ else None,
            status=CommonObjFactory.get_from_dto(status_),
        )

    @classmethod
    def get_many_from_tuples(
            cls, risks: list[RiskDTO], factors: list[CommonObjDTO], types: list[CommonObjDTO],
            methods: list[CommonObjDTO], statuses: list[CommonObjDTO], probabilities: list[CommonObjWithValueDTO],
            impacts: list[CommonObjWithValueDTO]
    ) -> list[ResponseRisk]:
        return [
            cls.get_from_tuple_with_dict(risk=risk, factors=factors, types=types, methods=methods, statuses=statuses,
                                        probabilities=probabilities, impacts=impacts) for risk in risks
        ]
