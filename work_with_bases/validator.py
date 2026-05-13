"""

Валидация json-файлов на основе JSON Schema

"""

from typing import Optional
from enum import Enum, auto
import json
import jsonschema

from loggers import ResearchLogger as Logger


class Responding(Enum):
    """ Реагирование на несоответствия с JSON Schema """
    SOFT = auto()  # Вывод только о наличии несоответствия формата
    MIXED = auto()  # Вывод только о несоответствии с указанием места
    HARD = auto()  # Бросить исключение при несоответствии с указанием места


def validate(instance: str, schema: dict, responding: Responding = Responding.HARD,
             message: Optional[str] = None) -> bool:
    """ Проверить на соответствие формату
        instance должен быть именно str, так как также проверяется синтаксис """
    try:
        instance = json.loads(instance)
        jsonschema.validate(instance, schema)
        return True

    except Exception as e:
        if message is not None:
            Logger.log(f'Bad format: {message}', type=Logger.MessageType.V)
        if responding == Responding.HARD:
            raise
        if responding == Responding.MIXED:
            print(e)
        return False
