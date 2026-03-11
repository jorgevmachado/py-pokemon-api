import logging
import logging.config
import os
import sys
from http import HTTPStatus
from typing import Any

import httpx
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

DEFAULT_LOG_LEVEL = 'INFO'
STATUS_MESSAGE_MAP: dict[HTTPStatus, str] = {
    HTTPStatus.INTERNAL_SERVER_ERROR: 'Internal server error',
    HTTPStatus.SERVICE_UNAVAILABLE: 'Failed to execute external request',
}


class ErrorHighlightFormatter(logging.Formatter):
    ERROR_STYLE = '\x1b[41;97m'
    RESET_STYLE = '\x1b[0m'

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname

        if record.levelno == logging.ERROR:
            record.levelname = f'{self.ERROR_STYLE}{original_levelname}{self.RESET_STYLE}'

        try:
            return super().format(record)
        finally:
            record.levelname = original_levelname


def _resolve_status_code(exception: Exception) -> HTTPStatus:
    if isinstance(exception, HTTPException):
        try:
            return HTTPStatus(exception.status_code)
        except ValueError:
            return HTTPStatus.INTERNAL_SERVER_ERROR

    if isinstance(exception, SQLAlchemyError):
        return HTTPStatus.INTERNAL_SERVER_ERROR

    if isinstance(exception, httpx.HTTPError):
        return HTTPStatus.SERVICE_UNAVAILABLE

    return HTTPStatus.INTERNAL_SERVER_ERROR


def _build_error_message(exception: Exception, status_code: HTTPStatus) -> str:
    if isinstance(exception, HTTPException):
        detail = exception.detail
        if isinstance(detail, str) and detail:
            return detail

    return STATUS_MESSAGE_MAP.get(status_code, status_code.phrase)


def log_service_exception(
    exception: Exception,
    *,
    logger: logging.Logger,
    service: str,
    operation: str,
) -> None:
    status_code = _resolve_status_code(exception)
    error_message = _build_error_message(exception, status_code)

    logger.exception(
        f'{service}.{operation}',
        extra={
            'service': service,
            'operation': operation,
            'status_code': status_code,
            'error_message': error_message,
        },
    )


def log_service_success(
    *,
    logger: logging.Logger,
    service: str,
    operation: str,
    status_code: HTTPStatus = HTTPStatus.OK,
    extra: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        'service': service,
        'operation': operation,
        'status_code': status_code,
        'message': 'Success',
    }

    if extra:
        payload.update(extra)

    logger.info(f'{service}.{operation}', extra=payload)


def configure_logging() -> None:
    if getattr(configure_logging, '_configured', False):
        return

    log_level = os.getenv('LOG_LEVEL', DEFAULT_LOG_LEVEL).upper()

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.handlers.clear()

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                '()': ErrorHighlightFormatter,
                'format': '%(levelname)s %(asctime)s:  %(name)s %(message)s ',
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'standard',
            },
        },
        'loggers': {
            'app': {
                'handlers': ['stdout'],
                'level': log_level,
                'propagate': False,
            },
        },
        'root': {
            'handlers': ['stdout'],
            'level': log_level,
        },
    })

    setattr(configure_logging, '_configured', True)
