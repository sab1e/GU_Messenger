"""Unit-тесты серверной чати приоложения"""

import unittest
from server import handler_client_message
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR


class TestClass(unittest.TestCase):
    """Класс с тестами"""
    ok_resp = {RESPONSE: 200}
    err_resp = {RESPONSE: 400, ERROR: 'Bad Request'}

    def test_response_200(self):
        """Корректное сообщение"""
        self.assertEqual(handler_client_message(
            {ACTION: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'Guest'}}),
            self.ok_resp)

    def test_no_action(self):
        """Ошибка, если отсутствует поле ACTION"""
        self.assertEqual(handler_client_message(
            {TIME: 1, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_resp)

    def test_wrong_action(self):
        """Ошибка, если значение поля ACTION неизвестно"""
        self.assertEqual(handler_client_message(
            {ACTION: 'test', TIME: 1, USER: {ACCOUNT_NAME: 'Guest'}}),
            self.err_resp)

    def test_no_time(self):
        """Ошибка, если отсутствует поле TIME"""
        self.assertEqual(handler_client_message(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}),
            self.err_resp)

    def test_no_user(self):
        """Ошибка, если отсутствует поле USER"""
        self.assertEqual(handler_client_message(
            {ACTION: PRESENCE, TIME: 1}),
            self.err_resp)

    def test_wrong_user(self):
        """Ошибка, если значение поля USER не Guest"""
        self.assertEqual(handler_client_message(
            {ACTION: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'test'}}),
            self.err_resp)


if __name__ == '__main__':
    unittest.main()
