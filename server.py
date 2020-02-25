"""Серверная часть приложения"""

import socket
import argparse
import json
from common.settings import ACTION, ACCOUNT_NAME, RESPONSE, \
    MAX_PACKAGE_LENGTH, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import recv_message, send_message


def handler_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request',
    }


def main():
    parser = argparse.ArgumentParser(description='messenger server app')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                        help='Input port for connection', choices=)
    args = parser.parse_args()
    listen_port = int(args.port)



if __name__ == '__main__':
    main()
