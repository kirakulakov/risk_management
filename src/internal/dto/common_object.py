from dataclasses import dataclass


@dataclass
class CommonObjDTO:
    id: int
    name: str


class CommonObjDTOFactory:
    @staticmethod
    def get_from_tuple(tuple_: tuple) -> CommonObjDTO:
        return CommonObjDTO(
            id=tuple_[0],
            name=tuple_[1],
        )

    @classmethod
    def get_many_from_tuples(cls, tuples: list[tuple]) -> list[CommonObjDTO]:
        return [cls.get_from_tuple(tuple_) for tuple_ in tuples]


@dataclass
class CommonObjWithValueDTO(CommonObjDTO):
    value: int | float


class CommonObjWithValueDTOFactory:
    @staticmethod
    def get_from_tuple(tuple_: tuple) -> CommonObjWithValueDTO:
        return CommonObjWithValueDTO(
            id=tuple_[0],
            name=tuple_[1],
            value=tuple_[2],
        )

    @classmethod
    def get_many_from_tuples(cls, tuples: list[tuple]) -> list[CommonObjWithValueDTO]:
        return [cls.get_from_tuple(tuple_) for tuple_ in tuples]
