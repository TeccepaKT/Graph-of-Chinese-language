"""

Функции для других программ

"""

from typing import TypeAlias
from random import seed, randint


Num: TypeAlias = int | float

seed(32)


def random_num(a: float, b: float, acc: int = 10000) -> float:
    """ Случайное число в [a, b] """
    return a + (b - a) * randint(0, acc) / acc
