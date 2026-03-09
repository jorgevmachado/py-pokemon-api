import logging
import logging.config
import os
import sys

DEFAULT_LOG_LEVEL = 'INFO'


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
