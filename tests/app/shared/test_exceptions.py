from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.shared.exceptions import (
    AppHTTPException,
    UnauthorizedException,
    handle_service_exception,
    log_service_exception,
)


class TestUnauthorizedException:
    @staticmethod
    def test_unauthorized_exception_default_message():
        """Should set unauthorized status code and default message"""
        exception = UnauthorizedException()

        assert exception.status_code == HTTPStatus.UNAUTHORIZED
        assert exception.detail == 'Incorrect email or password'


class TestLogServiceException:
    @staticmethod
    def test_log_service_exception_with_http_exception():
        """Should log exception without raising it"""
        logger = MagicMock()
        error = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Bad request')

        log_service_exception(
            error,
            logger=logger,
            service='test',
            operation='test_op',
        )

        logger.exception.assert_called_once()
        (message,) = logger.exception.call_args.args
        assert message == 'test.test_op'

    @staticmethod
    def test_log_service_exception_with_sqlalchemy_error():
        """Should log SQLAlchemy error without raising it"""
        logger = MagicMock()
        error = SQLAlchemyError('boom')

        log_service_exception(
            error,
            logger=logger,
            service='test',
            operation='test_op',
        )

        logger.exception.assert_called_once()

    @staticmethod
    def test_log_service_exception_with_invalid_http_status():
        """Should fallback to internal server error when HTTPException status is invalid"""
        logger = MagicMock()
        error = HTTPException(status_code=999, detail='Invalid')

        log_service_exception(
            error,
            logger=logger,
            service='test',
            operation='test_op',
        )

        logger.exception.assert_called_once()
        (message,) = logger.exception.call_args.args
        result_status_code = logger.exception.call_args.kwargs['extra']['status_code']
        result_error_message = logger.exception.call_args.kwargs['extra']['error_message']

        assert message == 'test.test_op'
        assert result_status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert result_error_message == 'Invalid'


class TestHandleServiceException:
    @staticmethod
    def test_handle_service_exception_with_http_exception():
        """Should preserve status code and detail from HTTPException"""
        logger = MagicMock()
        error = HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Bad request')

        with pytest.raises(AppHTTPException) as exc_info:
            handle_service_exception(
                error,
                logger=logger,
                service='auth',
                operation='authenticate',
            )

        assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
        assert exc_info.value.detail == 'Bad request'
        logger.exception.assert_called_once()
        result_status_code = logger.exception.call_args.kwargs['extra']['status_code']
        (message,) = logger.exception.call_args.args
        assert message == 'auth.authenticate'
        assert result_status_code == HTTPStatus.BAD_REQUEST

    @staticmethod
    def test_handle_service_exception_with_invalid_http_status():
        """Should fallback to internal server error when HTTPException status is invalid"""
        logger = MagicMock()
        error = HTTPException(status_code=999, detail='Invalid')

        with pytest.raises(AppHTTPException) as exc_info:
            handle_service_exception(
                error,
                logger=logger,
                service='auth',
                operation='authenticate',
            )

        result_status_code = logger.exception.call_args.kwargs['extra']['status_code']

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Invalid'
        assert result_status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        logger.exception.assert_called_once()

    @staticmethod
    def test_handle_service_exception_with_sqlalchemy_error():
        """Should return internal server error when SQLAlchemyError occurs"""
        logger = MagicMock()
        error = SQLAlchemyError('boom')

        with pytest.raises(AppHTTPException) as exc_info:
            handle_service_exception(
                error,
                logger=logger,
                service='auth',
                operation='authenticate',
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Internal server error'
        logger.exception.assert_called_once()

    @staticmethod
    def test_handle_service_exception_with_unexpected_error():
        """Should return internal server error when unexpected error occurs"""
        logger = MagicMock()
        error = Exception('boom')

        with pytest.raises(AppHTTPException) as exc_info:
            handle_service_exception(
                error,
                logger=logger,
                service='auth',
                operation='authenticate',
            )

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == 'Internal server error'
        logger.exception.assert_called_once()
