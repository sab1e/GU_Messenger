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
    DEFAULT_PORT, RESPONSE_200, RESPONSE_400, DESTINATION, EXIT
from common.utils import recv_message, send_message
from decos import log

SERVER_LOGGER = logging.getLogger('server')


@log
def create_listen_socket(address, port):
    """Создаем сокет"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((address, port))
    sock.listen(MAX_CONNECTIONS)
    sock.settimeout(0.5)
    return sock


@log
def args_handler():
    """Обработка параметров коммандной строки"""
    parser = argparse.ArgumentParser(description='messenger server app')
    parser.add_argument('-p', dest='port', type=int, default=DEFAULT_PORT,
                        nargs='?', help='Номер порта для соединения')
    parser.add_argument('-a', dest='ip', default='',
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
def client_msg_handler(message, messages_lst, client, clients, names):
    """Функция обрабатывает корректность сообщения клиента и,
     в случае необходимости возвращает ответ"""
    SERVER_LOGGER.debug(f'Обработка сообщения от клиента: {message}')
    # Если сообщение о присутствии, принимаем и отвечаем
    if ACTION in message and message[ACTION] == PRESENCE and \
            TIME in message and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже существует.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # Если это сообщение, то добавляем его в очередь:
    # {'action': 'message', 'from': 'test1', 'to': 'test2', 'time': 1584264912.1911829, 'msg_text': 'fsdfdg'}
    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_lst.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT \
            and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    # Иначе - Bad Request
    else:
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректен.'
        send_message(client, response)
        return


@log
def process_msg(msg, names, listen_socks):
    """Функция отправки сообщения определенному клиенту.
    Принимает словарь - сообщение, список зарегистрированных пользователей,
    слушащие сокеты."""
    if msg[DESTINATION] in names and names[msg[DESTINATION]] in listen_socks:
        send_message(names[msg[DESTINATION]], msg)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю '
                           f'{msg[DESTINATION]} от пользователя '
                           f'{msg[SENDER]}.')
    elif msg[DESTINATION] in names and \
            names[msg[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'Пользователь {msg[DESTINATION]} не зарегистрирован на сервере. '
            f'Отправка сообщения невозможна.'
        )


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
    print('Сервер запущен')

    clients = []
    messages = []
    names = dict()

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
            for client_with_msg in recv_msg_lst:
                try:
                    client_msg_handler(recv_message(client_with_msg),
                                       messages, client_with_msg,
                                       clients, names)
                except Exception:
                    SERVER_LOGGER.error(
                        f'Клиент '
                        f'{client_with_msg.getpeername()} '
                        f'отключился от сервера')
                    clients.remove(client_with_msg)

        for msg in messages:
            try:
                process_msg(msg, names, send_msg_lst)
            except Exception:
                SERVER_LOGGER.info(f'Связь с клинтом {msg[DESTINATION]} '
                                   f'прервана')
                clients.remove(names[msg[DESTINATION]])
                del names[msg[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main()
