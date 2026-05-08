"""

Основной модуль

"""

from __future__ import annotations
from typing import TypeAlias, Callable

import pinyin
from opencc import OpenCC


__version__ = '1.5.1 HT'


HierSymb: TypeAlias = str  # Одиночный символ иероглифа
HierStr: TypeAlias = str  # Строка иероглифов


simplify: Callable[[str], str] = OpenCC('t2s').convert  # Конвертирование иероглифа в упрощенный


def is_hieroglyph(symb: str) -> bool:
    """ Является ли символ иероглифом """
    return 19968 <= ord(symb) <= 40959


class Hieroglyph(str):
    """ Китайский иероглиф """

    def __new__(cls, symb: HierSymb) -> Hieroglyph:
        """ Проверка, что строка является иероглифом, и возвращение объекта """
        if not is_hieroglyph(symb):
            raise ValueError("Parameter 'symb' must be a hieroglyph")

        obj = super().__new__(cls, symb)
        return obj

    @classmethod
    def from_validated(cls, hier: HierSymb) -> Hieroglyph:
        """ Получить объект Hieroglyph без проверки """
        return super().__new__(cls, hier)  # Это не str

    @classmethod
    def hieroglyphs_from_text(cls, text: str) -> list[Hieroglyph]:
        """ Дать список Hieroglyph из текста """
        return [cls.from_validated(char) for char in text if is_hieroglyph(char)]

    @property
    def pinyin(self) -> str:
        """ Получить pinyin иероглифа """
        return pinyin.get(self)

    def __repr__(self) -> str:
        return f'Hieroglyph(symb={repr(str(self))}, pinyin={repr(self.pinyin)})'

    def simplified(self) -> Hieroglyph:
        """ Получить упрощённую версию иероглифа """
        return Hieroglyph.from_validated(simplify(self))
