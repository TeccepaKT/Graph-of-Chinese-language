"""

Валидация json-файлов на основе JSON Schema

"""

from enum import Enum, auto

import json
import jsonschema


class Responding(Enum):
    """ Реагирование на несоответствия с JSON Schema """
    SOFT = auto()  # Вывод только о наличии несоответствия формата
    MIXED = auto()  # Вывод только о несоответствии с указанием места
    HARD = auto()  # Бросить исключение при несоответствии с указанием места


invalid_identifiers: list[str] = []  # Объекты для исправления


def validate(instance: str, schema: dict, responding: Responding = Responding.HARD, identifier: str = ''):
    """ Проверить на соответствие формату
        instance должен быть именно str, так как проверяется и синтаксис """
    try:
        instance = json.loads(instance)
        jsonschema.validate(instance, schema)

    except Exception as e:
        print(f'[v] Bad format: {identifier}')
        if responding == Responding.HARD:
            raise
        if responding == Responding.MIXED:
            print(e)
        invalid_identifiers.append(identifier)

