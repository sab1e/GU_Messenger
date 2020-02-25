"""Утилиты"""

import json
from common.settings import MAX_PACKAGE_LENGTH, ENCODING


def recv_message(client):
    """
    Утилита приема и декодирования сообщения
    :param client:
    :return:
    """

    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock, message):
    """
    Утилита кодирования и отправки сообщения
    :param sock:
    :param message:
    :return:
    """
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    sock.send(encoded_message)
