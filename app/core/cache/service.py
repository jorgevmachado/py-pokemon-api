from typing import Annotated

from fastapi import Query

from app.core.cache.manager import CacheManager
from app.core.logging import LoggingParams, log_service_success
from app.shared.schemas import FilterPage


class CacheService:
    def __init__(
        self,
        *,
        alias: str = 'default',
        prefix: str = 'cache',
        logger_params: LoggingParams,
    ):
        self.alias = alias
        self.prefix = prefix
        self.logger_params = logger_params
        self.cache = CacheManager()

    def build_key_list(
        self,
        page_filter: Annotated[FilterPage, Query()] = None,
    ):
        filter_page = FilterPage.build(page_filter)
        log_service_success(
            self.logger_params,
            operation='cache_build_key_list',
            message=f'The {self.alias} list cache key was successfully created.',
        )
        return self.cache.build_key(self.prefix, 'list', filter_page.model_dump())
