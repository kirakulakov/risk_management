from pydantic import BaseModel, Field


class Account(BaseModel):
    id: int = Field(...)
    email: str = Field(...)
    name: str = Field(...)
    projectName: str = Field(...)
    projectId: str = Field(...)
    description: str | None = Field(None)


class ResponseAccount(Account):
    pass


class Token(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(default="bearer")


class ResponseSignUp(ResponseAccount, Token):
    pass
