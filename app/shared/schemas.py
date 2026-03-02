from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str


class FilterPage(BaseModel):
    offset: Optional[int] = Field(None, ge=0)
    limit: Optional[int] = Field(None, ge=1)
