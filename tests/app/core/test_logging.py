import logging

from app.core.logging import ErrorHighlightFormatter, configure_logging


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


class TestConfigureLogging:
    @staticmethod
    def test_configure_logging_sets_app_logger_propagation():
        """Should disable propagation for app logger"""
        if hasattr(configure_logging, '_configured'):
            delattr(configure_logging, '_configured')

        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        configure_logging()

        app_logger = logging.getLogger('app')
        assert app_logger.propagate is False

    @staticmethod
    def test_configure_logging_idempotent():
        """Should not reconfigure when called multiple times"""
        if hasattr(configure_logging, '_configured'):
            delattr(configure_logging, '_configured')

        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        configure_logging()
        first_handlers_count = len(logging.getLogger('app').handlers)

        configure_logging()
        second_handlers_count = len(logging.getLogger('app').handlers)

        assert first_handlers_count == second_handlers_count

    @staticmethod
    def test_configure_logging_clears_existing_handlers():
        """Should clear existing root logger handlers before configuration"""
        if hasattr(configure_logging, '_configured'):
            delattr(configure_logging, '_configured')

        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        existing_handler = logging.StreamHandler()
        root_logger.addHandler(existing_handler)

        assert len(root_logger.handlers) > 0

        configure_logging()

        assert existing_handler not in root_logger.handlers
