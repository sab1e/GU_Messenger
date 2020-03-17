"""Клиентская часть приложения"""

import sys
import json
import time
import argparse
import logging
import threading
from socket import socket, AF_INET, SOCK_STREAM
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, SENDER, \
    MESSAGE_TEXT, DESTINATION, EXIT
from common.utils import recv_message, send_message
from log import client_log_config
from decos import log
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError

CLIENT_LOGGER = logging.getLogger('client')


@log
def create_exit_msg(account_name):
    """Функция создания словаря с сообщением о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def msg_from_server(sock, my_username):
    """Функция обрабатывает сообщения других пользователей,
    полученных с сервера
    """
    while True:
        try:
            msg = recv_message(sock)
            if ACTION in msg and msg[ACTION] == MESSAGE and SENDER in msg and \
                    DESTINATION in msg and MESSAGE_TEXT in msg and \
                    msg[DESTINATION] == my_username:
                print(f'Получено сообщение от пользователя {msg[SENDER]}: \n'
                      f'{msg[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                                   f'{msg[SENDER]}: \n {msg[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(
                    f'Получено некорректное сообщение с сервера: '
                    f'{msg}')
        except IncorrectDataRecivedError:
            CLIENT_LOGGER.error(
                f'Не удалось декодировать полученное сообщение')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Соединение с сервером потеряно')
            break


@log
def create_msg(sock, account_name='Guest'):
    """Функция запрашивает получателя и текст сообщения и отправляет
    полученые данные на сервер
    """
    to_user = input('Введите получателя: ')
    msg = input('Введите сообщение для отправки: ')

    msg_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: msg,
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {msg_dict}')
    try:
        send_message(sock, msg_dict)
        CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@log
def user_input_handler(sock, username):
    """Функция запрашивает и обрабатывает команды пользователя и
    отправляет сообщения"""
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_msg(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_msg(username))
            print('Завершение соединения.')
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print('Неизвестная команда, попробуйте еще раз. '
                  'help - вывод списка команд.')


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
def print_help():
    """Функция выводит справку поддерживаемых команд"""
    print('Поддерживаемые команды: ')
    print('message - отправить сообщение')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@log
def server_ans_handler(msg):
    """Функция обрабатывает ответ от сервера"""
    CLIENT_LOGGER.debug(f'Обработка сообщения от сервера: {msg}')
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            return '200: OK'
        elif msg[RESPONSE] == 400:
            raise ServerError(f'400: {msg[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def args_handler():
    """Обработка параметров коммандной строки"""
    parser = argparse.ArgumentParser(description='messanger client app')
    parser.add_argument('addr', nargs='?', default=DEFAULT_IP_ADDRESS,
                        help='Адрес сервера для соединения')
    parser.add_argument('port', nargs='?', type=int, default=DEFAULT_PORT,
                        help='Порт сервера для соединения')
    parser.add_argument('-n', '--name', default=None, nargs='?',
                        help='Имя клиента')

    args = parser.parse_args()
    server_address = args.addr
    server_port = args.port
    client_name = args.name

    if not 1023 < server_port < 65535:
        CLIENT_LOGGER.critical(f'Попытка запуска с неподходящим номером '
                               f'порта: {server_port}. Номер порта должен '
                               f'находиться в диапозоне от 1024 до 65535')
        sys.exit(1)

    return server_address, server_port, client_name


def main():
    """Запуск приложения"""
    server_address, server_port, client_name = args_handler()

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    CLIENT_LOGGER.info(f'Клиент запущен с параметрами: '
                       f'IP сервера: {server_address}, '
                       f'порт  сервера: {server_port}, '
                       f'имя пользователя {client_name}')

    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presense(client_name))
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
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу '
            f'{server_address}:{server_port}. Сервер отверг '
            f'запрос на подключение')
        sys.exit(1)
    else:
        receiver = threading.Thread(target=msg_from_server,
                                    args=(transport, client_name))
        receiver.deamon = True
        receiver.start()

        user_interface = threading.Thread(target=user_input_handler,
                                          args=(transport, client_name))
        user_interface.deamon = True
        user_interface.start()
        CLIENT_LOGGER.info(f'Запущены потоки приема/отправки сообщений')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
