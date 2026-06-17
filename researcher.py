"""

Базовый класс Researcher для изучения иероглифов: получения информации и добавления в базу

"""

from abc import ABC, abstractmethod
from warnings import resetwarnings

from chinese import Hieroglyph


class Researcher(ABC):
    """ Исследователь иероглифов """

    @abstractmethod
    def research(self, hier: Hieroglyph):
        """ Получение информации об иероглифе и добавление в базу """
        raise NotImplementedError('The method is not implemented')

    def deep_research(self, hier: Hieroglyph):
        """ Глубокое изучение иероглифа """
        self.research(hier)  # По умолчанию делает то же, что и research
