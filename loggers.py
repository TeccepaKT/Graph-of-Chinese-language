"""

Логгирование разных частей программы

"""

import sys

from typing import Callable
from abc import ABC
from enum import Enum, auto
from functools import wraps


class DepthLogger(ABC):
	""" Логгирование вызовов функций (или похожего стека) """
	_depth: int = 0  # Размер стека (глубина) вызовов функций

	@classmethod
	def get_depth(cls) -> int:
		""" Глубина (уровень вложенности) лога.
			Глубина влияет на отображение """
		return DepthLogger._depth

	@classmethod
	def add_depth(cls, value: int = 1):
		""" Увеличить глубину """
		DepthLogger._depth += value

	@classmethod
	def reduce_depth(cls, value: int = 1):
		""" Уменьшить глубину лога """
		DepthLogger.add_depth(-value)


class AIDebugLogger(DepthLogger):
	""" Логгер для работы с AI """
	_file = open('./research_ai/ai_requests/logger_output.log', 'w')

	@classmethod
	def log(cls, *args, **kwargs):
		""" Вывести сообщение """
		print(end=' ' * (2 * cls.get_depth() + 1) + '- ', file=cls._file)
		print(*args, **kwargs, file=cls._file)

	@classmethod
	def logging(cls, importance: int = 0) -> Callable:
		""" Декоратор для логгирование вызовов и завершений функций """
		def deco(f: Callable):
			@wraps(f)
			def wrapper(*args, **kwargs):
				cls.log(f.__name__, 'called')
				cls.add_depth()
				res = f(*args, **kwargs)
				cls.reduce_depth()
				cls.log(f.__name__, 'ended' if importance == 0 or cls._depth != 0 else 'ended\n')
				return res

			return wrapper

		return deco


class ResearchLogger(DepthLogger):
	""" Видимые сообщения при Research иероглифов """
	_file = sys.stdout

	class MessageType(Enum):
		""" Типы сообщений """
		SPACE = auto()
		I = auto()
		V = auto()
		UNDERSCORE = auto()
		STAR = auto()
		SLASH = auto()
		VOID = auto()
		GT = auto()

	@classmethod
	def log(cls, *args, end: str = '\n', type: MessageType = MessageType.SPACE):
		""" Вывести сообщение """
		print(end=' ' * (4 * cls._depth + 1), file=cls._file)

		match type:  # TODO: Эта простая в будущем будет изменена
			case cls.MessageType.SPACE:
				print(end='[ ] ')
			case cls.MessageType.I:
				print(end='[i] ')
			case cls.MessageType.V:
				print(end='[v] ')
			case cls.MessageType.UNDERSCORE:
				print(end='[_] ')
			case cls.MessageType.STAR:
				print(end='[*] ')
			case cls.MessageType.SLASH:
				print(end='[/] ')
			case cls.MessageType.VOID:
				print(end='    ')
			case cls.MessageType.GT:
				print(end='[>] ')

		print(*args, end=end, file=cls._file)
