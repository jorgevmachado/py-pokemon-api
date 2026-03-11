import logging
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from app.core.logging import (
    ErrorHighlightFormatter,
    configure_logging,
    log_service_exception,
    log_service_success,
)


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
    def test_log_service_exception_with_http_exception():
        """Should log exception payload with mapped HTTP status"""
        logger = MagicMock()

        log_service_exception(
            logger=logger,
            service='auth',
            operation='authenticate',
            status_code=HTTPStatus.BAD_REQUEST,
            error_message='Bad request',
        )

        logger.exception.assert_called_once()
        (message,) = logger.exception.call_args.args
        payload = logger.exception.call_args.kwargs['extra']

        assert message == 'auth.authenticate'
        assert payload['status_code'] == HTTPStatus.BAD_REQUEST
        assert payload['error_message'] == 'Bad request'

    @staticmethod
    def test_log_service_success_with_defaults():
        """Should log success with default message and status code"""
        logger = MagicMock()

        log_service_success(
            logger=logger,
            service='auth',
            operation='authenticate',
        )

        logger.info.assert_called_once()
        (message,) = logger.info.call_args.args
        payload = logger.info.call_args.kwargs['extra']

        assert message == 'auth.authenticate'
        assert payload['status_code'] == HTTPStatus.OK
        assert payload['message'] == 'Success'

    @staticmethod
    def test_log_service_success_with_custom_payload():
        """Should merge custom payload fields into success log"""
        logger = MagicMock()

        log_service_success(
            logger=logger,
            service='auth',
            operation='authenticate',
            status_code=HTTPStatus.CREATED,
            extra={
                'trainer_id': 'trainer-1',
                'message': 'User authenticated',
            },
        )

        logger.info.assert_called_once()
        payload = logger.info.call_args.kwargs['extra']

        assert payload['status_code'] == HTTPStatus.CREATED
        assert payload['message'] == 'User authenticated'
        assert payload['trainer_id'] == 'trainer-1'


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

        with patch('app.core.logging.logging.config.dictConfig') as mock_dict_config:
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

        with patch('app.core.logging.logging.config.dictConfig', side_effect=fake_dict_config):
            configure_logging()

        assert handlers_cleared_before_dict_config['value'] is True
