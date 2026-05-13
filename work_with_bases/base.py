"""

Работа с базой иероглифов

"""

import os
import json
from typing import Any
from time import time

from chinese import is_hieroglyph, Hieroglyph
from utils.paths import Paths
from loggers import ResearchLogger as Logger
from work_with_bases import validator


class Base:
    """ Класс для работы с базой иероглифов
        Смотрите комментарии в коде Base """
    
    _path: str  # Путь к папке
    _additional_format_info: dict[str, Any]  # Информация, приписываемая к новым файлам
    # Добавляйте нижнее подчёркивание в начале к этим ключам, чтобы валидатор не обращал внимания
    #  на то, что добавлены неизвестные ключи

    _contains: set[Hieroglyph]  # Иероглифы, находящиеся в базе
    _path_to_saves: str  # Путь к файлам, которые будут продублированы, чтобы не потерять их при ошибке (опционально)
    _valid_format_scheme: dict  # Схема правильного json-формата для валидации файлов в базе (обязателен)

    def __init__(self, path: str, additional_format_info: dict[str, Any]):
        if not os.path.isdir(path):
            raise ValueError('It is not a directory')

        # Переменные
        self._path = path
        self._additional_format_info = additional_format_info
        self._contains = set()
        self._path_to_saves = f'{path}/{Paths.Base.path_to_saves}'  # Может не существовать

        validate_file_path: str = f'{self._path}/{Paths.Base.validate_format_file}'
        if not os.path.isfile(validate_file_path):
            raise FileNotFoundError(f'The base must contain a {validate_file_path} file')

        with open(validate_file_path, 'r') as f:
            self._valid_format_scheme = json.load(f)

        # Загрузка иероглифов, уже находящихся в базе
        for filename in os.listdir(path):
            hier_path: str = f'{path}/{filename}'
            if not os.path.isfile(hier_path):
                continue
            
            pack: list[str] = filename.split('.')
            if len(pack) != 2 or len(pack[0]) != 1 or not is_hieroglyph(pack[0]) or pack[1] != 'json':
                continue
            self._contains.add(Hieroglyph.from_validated(pack[0]))

        # Валидация
        Logger.log('Base validation...', type=Logger.MessageType.V)

        invalid: list[str] = self.validate()
        if invalid:
            text: str = ' '.join(invalid)
            Logger.log(f'Please fix the following: {text}', type=Logger.MessageType.V)

        Logger.log('Base may be invalid' if invalid else 'Base is validated', type=Logger.MessageType.V)

    def __contains__(self, hier: Hieroglyph) -> bool:
        """ Есть ли иероглиф в базе """
        return hier in self._contains

    def __iter__(self):
        return iter(self._contains)

    # Чтение из базы
    def read_text(self, hier: Hieroglyph) -> str:
        """ Вернуть информацию о иероглифе из базы """
        if hier not in self:
            raise KeyError('Cannot read hieroglyph data from base: it does not exists here')

        path: str = f'{self._path}/{hier}.json'
        with open(path, 'r') as f:
            data = f.read()
        
        return data

    def read_json(self, hier: Hieroglyph) -> dict:
        """ Прочесть из базы json-файл """
        return json.loads(self.read_text(hier))

    # Запись в базу
    def _attach_additional_info(self, text: str) -> str:
        """ Добавить дополнительную информацию в json-текст для записи в файл """
        add = ''
        for key, val in self._additional_format_info.items():
            key = repr(key).replace("'", '"')
            val = repr(val).replace("'", '"')
            add += f'\n    {key}: {val},'

        text = text[0] + add + text[1:]
        return text

    def save_raw(self, hier: Hieroglyph, text: str):
        """ Функция для сохранения необработанных ответов без добавления доп. информации и проверки на формат
            Если папки с соответствующими сохранениями нет, ничего не делает
            Нужно, чтобы не потерять ответ в случае ошибки """
        if not os.path.isdir(self._path_to_saves):
            return  # Если папка не создана, ничего не делать
        
        path = f'{self._path_to_saves}/{hier} {int(time())}.json'
        with open(path, 'w') as f:
            f.write(text)

    def form_and_write(self, hier: Hieroglyph, text: str, *, rewrite: bool = False):
        """ Безопасно добавить файл для иероглифа с содержимым text
            В файл допишутся дополнительные данные
            Кроме того, пройдёт проверка файла на формат """
        text = self._attach_additional_info(text)
        validator.validate(text, self._valid_format_scheme, responding=validator.Responding.SOFT, identifier=hier)

        path = f'{self._path}/{hier}.json'
        if os.path.exists(path) and not rewrite:
            print(f"[*] File already exists: {path}. Did not rewrite")
            return

        with open(path, 'w') as f:
            f.write(text)
        self._contains.add(hier)

    def validate(self) -> list[str]:
        """ Проверить файлы базы. Возвращает список объектов с некорректным содержимым """
        invalid: list[str] = []

        for hier in self:
            if not validator.validate(self.read_text(hier), self._valid_format_scheme,
                                      responding=validator.Responding.MIXED, message=hier):
                invalid.append(hier)

        return invalid
