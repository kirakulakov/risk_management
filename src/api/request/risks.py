from pydantic import BaseModel, Field, field_validator


class RequestRisk(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: str | None = Field(None)
    comment: str | None = Field(None)
    factor_id: int = Field(...)
    type_id: int = Field(...)
    method_id: int = Field(...)
    probability_id: int = Field(...)
    impact_id: int = Field(...)

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


class RequestRiskUpdate(BaseModel):
    id: str = Field(...)
    name: str | None = Field(None)
    description: str | None = Field(None)
    comment: str | None = Field(None)
    factor_id: int | None = Field(None)
    type_id: int | None = Field(None)
    method_id: int | None = Field(None)
    probability_id: int | None = Field(None)
    impact_id: int | None = Field(None)
    status_id: int | None = Field(None)

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
        if name:
            if len(name) < 3 or len(name) > 260:
                raise ValueError("Name must be between 3 and 260 characters long")
        return name
