from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import CapturedPokemon, Pokedex
from app.shared.gender_enum import GenderEnum
from app.shared.role_enum import RoleEnum
from app.shared.status_enum import StatusEnum


class CreateUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    role: RoleEnum = Field(default=RoleEnum.USER)
    gender: GenderEnum
    status: StatusEnum = Field(default=StatusEnum.INCOMPLETE)
    password: str
    date_of_birth: datetime
    pokeballs: int = Field(default=5)
    capture_rate: int = Field(default=45)


class UserPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: RoleEnum
    name: str
    email: EmailStr
    gender: GenderEnum
    status: StatusEnum
    pokeballs: int
    capture_rate: int
    date_of_birth: datetime
    total_authentications: int
    last_authentication_at: datetime | None
    authentication_success: int
    authentication_failures: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    pokedex: list['Pokedex'] | None
    captured_pokemons: list['CapturedPokemon'] | None


class FindOneUserSchemaParams(BaseModel):
    id: str | None = None
    email: str | None = None
