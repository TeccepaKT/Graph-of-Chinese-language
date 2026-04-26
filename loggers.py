import sys

from typing import Callable
from abc import ABC
from functools import wraps


class DepthLogger(ABC):
	""" Логгирование вызовов функций (или похожего стека) """
	_depth: int = 0  # Размер стека (глубина) вызовов функций

	@staticmethod
	def get_depth() -> int:
		return DepthLogger._depth

	@staticmethod
	def add_depth(value: int = 1):
		""" Увеличить глубину (уровень вложенности) лога.
			Глубина влияет на отображение """
		DepthLogger._depth += value

	@staticmethod
	def reduce_depth(value: int = 1):
		DepthLogger.add_depth(-value)


class AIDebugLogger(DepthLogger):
	""" Логгер для работы с AI """
	_file = open('./research_ai/ai_requests/logger_output.log', 'w')

	@staticmethod
	def log(*args, **kwargs):
		""" Вывести сообщение """
		print(end = ' ' * (2 * AIDebugLogger.get_depth() + 1) + '- ', file=AIDebugLogger._file)
		print(*args, **kwargs, file=AIDebugLogger._file)

	@staticmethod
	def logging(
		level: "0 | 1" = 0  # Уровень лога
	) -> Callable:
		""" Логгирование вызова и завершения функции """
		def deco(f: Callable):
			@wraps(f)
			def wrapper(*args, **kwargs):
				AIDebugLogger.log(f.__name__, 'called')
				AIDebugLogger.add_depth()
				res = f(*args, **kwargs)
				AIDebugLogger.reduce_depth()
				AIDebugLogger.log(f.__name__, 'ended' if level == 0 or AIDebugLogger._depth != 0 else 'ended\n')
				return res

			return wrapper

		return deco


class ResearchLogger(DepthLogger):
	""" Видимые сообщения при Research иероглифов """
	_file = sys.stdout

	@staticmethod
	def log(*args, **kwargs):
		""" Вывести сообщение """
		print(end = ' ' * (4 * ResearchLogger._depth + 1), file=ResearchLogger._file)
		print(*args, **kwargs, file=ResearchLogger._file)
