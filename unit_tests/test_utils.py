"""Unit-тесты общих функций для серверной и клиентской частей"""
import unittest
import json
from common.utils import recv_message, send_message
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    ENCODING, RESPONSE, ERROR


class TestSocket:
    """
    Тестовый класс имитирующий сокет,
    при создании принимает тестовый словарь
    """

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.enc_msg = None
        self.recv_msg = None

    def send(self, msg_to_send):
        """
        Тестовый метод отправки, корректно кодирует и
        сохраняет тестовый словарь, так же сохраняет значение,
        отправленное тестируемой функцией
        """
        json_msg = json.dumps(self.test_dict)
        self.enc_msg = json_msg.encode(ENCODING)
        self.recv_msg = msg_to_send

    def recv(self, max_len):
        """Метод возвращает закодированный словарь"""
        json_test_msg = json.dumps(self.test_dict)
        return json_test_msg.encode(ENCODING)


class TestClass(unittest.TestCase):
    """Класс с тестами"""
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 1,
        USER: {
            ACCOUNT_NAME: 'Guest',
        },
    }

    test_dict_recv_ok = {
        RESPONSE: 200,
    }

    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: 'Bad Request',
    }

    def test_recv_message(self):
        """Тест функции приема сообщений"""
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        self.assertEqual(recv_message(test_sock_ok), self.test_dict_recv_ok)
        self.assertEqual(recv_message(test_sock_err), self.test_dict_recv_err)

    def test_recv_raise(self):
        """Тест исключения если в сообщении не словарь"""
        test_sock = TestSocket(1111)
        self.assertRaises(ValueError, recv_message, test_sock)

    def test_send_message(self):
        """Тест функции отправки сообщения"""
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.enc_msg, test_socket.recv_msg)


if __name__ == '__main__':
    unittest.main()
