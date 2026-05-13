"""

Использование базы AI

"""

import heapq
from typing import Any, Callable, Optional
from collections import defaultdict

import numpy as np
from sklearn.manifold import MDS
from scipy.sparse.csgraph import shortest_path

from chinese import Hieroglyph
from utils.functions import Num
from visualization.builder import Builder, Node, Graph
from work_with_bases.base import Base
from work_with_bases.ai_base import ai_base


class AIBuilder(Builder):
    def get_base(self) -> Base:
        return ai_base

    def _nodes_by_graph(self, out: Graph) -> np.ndarray:
        """ Получить список координат Node по графу с весами в [0, 1]. Должен быть неориентированным """
        n: int = len(out)
        mult: Num = 5.0  # Множитель расстояний для изменения масштаба
        weight_to_dist: Callable[[float], float] = lambda w: 4 + 300 * (1 - w) ** 5  # Перевод весов в расстояния

        adj_matrix: np.ndarray = np.full((n, n), np.inf)  # Матрица смежности графа
        np.fill_diagonal(adj_matrix, 0)

        for u, out_u in out.items():
            for v, w in out_u.items():
                if not 0 <= w <= 1:
                    raise ValueError('Weights must be in [0, 1]')
                adj_matrix[u, v] = mult * weight_to_dist(w)

        adj_matrix_tr: np.ndarray = shortest_path(csgraph=adj_matrix, directed=False, method='FW')  # Транзитивное
            # замыкание (заполняется кратчайшими расстояниями)
        if not np.all(np.isfinite(adj_matrix_tr)):  # Проверка, что компонента связности одна
            raise ValueError('Graph is not connected')  ## Можно добавить обработку

        mds: MDS = MDS(n_components=3, metric='precomputed', metric_mds=True,
                       n_init=30, max_iter=800, eps=1e-3, random_state=42, init='random')
        coords: np.ndarray = mds.fit_transform(adj_matrix_tr)  # Координаты узлов графа в пространстве

        return coords

    def get_graph(self, max_vertices: Optional[int] = None,
                  comp: Callable[[Hieroglyph], bool] = lambda h: h  # Выбор max_vertices иероглифов
                  ) -> tuple[Graph, np.ndarray, list[Hieroglyph]]:
        """ Получение графа
            Если задано число max_vertices, задайте comp для сортировки иероглифов и выбора
             лучших (меньших по отношению comp) среди них """
        out: Graph = {}
        base: Base = self.get_base()
        max_points: Num = 10  # Наибольшее количество очков, которое может получить ребро (чтобы привести веса к [0, 1])

        numbering: dict[Hieroglyph, int] = {}  # Биекция с числами
        at: int = 0

        def number(hier: Hieroglyph):
            """ Добавление иероглифа в словарь и выдача ему номера """
            nonlocal numbering, out, at

            if hier not in numbering:
                numbering[hier] = at
                out[at] = defaultdict(float)
                at += 1

        hieroglyphs: list[Hieroglyph] = []
        if max_vertices is not None:
            hieroglyphs = heapq.nsmallest(max_vertices, base, key=comp)
        else:
            hieroglyphs = list(base)

        for hier in hieroglyphs:  # Можно также добавлять синонимы иероглифов
            number(hier)

        for hier in numbering:
            data: dict[str, Any] = base.read_json(hier)

            # Данные могли повторяться, потому сортируем с reversed и убираем слабые дублированные связи
            rels: list[tuple[Hieroglyph, float]] = sorted(data['related_words'], reverse=True)
            rels = [rels[0]] + [rels[i] for i in range(1, len(rels)) if rels[i][0] != rels[i - 1][0]]

            for sim_hier, sim in rels:
                if sim_hier == hier or sim_hier not in numbering:
                    continue
                out[numbering[hier]][numbering[sim_hier]] += sim / 2
                out[numbering[sim_hier]][numbering[hier]] += sim / 2

        for u in out:
            for v in out:
                out[u][v] /= max_points  # Нормализация значений

        hier_by_number: dict[int, Hieroglyph] = {i: hier for hier, i in numbering.items()}
        hieroglyphs: list[Hieroglyph] = [hier_by_number[i] for i in range(len(hier_by_number))]
        return out, self._nodes_by_graph(out), hieroglyphs


ai_builder: AIBuilder = AIBuilder()
