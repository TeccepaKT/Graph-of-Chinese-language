"""

Создание списков узлов для визуализации

"""

from typing import TypeAlias, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import dist

from utils.functions import Num
from work_with_bases.base import Base


Graph: TypeAlias = dict[int, dict[int, Num]]  # Взвешенный граф


@dataclass
class Node:
    """ Узел графа """
    x: float
    y: float
    z: float

    def coords(self):
        """ Получить кортеж координат """
        return self.x, self.y, self.z


class Builder(ABC):
    """ Класс для создания графов """

    @abstractmethod
    def get_base(self) -> Base:
        """ Рабочая база """
        raise NotImplementedError()

    @abstractmethod
    def get_graph(self, max_vertices: Optional[int] = None):
        """ Получение всех объектов """
        raise NotImplementedError()

    # TODO:
    # @abstractmethod
    # def get_close_graph(self, hier: Hieroglyph) -> list[Node]:
    #     """ Получение объектов, близких к данному """
    #     raise NotImplementedError()


def node_dist(a: Node, b: Node) -> float:
    """ Расстояние между узлами """
    return dist(a.coords(), b.coords())
