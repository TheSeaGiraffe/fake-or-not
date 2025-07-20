from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str
    name: str


class UserOut(UserBase):
    id: int


class UserCreate(UserBase):
    password: str
