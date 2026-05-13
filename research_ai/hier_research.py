"""

Изучение с помощью AI

"""

from time import sleep

from chinese import Hieroglyph
from loggers import ResearchLogger as Logger
from researcher import Researcher
from utils.paths import Paths
from utils.functions import random_num
from work_with_bases.ai_base import ai_base
from hieroglyph_frequency_lists.hier_dictionaries import hanzi_dictionary
from research_ai.ai_requests.chat import DummyChat, AIChat


class AIChatResearcher(Researcher):
    """ Исследователь иероглифов с AIChat """

    # Параметры глубокого изучения иероглифа
    max_number: int = 1100  # Наименьший номер в списке частотности для перехода к следующему иероглифу
    min_relation: int = 8  # Наименьшая связь с данным (из базы) для перехода
    max_level: int = 2  # Наибольшая глубина рекурсии (1 - без рекурсии)
    max_researched: int = 1  # Наибольшее кол-во изучений за один запуск
    safety_chat: AIChat = DummyChat() # Используемый чат при safety_mode

    # Поля
    _safety_mode: bool  # Изучение без AI и записи в базу
    _chat: AIChat

    _researched: int = 0  # Всего изучено с момента запуска
    _max_researched_reached: bool = False  # Достижение максимального значения researched
    _research_pause_interval: tuple[int, int] = (5, 8)  # Пауза после одного изучения

    def __init__(self, chat: AIChat, safety_mode: bool = False):
        self._chat = chat
        self._safety_mode = safety_mode

    @staticmethod
    def _get_request_text(hier: Hieroglyph) -> str:
        """ Дать prompt для получения информации о иероглифе """
        with open(Paths.prompt_file, 'r') as f:
            request = f.read().replace('$HIER', hier)
        with open(Paths.format_file, 'r') as f:
            request = request + f'\n\nНапишите строго в формате:\n```json\n{f.read()}\n```'
        return request

    @property
    def safety_mode(self) -> bool:
        """ Находится ли AIChatResearcher в безопасном режиме """
        return self._safety_mode

    @property
    def chat(self) -> AIChat:
        """ Вернуть используемый чат """
        return self._chat if not self.safety_mode else self.safety_chat

    def research(self, hier: Hieroglyph):
        """ Добавить файл о иероглифе, если его ещё нет в базе """
        hier: Hieroglyph = hier.simplified()

        if hier in ai_base:
            Logger.log(f'Already in base: {hier}', type=Logger.MessageType.SPACE)
            return

        # Получение информации
        Logger.log(f'    Considering {hier}...', end='\r', type=Logger.MessageType.VOID)
        json: str = self.chat.get_response(AIChatResearcher._get_request_text(hier))

        # Запись
        if not json:
            raise ValueError('Возвращён пустой ответ. Возможно, он не был скопирован.')
        ai_base.save_raw(hier, json)

        # Исправление формата
        json = json.strip('`')
        if json.startswith('json'):
            json = json[4:]
        json = json.strip()

        # Запись в базу
        if not AIChatResearcher.safety_mode:
            ai_base.form_and_write(hier, json)
        else:
            Logger.log("SAFETY: Добавить PHONY-файл")

        Logger.log(f'Added: {hier}', Logger.MessageType.I)
        self._researched += 1
        sleep(random_num(*self._research_pause_interval))  # Не слишком частые запросы

    def deep_research(self, hier: Hieroglyph, *, level: int = 1):
        """ Глубокое изучение: рекурсивно изучать все (или некоторые) связи """
        if self._researched == self.max_researched:
            Logger.log('The greatest knowledge has been reached', type=Logger.MessageType.SLASH)
            self._max_researched_reached = True
            return

        # Изучение данного иероглифа
        self.research(hier)
        if level == self.max_level:
            return

        # Глубокое изучение
        data: dict = ai_base.read_json(hier)  # Получение информации о иероглифе
        been: set[Hieroglyph] = set()  # Запоминание того, какие иероглифы уже были рассмотрены

        Logger.log(f'Deep research of {hier}:', type=Logger.MessageType.GT)
        Logger.add_depth()

        for word, relation in data['related_words']:  # Просмотр всех связанных слов
            for hier in Hieroglyph.hieroglyphs_from_text(word):  # По иероглифам
                if hier in been or relation < self.min_relation \
                    or hanzi_dictionary.get_frequency_position(hier) > self.max_number:
                    continue  # Недостаточно хорошие характеристики частотности или уже изучен

                self.deep_research(hier, level = level + 1)
                been.add(hier)  # Запоминание

        Logger.reduce_depth()
