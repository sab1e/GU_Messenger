"""Декораторы"""

import sys
import logging
import traceback
import inspect
import log.client_log_config
import log.server_log_config


if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('app.client')
else:
    LOGGER = logging.getLogger('app.server')


def log(func_for_log):
    """Декоратор"""
    def log_create(*args, **kwargs):
        """Обертка"""
        res = func_for_log(*args, **kwargs)
        LOGGER.debug(f'Вызвана функция {func_for_log.__name__} с параматреми '
                     f'{args}, {kwargs}. Вызов из модуля '
                     f'{func_for_log.__module__}. Вызов из функции '
                     f'{traceback.format_stack()[0].strip().split()[-1]}. '
                     f'Вызов из функции {inspect.stack()[1][3]}')
        return res
    return log_create
