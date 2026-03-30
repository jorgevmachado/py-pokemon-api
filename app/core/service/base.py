from http import HTTPStatus
from typing import Annotated, Generic, TypeVar

from fastapi import HTTPException, Query

from app.core.cache.service import CacheService
from app.core.exceptions import handle_service_exception
from app.core.logging import LoggingParams, log_service_success
from app.shared.schemas import FilterPage
from app.shared.utils.pagination import exception_pagination
from app.shared.utils.string import is_valid_uuid

RepositoryT = TypeVar('RepositoryT')
ModelT = TypeVar('ModelT')
UpdateSchemaT = TypeVar('UpdateSchemaT')


class BaseService(Generic[RepositoryT, ModelT]):
    def __init__(
        self,
        alias: str,
        repository: RepositoryT,
        logger_params: LoggingParams,
        cache_prefix: str | None = None,
    ):
        prefix = cache_prefix or alias.replace(' ', '_').lower()
        self.alias = alias
        self.repository = repository
        self.cache_prefix = cache_prefix
        self.logger_params = logger_params
        self.cache_service = CacheService(
            alias=alias, prefix=prefix, logger_params=logger_params
        )

    async def list_all(
        self,
        page_filter: Annotated[FilterPage, Query()] = None,
        user_request: str | None = None,
        trainer_id: str | None = None,
    ):
        try:
            filter_page = FilterPage.build(page_filter, trainer_id=trainer_id)
            return await self.repository.list_all(page_filter=filter_page)
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='list_all',
                user_request=user_request,
                raise_exception=False,
            )
            return exception_pagination(page_filter)
        finally:
            log_service_success(
                self.logger_params,
                operation='list_all',
                message='List all successfully',
                user_request=user_request,
            )

    async def find_one(
        self,
        param: str,
        user_request: str | None = None,
    ):
        try:
            if is_valid_uuid(param):
                result = await self.repository.find_by(id=param)
            else:
                result = await self.repository.find_by(name=param)

            if result is None:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail=f'{self.alias} not found',
                )
            return result
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='find_one',
                user_request=user_request,
                raise_exception=True,
            )
        finally:
            log_service_success(
                self.logger_params,
                operation='find_one',
                message=f'Find one {self.alias} successfully',
                user_request=user_request,
            )

    async def find_by(self, **kwargs):
        user_request = kwargs.get('user_request', None)
        try:
            result = await self.repository.find_by(**kwargs)
            if result is None:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail=f'{self.alias} not found',
                )
            return result
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='find_by',
                user_request=user_request,
            )
        finally:
            log_service_success(
                self.logger_params,
                operation='find_by',
                message=f'Find by {self.alias} successfully',
                user_request=user_request,
            )

    async def update(
        self,
        param: str,
        update_schema: UpdateSchemaT,
        user_request: str | None = None,
    ) -> ModelT:
        try:
            entity = await self.find_one(param, user_request)
            if entity is None:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail=f'{self.alias} not found',
                )
            update_data = update_schema.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if isinstance(entity, dict):
                    entity[key] = value
                else:
                    setattr(entity, key, value)
            return await self.repository.update(entity)
        except Exception as exception:
            handle_service_exception(
                exception,
                logger=self.logger_params.logger,
                service=self.logger_params.service,
                operation='update',
                user_request=user_request,
                raise_exception=True,
            )
        finally:
            log_service_success(
                self.logger_params,
                operation='update',
                message=f'Update {self.alias} successfully',
                user_request=user_request,
            )
