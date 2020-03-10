"""Утилиты"""

import json
import sys
from common.settings import MAX_PACKAGE_LENGTH, ENCODING
from decos import log
sys.path.append('../')


@log
def recv_message(client):
    """Функция приема и декодирования сообщения"""
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


@log
def send_message(sock, message):
    """Функция кодирования и отправки сообщения"""
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    sock.send(encoded_message)
