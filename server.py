"""Серверная часть приложения"""

import socket
import argparse
import sys
import logging
import time
import select
from socket import socket, AF_INET, SOCK_STREAM
import log.server_log_config
from common.settings import ACTION, ACCOUNT_NAME, SENDER, RESPONSE, \
    MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, MESSAGE, MESSAGE_TEXT, \
    DEFAULT_PORT
from common.utils import recv_message, send_message
from decos import log

SERVER_LOGGER = logging.getLogger('app.server')


@log
def create_listen_socket(address, port):
    """Создаем сокет"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((address, port))
    sock.listen(MAX_CONNECTIONS)
    sock.settimeout(0.2)
    return sock


@log
def args_handler():
    """Обработка параметров коммандной строки"""
    parser = argparse.ArgumentParser(description='messenger server app')
    parser.add_argument('-p', dest='port', type=int, default=DEFAULT_PORT,
                        nargs='?', help='Номер порта для соединения')
    parser.add_argument('-a', dest='ip', type=str, default='',
                        nargs='?', help='Адрес для соединения')
    args = parser.parse_args()
    listen_address = args.ip
    listen_port = args.port

    if not 1023 < listen_port < 65535:
        SERVER_LOGGER.critical(f'Попытка запуска с неподходящим номером '
                               f'порта: {listen_port}. Номер порта должен '
                               f'находиться в диапозоне от 1024 до 65535')
        sys.exit(1)

    return listen_address, listen_port


@log
def client_message_handler(message, messages_lst, client):
    """Функция обрабатывает корректность сообщения клиента и
    возвращает ответ"""
    SERVER_LOGGER.debug(f'Обработка сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_lst.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request',
        })
        return


def main():
    """Основной цикл обработки запросов клиента"""
    listen_address, listen_port = args_handler()
    transport = create_listen_socket(listen_address, listen_port)

    SERVER_LOGGER.info(f'Запущен сервер с портом для подключений: '
                       f'{listen_port}, '
                       f'адрес с которого принимаются подключения: '
                       f'{listen_address}. '
                       f'Если адрес не указан, соединения будут приниматься '
                       f'с любых адресов')

    clients = []
    messages = []

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соединение с адресом: '
                               f'{client_address}')
            clients.append(client)

        recv_msg_lst = []
        send_msg_lst = []
        err_lst = []

        try:
            if clients:
                recv_msg_lst, send_msg_lst, err_lst = select.select(clients,
                                                                    clients,
                                                                    [], 0)
        except OSError:
            pass

        if recv_msg_lst:
            for client_with_messsage in recv_msg_lst:
                try:
                    client_message_handler(recv_message(client_with_messsage),
                                           messages, client_with_messsage)
                except BaseException:
                    SERVER_LOGGER.error(
                        f'Клиент '
                        f'{client_with_messsage.getpeername()} '
                        f'отключился от сервера')

        if messages and send_msg_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1],
            }
            del messages[0]
            for waiting_client in send_msg_lst:
                try:
                    send_message(waiting_client, message)
                except BaseException:
                    SERVER_LOGGER.error(f'Клиент {waiting_client.getpeername} '
                                        f'отключился от сервера')
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
