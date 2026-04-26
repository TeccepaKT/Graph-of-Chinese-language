from enum import Enum, auto

import json
import jsonschema


class Responding(Enum):
    SOFT = auto()  # Только вывод о наличии несоответствия формата
    MIXED = auto()  # Только вывод о несоответствии с указанием места ошибки
    HARD = auto()  # Бросить исключение при несоответствии


invalid_identifiers: list[str] = []  # Объекты для исправления


def validate(instance: str, schema: object, responding: Responding = Responding.HARD, identifier: str = ''):
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

