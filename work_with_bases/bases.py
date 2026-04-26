"""

Работа с базой иероглифов

"""

import os
import json

from typing import Any
from time import time

from chinese import is_hieroglyph
from work_with_bases import validator


class Base:
    """ Класс для работы с базой иероглифов
        Смотрите комментарии в коде Base """
    
    _path: str  # Путь к папке
    _additional_format_info: dict[str, Any]  # Информация, приписываемая к новым файлам
        # Добавляйте нижнее подчёркивание в начале к этим ключам, чтобы валидатор не обращал внимания
        #  на то, что добавлены неизвестные ключи

    _contains: set[str]  # Иероглифы, находящиеся в базе
    _path_to_saves: str  # Путь к файлам, которые будут продублированы, чтобы не потерять их при ошибке (опционально)
    _valid_format_scheme: object  # Схема правильного json-формата для валидации файлов в базе (обязателен)
    
    
    def __init__(self, path: str, additional_format_info: dict[str, Any] = {}):
        if not os.path.isdir(path):
            raise ValueError('It is not a base')

        # Переменные
        self._path = path
        self._additional_format_info = additional_format_info
        self._contains = set()
        self._path_to_saves = f'{path}/save_raw'  # Может не существовать
        
        with open(f'{self._path}/.valid_format.json', 'r') as f:  # TODO: Делать проверку и написать, что это необходимо для базы
            self._valid_format_scheme = json.load(f)

        # Загрузка иероглифов, уже находящихся в базе, а также валидация их файлов
        for filename in os.listdir(path):
            hierpath: str = f'{path}/{filename}'
            if not os.path.isfile(hierpath):
                continue
            
            pack = filename.split('.')
            if len(pack) != 2 or len(pack[0]) != 1 or not is_hieroglyph(pack[0]) or pack[1] != 'json':
                continue
            hier, ext = pack
            
            with open(hierpath) as f:
                hiertext = f.read()
            validator.validate(hiertext, self._valid_format_scheme, responding=validator.Responding.MIXED, identifier=hier)
            
            self._contains.add(hier)

        print('[v] Base validated')
        if validator.invalid_identifiers:
            print(f'[v] Please fix the following: {" ".join(validator.invalid_identifiers)}')


    def __contains__(self, hier: str) -> bool:
        """ Есть ли иероглиф в базе """
        return hier in self._contains

    
    def __iter__(self):
        return iter(self._contains)
    
    
    # Чтение из базы
    def read_text(self, hier: str) -> str:
        """ Вернуть информацию о иероглифе из базы """
        if hier not in self:
            raise KeyError('Cannot read hieroglyph data from base: it does not exists here')

        path: str = f'{self._path}/{hier}.json'
        with open(path, 'r') as f:
            data = f.read()
        
        return data


    def read_json(self, hier: str) -> dict | list:
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


    def save_raw(self, hier: str, text: str):
        """ Функция для сохранения необработанных ответов без добавления доп. информации и проверки на формат
            Если папки с соответствующими сохранениями нет, ничего не делает
            Нужно, чтобы не потерять ответ в случае ошибки """
        if not os.path.isdir(self._path_to_saves):
            return  # Если папка не создана, ничего не делать
        
        path = f'{self._path_to_saves}/{hier} {int(time())}.json'
        with open(path, 'w') as f:
            f.write(text)


    def form_and_write(self, hier: str, text: str, *, rewrite: bool = False):
        """ Безопасно добавить файл для hier с содержимым text
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


# Базы с версиями форматирования
base_ai: Base = Base('research_ai/hier_base', {'_version': '1.3.1'})
base_dicts: Base = Base('research_dictionaries/hier_base', {'_version': '1.0.0'})

