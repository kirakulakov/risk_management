from dataclasses import dataclass
from pydantic import Field, BaseModel, validator


class RequestSignUp(BaseModel):
    email: str = Field(...)
    password: str = Field(..., min_length=5)
    name: str = Field(...)
    projectName: str = Field(...)
    projectId: str = Field(...)
    description: str | None = Field(None)

    def to_dict(self):
        return {
            "name": self.name,
            "project_name": self.projectName,
            "project_id": self.projectId,
            "email": self.email,
            "password": self.password,
            "description": self.description,
        }

    @validator("email")
    def validate_email(cls, value):
        if len(value.split("@")[0]) < 2:
            raise ValueError(
                "Email must have at least 2 characters before '@'"
            )
        if len(value.split("@")[1].split(".")[0]) < 2:
            raise ValueError(
                "Email must have at least 2 characters between '@' and '.'"
            )
        if len(value.split("@")[1].split(".")[1]) < 2:
            raise ValueError("Email must have at least 2 characters after '.'")
        return value

    @validator("name")
    def validate_name_length(cls, name):
        if len(name) < 3 or len(name) > 260:
            raise ValueError("Name must be between 3 and 260 characters long")
        return name

    @validator("projectName")
    def validate_project_name_length(cls, projectName):
        if len(projectName) < 3 or len(projectName) > 260:
            raise ValueError(
                "Project name must be between 3 and 260 characters long"
            )
        return projectName

    @validator("projectId")
    def validate_project_id_length(cls, projectId):
        if len(projectId) != 3:
            raise ValueError("Project ID must be exactly 3 characters long")
        return projectId

    @validator("description", pre=True, always=True)
    def validate_description_length(cls, description):
        if description and len(description) > 2000:
            raise ValueError("Description must be up to 2000 characters long")
        return description


@dataclass
class RequestPatchAccount:
    email: str | None = Field(None)
    name: str | None = Field(None)
    projectName: str | None = Field(None)
    projectId: str | None = Field(None)
    description: str | None = Field(None)

    def to_dict(self):
        return {
            "name": self.name,
            "project_name": self.projectName,
            "project_id": self.projectId,
            "email": self.email,
            "description": self.description,
        }


@dataclass
class RequestPatchPassword:
    currentPassword: str = Field(...)
    newPassword: str = Field(...)


@dataclass
class RequestSignIn:
    email: str = Field(...)
    password: str = Field(...)
