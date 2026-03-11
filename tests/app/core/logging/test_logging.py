import logging
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from app.core.logging import (
    ErrorHighlightFormatter,
    LoggingParams,
    configure_logging,
    log_service_exception,
    log_service_success,
)
from app.core.logging.logging import build_logger_params


@pytest.fixture(autouse=True)
def reset_logging_configuration_state():
    """Reset shared logging state between tests to avoid cross-test side effects"""
    if hasattr(configure_logging, '_configured'):
        delattr(configure_logging, '_configured')

    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    yield

    if hasattr(configure_logging, '_configured'):
        delattr(configure_logging, '_configured')

    root_logger.handlers.clear()


class TestErrorHighlightFormatter:
    @staticmethod
    def test_format_adds_color_only_to_error_levelname():
        """Should wrap only ERROR levelname with ANSI color codes"""
        formatter = ErrorHighlightFormatter('%(levelname)s %(name)s %(message)s')
        record = logging.LogRecord(
            name='app.test',
            level=logging.ERROR,
            pathname=__file__,
            lineno=10,
            msg='Failure',
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        assert formatted.startswith(f'{formatter.ERROR_STYLE}ERROR{formatter.RESET_STYLE} ')
        assert 'Failure' in formatted
        assert formatted.count(formatter.ERROR_STYLE) == 1
        assert formatted.count(formatter.RESET_STYLE) == 1

    @staticmethod
    def test_format_keeps_info_levelname_plain():
        """Should keep INFO levelname without ANSI codes"""
        formatter = ErrorHighlightFormatter('%(levelname)s %(name)s %(message)s')
        record = logging.LogRecord(
            name='app.test',
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg='All good',
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        assert formatted.startswith('INFO ')
        assert '\x1b[' not in formatted


class TestServiceLogging:
    @staticmethod
    def test_log_service_exception_with_keyword_args():
        """Should log exception payload when called with keyword arguments"""
        logger = MagicMock()

        log_service_exception(
            logger=logger,
            service='auth',
            operation='authenticate',
            status_code=HTTPStatus.BAD_REQUEST,
            message='Bad request',
        )

        logger.exception.assert_called_once()
        (log_message,) = logger.exception.call_args.args
        payload = logger.exception.call_args.kwargs['extra']

        assert log_message == 'auth.authenticate'
        assert payload['status_code'] == HTTPStatus.BAD_REQUEST
        assert payload['detail'] == 'Bad request'

    @staticmethod
    def test_log_service_exception_with_logging_params():
        """Should log exception payload when called with LoggingParams"""

        logger = MagicMock()
        params = LoggingParams(
            logger=logger,
            service='auth',
            operation='authenticate',
            status_code=HTTPStatus.UNAUTHORIZED,
            message='Unauthorized',
        )

        log_service_exception(params)

        logger.exception.assert_called_once()
        (log_message,) = logger.exception.call_args.args
        payload = logger.exception.call_args.kwargs['extra']

        assert log_message == 'auth.authenticate'
        assert payload['status_code'] == HTTPStatus.UNAUTHORIZED
        assert payload['detail'] == 'Unauthorized'

    @staticmethod
    def test_log_service_exception_defaults_to_internal_server_error():
        """Should default to INTERNAL_SERVER_ERROR when no status_code is provided"""
        logger = MagicMock()

        log_service_exception(
            logger=logger,
            service='auth',
            operation='authenticate',
        )

        logger.exception.assert_called_once()
        payload = logger.exception.call_args.kwargs['extra']

        assert payload['status_code'] == HTTPStatus.INTERNAL_SERVER_ERROR

    @staticmethod
    def test_log_service_success_with_keyword_args():
        """Should log success when called with keyword arguments"""
        logger = MagicMock()

        log_service_success(
            logger=logger,
            service='auth',
            operation='authenticate',
        )

        logger.info.assert_called_once()
        (log_message,) = logger.info.call_args.args
        payload = logger.info.call_args.kwargs['extra']

        assert log_message == 'auth.authenticate'
        assert payload['status_code'] == HTTPStatus.OK

    @staticmethod
    def test_log_service_success_with_logging_params():
        """Should log success when called with LoggingParams"""

        logger = MagicMock()
        params = LoggingParams(
            logger=logger,
            service='auth',
            operation='',
        )

        log_service_success(
            params,
            operation='authenticate',
            message='User authenticated',
        )

        logger.info.assert_called_once()
        (log_message,) = logger.info.call_args.args
        payload = logger.info.call_args.kwargs['extra']

        assert log_message == 'auth.authenticate'
        assert payload['detail'] == 'User authenticated'
        assert payload['status_code'] == HTTPStatus.OK

    @staticmethod
    def test_log_service_success_with_custom_status_code():
        """Should use provided status code in success log"""
        logger = MagicMock()

        log_service_success(
            logger=logger,
            service='auth',
            operation='authenticate',
            status_code=HTTPStatus.CREATED,
            message='Resource created',
        )

        logger.info.assert_called_once()
        payload = logger.info.call_args.kwargs['extra']

        assert payload['status_code'] == HTTPStatus.CREATED
        assert payload['detail'] == 'Resource created'


class TestBuildLoggerParams:
    @staticmethod
    def test_raises_when_logger_is_none():
        """Should raise TypeError when no logger is provided"""

        with pytest.raises(TypeError, match='logger is required'):
            build_logger_params(
                service='auth',
                operation='authenticate',
            )

    @staticmethod
    def test_raises_when_logger_has_no_info_method():
        """Should raise TypeError when logger does not implement info()"""

        class InvalidLogger:
            def exception(self) -> None:
                pass

        with pytest.raises(TypeError, match='logger is required'):
            build_logger_params(
                logger=InvalidLogger(),
                service='auth',
                operation='authenticate',
            )

    @staticmethod
    def test_raises_when_service_is_missing():
        """Should raise TypeError when service is not provided"""

        with pytest.raises(TypeError, match='service is required'):
            build_logger_params(
                logger=MagicMock(),
                operation='authenticate',
            )

    @staticmethod
    def test_raises_when_operation_is_missing():
        """Should raise TypeError when operation is not provided"""

        with pytest.raises(TypeError, match='operation is required'):
            build_logger_params(
                logger=MagicMock(),
                service='auth',
            )

    @staticmethod
    def test_accepts_mapping_as_logging_params():
        """Should resolve base fields from a plain Mapping"""

        logger = MagicMock()
        params = build_logger_params({
            'logger': logger,
            'service': 'auth',
            'operation': 'authenticate',
        })

        assert params.service == 'auth'
        assert params.operation == 'authenticate'
        assert params.logger is logger

    @staticmethod
    def test_overrides_mapping_fields_with_keyword_args():
        """Should allow keyword args to override fields from a Mapping"""

        logger = MagicMock()
        params = build_logger_params(
            {
                'logger': logger,
                'service': 'auth',
                'operation': 'old_operation',
            },
            operation='new_operation',
        )

        assert params.operation == 'new_operation'


class TestConfigureLogging:
    @staticmethod
    def test_configure_logging_sets_app_logger_propagation():
        """Should disable propagation for app logger"""
        configure_logging()

        app_logger = logging.getLogger('app')
        assert app_logger.propagate is False

    @staticmethod
    def test_configure_logging_idempotent():
        """Should not reconfigure when called multiple times"""
        configure_logging()
        first_handlers_count = len(logging.getLogger('app').handlers)

        configure_logging()
        second_handlers_count = len(logging.getLogger('app').handlers)

        assert first_handlers_count == second_handlers_count

    @staticmethod
    def test_configure_logging_returns_early_when_already_configured():
        """Should return early when logger has already been configured"""
        setattr(configure_logging, '_configured', True)

        with patch('logging.config.dictConfig') as mock_dict_config:
            configure_logging()

        mock_dict_config.assert_not_called()

    @staticmethod
    def test_configure_logging_clears_existing_handlers():
        """Should clear existing root logger handlers before configuration"""
        root_logger = logging.getLogger()
        existing_handler = logging.StreamHandler()
        root_logger.addHandler(existing_handler)

        handlers_cleared_before_dict_config = {'value': False}

        def fake_dict_config(_: dict) -> None:
            handlers_cleared_before_dict_config['value'] = len(root_logger.handlers) == 0

        with patch('logging.config.dictConfig', side_effect=fake_dict_config):
            configure_logging()

        assert handlers_cleared_before_dict_config['value'] is True
