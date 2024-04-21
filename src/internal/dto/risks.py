from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class RiskDTO:
    id: str
    name: str
    factor_id: int
    type_id: int
    method_id: int
    probability: int
    impact: int
    description: str | None = None
    comment: str | None = None


class RiskDTOFactory:
    @staticmethod
    def from_tuple(tuple_: tuple) -> RiskDTO:
        return RiskDTO(
            id=tuple_[0],
            name=tuple_[1],
            description=tuple_[2],
            comment=tuple_[3],
            factor_id=tuple_[4],
            type_id=tuple_[5],
            method_id=tuple_[6],
            probability=tuple_[7],
            impact=tuple_[8],
        )

    @classmethod
    def get_many_from_tuples(cls, tuples: list[tuple]) -> list[RiskDTO]:
        return [cls.from_tuple(tuple_) for tuple_ in tuples]
