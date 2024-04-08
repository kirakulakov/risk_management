from pydantic import BaseModel, Field, validator


class RequestRisk(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: str | None = Field(None)
    comment: str | None = Field(None)
    factor_id: int = Field(...)
    type_id: int = Field(...)
    method_id: int = Field(...)
    probability: int = Field(ge=0, le=10)
    impact: int = Field(ge=0, le=10)

    @validator("description", pre=True, always=True)
    def validate_description_length(cls, description):
        if description and len(description) > 2000:
            raise ValueError("Description must be up to 2000 characters long")
        return description

    @validator("comment", pre=True, always=True)
    def validate_description_length(cls, comment):
        if comment and len(comment) > 2000:
            raise ValueError("Description must be up to 2000 characters long")
        return comment

    @validator("name", pre=True, always=True)
    def validate_description_length(cls, name):
        if len(name) < 3 or len(name) > 260:
            raise ValueError("Name must be between 3 and 260 characters long")
        return name
