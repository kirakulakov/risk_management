from pydantic import BaseModel, Field


class ResponseEmpty(BaseModel):
    result: bool = Field(True)
