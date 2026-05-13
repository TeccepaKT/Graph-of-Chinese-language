"""

Изучение иероглифов по словарям

"""

import json
from typing import Callable

from word_similarity import WordSimilarity2010

from chinese import Hieroglyph
from utils.functions import Num
from researcher import Researcher
from work_with_bases.dicts_base import dicts_base
from hieroglyph_frequency_lists.hier_dictionaries import subtlex_dictionary


similarity: Callable[[Hieroglyph, Hieroglyph], Num] = WordSimilarity2010().similarity  # Схожесть двух иероглифов


def get_relations(base_hier: Hieroglyph, pool: list[Hieroglyph]) -> list[tuple[Hieroglyph, Num]]:
    """ Получение ближайших по смыслу иероглифов среди данных """
    sim: list[tuple[Hieroglyph, Num]] = []
    min_sim: Num = 0.8  # Наименьшая связь для вхождения в ответ
    to_sim: Num = 0.1  # Нормализация значения: оно будет в [to_sim, 1]
    
    for hier in pool:
        if hier == base_hier:
            continue
        
        s: Num = similarity(hier, base_hier)
        if s < min_sim:
            continue  # Слишком малая схожесть

        value: Num = 1 - (1 - s) / (1 - min_sim) * (1 - to_sim)  # Нормализация
        sim.append((Hieroglyph.from_validated(hier), value))  # Добавление
    
    sim.sort(key=lambda t: t[1], reverse=True)  # Сначала наиболее похожие
    return sim


class DictsResearcher(Researcher):
    """ Исследователь иероглифов со словарями """

    # Параметры изучения
    _pool_size: int = 3000  # Рассматривать иероглифов в словаре

    # Поля
    pool: list[Hieroglyph]  # Рассматриваемые иероглифы

    def __init__(self):
        self.pool = subtlex_dictionary.get_frequency_list()[:self._pool_size]

    def research(self, hier: Hieroglyph):
        """ Изучение иероглифа относительно иероглифов из pool """
        if hier not in self.pool:
            raise ValueError('This hieroglyph is not in the pool. Increase the _pool_size value')

        relations: list[tuple[Hieroglyph, Num]] = get_relations(hier, self.pool)
        text: str = json.dumps({'related_words': relations})
        dicts_base.form_and_write(hier, text, rewrite=True)
