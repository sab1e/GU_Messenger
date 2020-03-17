"""Настройки журналирования клиентской части приложения"""

import sys
import os
import logging
from common.settings import LOGGING_LEVEL

sys.path.append('../')

CLIENT_FORMATTER = logging.Formatter(
    "%(asctime)s %(levelname)s %(module)s %(message)s")

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

FILE_HANDLER = logging.FileHandler(PATH, encoding='utf-8')
FILE_HANDLER.setFormatter(CLIENT_FORMATTER)

LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('critical - тестовый запуск')
    LOGGER.error('error - тестовый запуск')
    LOGGER.warning('warning - тестовый запуск')
    LOGGER.info('info - тестовый запуск')
    LOGGER.debug('debug - тестовый запуск')
