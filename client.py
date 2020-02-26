"""Клиентская часть приложения"""

import sys
import json
import socket
import time
import argparse
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME,\
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import recv_message, send_message


def create_presense(account_name='Guest'):
    """Функция генерирует сервисное сообщение о присутствии клиента"""
    presence_msg = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }

    return presence_msg


def handler_server_ans(message):
    """Функция обрабатывает ответ от сервера"""
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    raise ValueError


def main():
    """Запуск приложения"""
    try:
        parser = argparse.ArgumentParser(description='messanger client app')
        parser.add_argument('ip', nargs='?', type=str,
                            default=DEFAULT_IP_ADDRESS,
                            help='Адрес сервера для соединения')
        parser.add_argument('port', nargs='?', type=int, default=DEFAULT_PORT,
                            help='Порт сервера для соединения')

        args = parser.parse_args()
        server_address = args.ip
        server_port = args.port

        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except ValueError:
        print('Номер порта должен находиться в диапозоне от 1024 до 65535')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = create_presense()
    send_message(transport, message_to_server)
    try:
        answer = handler_server_ans(recv_message(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
