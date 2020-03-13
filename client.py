"""Клиентская часть приложения"""

import sys
import json
import time
import argparse
import logging
from socket import socket, AF_INET, SOCK_STREAM
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, SENDER, \
    MESSAGE_TEXT
from common.utils import recv_message, send_message
from log import client_log_config
from decos import log
from errors import ReqFieldMissingError, ServerError

CLIENT_LOGGER = logging.getLogger('app.client')


@log
def msg_from_server(msg):
    """Функция обрабатывает сообщения других пользователей,
    полученных с сервера
    """
    if ACTION in msg and msg[ACTION] == MESSAGE and SENDER in msg and \
            MESSAGE_TEXT in msg:
        print(f'Получено сообщение от пользователя {msg[SENDER]}: \n'
              f'{msg[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                           f'{msg[SENDER]}: \n {msg[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: '
                            f'{msg}')


@log
def create_msg(sock, account_name='Guest'):
    """Функция запрашивает ввод текста сообщения и возвращает
    словарь сообщения, или завершает работу при вводе команды
    """
    msg = input('Введите сообщени для отправки или \'!!!\' '
                'для завершения работы: ')
    if msg == '!!!':
        sock.close()
        CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
        print(f'Спасибо за использования нашего сервиса!')
        sys.exit(0)
    msg_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: msg,
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {msg_dict}')
    return msg_dict


@log
def create_presense(account_name='Guest'):
    """Функция генерирует сервисное сообщение о присутствии клиента"""

    presence_msg = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }

    CLIENT_LOGGER.debug(f'Сгенерировано сервисное сообщение {PRESENCE} '
                        f'пользователем {account_name} ')

    return presence_msg


@log
def server_ans_handler(msg):
    """Функция обрабатывает ответ от сервера"""
    CLIENT_LOGGER.debug(f'Обработка сообщения от сервера: {msg}')
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            return '200: OK'
        return f'400: {msg[ERROR]}'
    CLIENT_LOGGER.error(f'В сообщении отсутствует обязательное {RESPONSE}')
    raise ReqFieldMissingError(RESPONSE)


@log
def args_handler():
    """Обработка параметров коммандной строки"""
    parser = argparse.ArgumentParser(description='messanger client app')
    parser.add_argument('addr', nargs='?', default=DEFAULT_IP_ADDRESS,
                        help='Адрес сервера для соединения')
    parser.add_argument('port', nargs='?', type=int, default=DEFAULT_PORT,
                        help='Порт сервера для соединения')
    parser.add_argument('-m', '--mode', default='listen', nargs='?',
                        help='Режим работы клиента')

    args = parser.parse_args()
    server_address = args.addr
    server_port = args.port
    client_mode = args.mode

    if not 1023 < server_port < 65535:
        CLIENT_LOGGER.critical(f'Попытка запуска с неподходящим номером '
                               f'порта: {server_port}. Номер порта должен '
                               f'находиться в диапозоне от 1024 до 65535')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f'Указан недопустимый режим работы '
                               f'{client_mode}. Допустимые режимы: '
                               f'listen, send')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    """Запуск приложения"""
    server_address, server_port, client_mode = args_handler()

    CLIENT_LOGGER.info(f'Клиент запущен с параметрами: '
                       f'IP сервера: {server_address}, '
                       f'порт  сервера: {server_port}, '
                       f'режим работы {client_mode}')

    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presense())
        answer = server_ans_handler(recv_message(transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером: '
                           f'{server_address}:{server_port}. '
                           f'Ответ от сервера {answer}')
        print(f'Соединение с сервером установлено.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error(f'Не удалось декодировать полученую JSON строку')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.info(f'При установке соединения сервер вернул ошибку: '
                           f'{error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                            f'{missing_error}')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу '
            f'{server_address}:{server_port}. Сервер отверг '
            f'запрос на подключение')
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - прием сообщений.')
        while True:
            if client_mode == 'send':
                try:
                    send_message(transport, create_msg(transport))
                except (ConnectionResetError,
                        ConnectionError,
                        ConnectionAbortedError):
                    CLIENT_LOGGER.error(
                        f'Соединение с сервером {server_port}:{server_port} '
                        f'было потеряно')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    msg_from_server(recv_message(transport))
                except (ConnectionResetError,
                        ConnectionError,
                        ConnectionAbortedError):
                    CLIENT_LOGGER.error(
                        f'Соединение с сервером {server_address}:{server_port}'
                        f'было потеряно')
                    sys.exit(1)


if __name__ == '__main__':
    main()
