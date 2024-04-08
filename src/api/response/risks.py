from pydantic import BaseModel, Field


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
        tuple_: tuple, factors: dict, types: dict, methods: dict
    ) -> ResponseRisk:
        return ResponseRisk(
            id=tuple_[0],
            name=tuple_[1],
            description=tuple_[2],
            comment=tuple_[3],
            factor=CommonObjFactory.get_from_tuple(factors.get(tuple_[4])),
            type=CommonObjFactory.get_from_tuple(types.get(tuple_[5])),
            method=CommonObjFactory.get_from_tuple(methods.get(tuple_[6])),
            probability=tuple_[7],
            impact=tuple_[8],
        )

    @classmethod
    def get_many_from_tuples(
        cls, tuples: list[tuple], factors: dict, types: dict, methods: dict
    ) -> list[ResponseRisk]:
        return [
            cls.get_from_tuple_with_dict(
                tuple_=tuple_, factors=factors, types=types, methods=methods
            )
            for tuple_ in tuples
        ]
