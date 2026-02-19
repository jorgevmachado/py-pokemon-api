from pydantic import BaseModel, ConfigDict, EmailStr


class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    token_type: str
    access_token: str


class Login(BaseModel):
    email: EmailStr
    password: str
