"""Серверная часть приложения"""

import socket
import argparse
import json
import sys
import logging
import log.server_log_config
from common.settings import ACTION, ACCOUNT_NAME, RESPONSE, \
    MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import recv_message, send_message
from decos import log


SERVER_LOGGER = logging.getLogger('app.server')


@log
def handler_client_message(message):
    """Функция обрабатывает корректность сообщения клиента и
    возвращает ответ"""
    SERVER_LOGGER.debug(f'Обработка сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request',
    }


def main():
    """Запуск приложения"""
    try:
        parser = argparse.ArgumentParser(description='messenger server app')
        parser.add_argument('-p', dest='port', type=int, default=DEFAULT_PORT,
                            help='Номер порта для соединения')
        parser.add_argument('-a', dest='ip', type=str, default='',
                            help='Адрес для соединения')
        args = parser.parse_args()
        listen_port = args.port
        listen_address = args.ip
        if listen_port < 1024 or listen_port > 65535:
            SERVER_LOGGER.critical(f'Попытка запуска с неподходящим номером '
                                   f'порта: {listen_port}')
            raise ValueError

    except ValueError:
        print('Номер порта должен находиться в диапозоне от 1024 до 65535')
        sys.exit(1)

    SERVER_LOGGER.info(f'Запущен сервер с портом для подключений: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}. '
                       f'Если адрес не указан, соединения будут приниматься '
                       f'с любых адресов')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        SERVER_LOGGER.info(f'Установлено соединение с адресом: {client_address}')
        try:
            message_from_client = recv_message(client)
            SERVER_LOGGER.debug(f'Получено сообщение: {message_from_client}')
            print(message_from_client)

            response = handler_client_message(message_from_client)
            send_message(client, response)
            SERVER_LOGGER.info(f'Отправлено сообщение клиенту: {response}')
            SERVER_LOGGER.debug(f'Соединение с клиентом {client_address} закрыто')
            client.close()
        except (ValueError, json.JSONDecodeError):
            SERVER_LOGGER.error(f'Неудалось декодировать JSON сообщение '
                                f'от клиента {client_address}. '
                                f'Cоединение закрыто.')
            client.close()


if __name__ == '__main__':
    main()
