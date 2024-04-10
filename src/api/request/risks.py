from pydantic import BaseModel, Field, field_validator


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

    @field_validator("description", mode='before')
    def validate_description_length(cls, description):
        if description and len(description) > 2000:
            raise ValueError("Description must be up to 2000 characters long")
        return description

    @field_validator("comment", mode='before')
    def validate_comment_length(cls, comment):
        if comment and len(comment) > 2000:
            raise ValueError("Description must be up to 2000 characters long")
        return comment

    @field_validator("name", mode='before')
    def validate_name_length(cls, name):
        if len(name) < 3 or len(name) > 260:
            raise ValueError("Name must be between 3 and 260 characters long")
        return name
