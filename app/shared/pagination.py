from typing import Annotated, Optional

from fastapi import Query
from fastapi_pagination import LimitOffsetPage, LimitOffsetParams

from app.shared.schemas import FilterPage


def limit_paginate(limit: Optional[int] = None, max_limit: int = 100) -> int:
    if not limit:
        return max_limit
    return min(limit, max_limit)


def is_paginate(page_filter: Annotated[FilterPage, Query()] = None) -> bool:
    if not page_filter:
        return False
    has_offset = page_filter.offset is not None
    has_limit = page_filter.limit is not None
    return has_offset and has_limit


def exception_pagination(page_filter: Annotated[FilterPage, Query()] = None):
    try:
        if is_paginate(page_filter):
            params = LimitOffsetParams(
                limit=limit_paginate(page_filter.limit),
                offset=page_filter.offset,
            )
            return LimitOffsetPage.create([], total=0, params=params)
    except Exception as e:
        print(f'# => exception_pagination => error => {e}')
        return []
    return []
