from typing import Any, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):
    message: str


TFilterPage = TypeVar('TFilterPage', bound='FilterPage')


class FilterPage(BaseModel):
    model_config = ConfigDict(extra='allow')

    offset: Optional[int] = Field(None, ge=0)
    limit: Optional[int] = Field(None, ge=1)

    def with_updates(self, **updates: Any) -> TFilterPage:
        payload = self.model_dump(exclude_none=True)
        payload.update({key: value for key, value in updates.items() if value is not None})
        return self.__class__.model_validate(payload)

    @classmethod
    def build(
        cls: type[TFilterPage], page_filter: TFilterPage | None = None, **updates: Any
    ) -> TFilterPage:
        payload = page_filter.model_dump(exclude_none=True) if page_filter is not None else {}
        payload.update({key: value for key, value in updates.items() if value is not None})
        return cls.model_validate(payload)
