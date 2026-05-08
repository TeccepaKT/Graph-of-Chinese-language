"""

Запросы к AI через чаты

"""

from typing import Any
from abc import ABC, abstractmethod
from time import sleep
from random import randint


def random_num(a: float, b: float, acc: int = 10000) -> float:
    """ Случайное число в [a, b] """
    return a + (b - a) * randint(0, acc) / acc


class AIChat(ABC):
    """ Взаимодействие с ИИ """
    @abstractmethod
    def get_response(self, *args, **kwargs) -> Any:
        """ Получить ответ на запрос """
        raise NotImplementedError()


class DummyChat(AIChat):
    """ Чат-заглушка для safety mode и тестирования
        Не использует логгер """
    def get_response(self, text: str) -> str:
        sleep(2)
        return "DummyChatResponse"
