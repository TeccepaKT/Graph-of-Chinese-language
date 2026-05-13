"""

Получение частотности иероглифов, списков частотностей

Используемые словари:
  - BCC - основан на новостях, статьях, литературный и официальный языки
  - SUBTLEX-CH - основан на субтитрах, разговорный язык
  - hanzipy - неизвестно

"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Callable, Optional
from functools import wraps

from utils.functions import Num
from utils.paths import Paths
from hanzipy.dictionary import HanziDictionary, NotAHanziCharacter
from chinese.chinese import Hieroglyph


__version__ = '2.0.0 HT'  # Changelog deleted


INF: float = float('inf')


class SingletonMeta(type):
    """ Singleton метакласс """
    _instances: dict[type, object] = {}

    def __call__[T](cls: T, *args, **kwargs) -> T:
        """ Создать объект или использовать созданный """
        if cls not in cls._instances:
            instance: object = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonABCMeta(SingletonMeta, ABCMeta):
    """ Singleton метакласс с поддержкой абстрактных методов """
    pass


class Dictionary(metaclass=SingletonABCMeta):
    """ Словарь с ленивой инициализацией """
    _is_ready: bool = False

    @abstractmethod
    def _initialize_func(self):
        """ Получить необходимые ресурсы """
        raise NotImplementedError()

    def is_dictionary_ready(self):
        """ Можно ли уже использовать словарь """
        return self._is_ready

    def prepare_dictionary(self):
        """ Инициализация словаря, если он ещё не готов """
        if not self.is_dictionary_ready():
            self._initialize_func()
            self._is_ready = True

    @staticmethod
    def requires_initialize(func: Callable) -> Callable:
        """ Декоратор для методов, требующих инициализации словаря """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.prepare_dictionary()
            return func(self, *args, **kwargs)

        return wrapper


class HanZiDictionary(Dictionary):
    """ Словарь HanZi (модуль hanzipy) """
    _dictionary: Optional[HanziDictionary] = None

    def _initialize_func(self):
        """ Инициализация словаря HanZi """
        self._dictionary = HanziDictionary()

    @Dictionary.requires_initialize
    def get_frequency_position(self, hier: Hieroglyph, default: Num = INF) -> Num:
        """ Получить позицию иероглифа в списке частотности, если он найден, иначе default """
        try:
            return self._dictionary.get_character_frequency(hier)['number']
        except (NotAHanziCharacter, KeyError):
            return default

    @Dictionary.requires_initialize
    def get_count_per_million(self, hier: Hieroglyph, default: Num = INF) -> Num:
        """ Получить количество вхождений иероглифа на миллион, если он найден, иначе default """
        try:
            return int(self._dictionary.get_character_frequency(hier)['count']) / 1.95e8 * 1e6
        except (NotAHanziCharacter, KeyError):
            return default


class BCCDictionary(Dictionary):
    """ Словарь BCC """
    _word_freq_dict: dict[str, int]
    _hier_freq_dict: dict[Hieroglyph, int]
    _hier_freq_list: list[Hieroglyph]
    _hier_position_in_freq_list: dict[Hieroglyph, int]

    def _initialize_func(self):
        """ Инициализация словаря BCC """
        with open(Paths.bcc_dictionary, 'r', encoding='GB18030') as f:
            lines: list[str] = f.readlines()
            table: list[list[str]] = [line.strip().split('\t') for line in lines]

        self._word_freq_dict = {t[0]: int(t[1]) for t in table if len(t) == 2}
        self._hier_freq_dict = {}

        for word, count in self._word_freq_dict.items():
            for hier in Hieroglyph.hieroglyphs_from_text(word):
                if hier in self._hier_freq_dict:
                    self._hier_freq_dict[hier] += count
                else:
                    self._hier_freq_dict[hier] = count

        self._hier_freq_list = sorted(self._hier_freq_dict,
                                      key=lambda h: self._hier_freq_dict[h], reverse=True)
        self._hier_position_in_freq_list = {self._hier_freq_list[i]: i
                                            for i in range(len(self._hier_freq_list))}

    @Dictionary.requires_initialize
    def get_frequency_position(self, hier: Hieroglyph, default: Num = INF) -> Num:
        """ Получить позицию иероглифа в списке частотности, если он найден, иначе default """
        return self._hier_position_in_freq_list[hier] if hier in self._hier_position_in_freq_list else default

    @Dictionary.requires_initialize
    def get_count_per_million(self, hier: Hieroglyph, default: Num = INF) -> Num:
        """ Получить количество вхождений иероглифа на миллион, если он найден, иначе default """
        return self._hier_freq_dict[hier] / 2.85e10 * 1e6 if hier in self._hier_freq_dict else default

    @Dictionary.requires_initialize
    def get_frequency_list(self) -> list[Hieroglyph]:
        """ Получить список частотности иероглифов """
        return self._hier_freq_list


class SubtlexDictionary(Dictionary):
    """ Словарь SUBTLEX """
    _hier_stat_dict: dict[Hieroglyph, dict]
    _hier_freq_list: list[Hieroglyph]
    _hier_position_in_freq_list: dict[Hieroglyph, int]

    def _initialize_func(self):
        """ Инициализация словаря SUBTLEX-CH """
        with open(Paths.subtlex_dictionary, 'r', encoding='GB18030') as f:
            lines: list[str] = f.readlines()[3:]
            table: list[list[str]] = [line.strip().split('\t') for line in lines]

        self._hier_stat_dict = {Hieroglyph(t[0]): {
            'CHRCount': int(t[1]),
            'CHR/million': float(t[2]),
            'logCHR': float(t[3]),
            'CHR-CD': int(t[4]),
            'CHR-CD%': float(t[5]),
            'logCHR-CD': float(t[6])
        } for t in table}

        self._hier_freq_list = sorted(self._hier_stat_dict, key=lambda h:
                                      self._hier_stat_dict[h]['CHRCount'], reverse=True)
        self._hier_position_in_freq_list = {self._hier_freq_list[i]: i
                                            for i in range(len(self._hier_freq_list))}

    @Dictionary.requires_initialize
    def get_frequency_position(self, hier: Hieroglyph, default: Num = INF) -> Num:
        """ Получить позицию иероглифа в списке частотности, если он найден, иначе default """
        return self._hier_position_in_freq_list[hier] if hier in self._hier_position_in_freq_list else default

    @Dictionary.requires_initialize
    def get_count_per_million(self, hier: Hieroglyph, default: Num = INF) -> Num:
        """ Получить количество вхождений иероглифа на миллион, если он найден, иначе default """
        return self._hier_stat_dict[hier]['CHR/million'] if hier in self._hier_stat_dict else default

    @Dictionary.requires_initialize
    def get_frequency_list(self) -> list[Hieroglyph]:
        """ Получить список частотности иероглифов """
        return self._hier_freq_list


hanzi_dictionary: HanZiDictionary = HanZiDictionary()
bcc_dictionary: BCCDictionary = BCCDictionary()
subtlex_dictionary: SubtlexDictionary = SubtlexDictionary()
