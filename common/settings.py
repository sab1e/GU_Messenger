"""Настройки по умолчанию"""

import logging

# Порт по умолчанию
DEFAULT_PORT = 7777
# IP адрес для подключения по умолчанию
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключения клиента
MAX_CONNECTIONS = 5
# Максимальная длина сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'
# Текущий уровень логирования
LOGGING_LEVEL = logging.DEBUG

# Потокол JIM. Основные ключи
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'msg_text'
EXIT = 'exit'

# Словари с ответами
# 200
RESPONSE_200 = {RESPONSE: 200}
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}

