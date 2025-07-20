from pydantic import BaseModel, ConfigDict


class TokenBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TokenAccess(TokenBase):
    access_token: str


class Token(TokenAccess):
    refresh_token: str
