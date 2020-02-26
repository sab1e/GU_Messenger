"""Серверная часть приложения"""

import socket
import argparse
import json
import sys
from common.settings import ACTION, ACCOUNT_NAME, RESPONSE, \
    MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import recv_message, send_message


def handler_client_message(message):
    """Функция обрабатывает корректность сообщения клиента и
    возвращает ответ"""
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
            raise ValueError

    except ValueError:
        print('Номер порта должен находиться в диапозоне от 1024 до 65535')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = recv_message(client)
            print(message_from_client)

            response = handler_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print(f'Сообщение от пользователя некорректно')
            client.close()


if __name__ == '__main__':
    main()
