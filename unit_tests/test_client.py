"""Unit-тесты клиентской чати приоложения"""

import unittest
from client import create_presense, handler_server_ans
from common.settings import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR


class TestClass(unittest.TestCase):
    """Класс с тестами"""
    def test_presense(self):
        """Тест генерации корректного сервисного сообщения от клиента"""
        test = create_presense()
        test[TIME] = 1

        self.assertEqual(test,
                         {ACTION: PRESENCE, TIME: 1,
                          USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_server_ans(self):
        """Тест корректной обрабоки ответа 200 от сервера"""
        test = handler_server_ans({RESPONSE: 200})
        self.assertEqual(test, '200: OK')

    def test_400_server_ans(self):
        """Тест корректной обрабоки ответа 400 от сервера"""
        test = handler_server_ans({RESPONSE: 400, ERROR: 'Bad Request'})
        self.assertEqual(test, '400: Bad Request')

    def test_no_server_ans(self):
        """Тест исключения при отсутствии поля RESPONSE"""
        self.assertRaises(
            ValueError, handler_server_ans, {
                ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
