import logging
from typing import Annotated, Optional

from fastapi import Query
from fastapi_pagination import LimitOffsetParams

from app.core.exceptions import handle_service_exception
from app.core.pagination.schemas import CustomLimitOffsetPage
from app.shared.schemas import FilterPage

logger = logging.getLogger(__name__)


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
            return CustomLimitOffsetPage.create([], total=0, params=params)
    except Exception as exception:
        handle_service_exception(
            logger=logger,
            exception=exception,
            service='exception_pagination',
            operation='exception_pagination',
            raise_exception=False,
        )
        return []
    return []
