"""

Цвета в консоли

"""

__version__ = '1.2.2.006 HT'

"""

Changelog deleted

"""

import itertools as it

from typing import TypeAlias, Sequence, Iterable, Optional
from threading import Thread as th
from math import sin, cos, pi
from functools import reduce
from time import time
from os import system


system('') # Включение цветов

Num: TypeAlias = int | float
Coords: TypeAlias = tuple[Num, Num]
RGB: TypeAlias = tuple[Num, Num, Num]
Box: TypeAlias = tuple[Num, Num, Num, Num]

HEX = r'[0-9a-f]{6}'


def array_round(x: Num | Iterable[Num]) -> Num | list[Num]:
	""" Округление числа или массива чисел """
	if isinstance(x, Num):
		return round(x)
	return [round(c) for c in x]


def clr(
		fore: Optional[RGB] = None,
		bg: Optional[RGB] = None
	) -> str:
	""" 
	Возвращает строку, содержащую код изменения цвета при её использовании в консоли
	Если не переданы аргументы, очищает цвет
	 * fore — Цвет букв
	 * bg — Цвет фона
	"""
	if fore is None:
		if bg is None:
			return Commands.nocolor
		return Commands.bg.format(*bg)

	if bg is None:
		return Commands.fore.format(*fore)

	return Commands.fore_bg.format(*fore, *bg)


def clean():
	""" Очистить консоль """
	print(end=Commands.clean)


def bright(
		rgb: Sequence[Num], 
		bright: 'True | Num | Sequence[Num]' = True
	) -> list[Num]:
	"""
	Изменение яркости (интенсивности) цвета.
	 * rgb — Исходный цвет
	 * [ bright: True — Умножение яркости (элементов rgb) на x
		 [ bright: Num — Привести к максимальной яркости (до 255)
		 [ bright: Iterable[Num] — Пропорциональное изменение яркости
	"""
	if bright is True: # До 255
		max_value = max(rgb)
		if max_value == 0: # Чёрный цвет
			return (255,)*len(rgb)
		return [round(c*255/max_value) for c in rgb]

	if isinstance(bright, Num):
		return [round(c*bright) for c in rgb] # Домножение

	return [round(rgb[i]*bright[i]) for i in range(len(rgb))] # Пропорциональное домножение

	
def area(
		minrgb: Sequence[Num], 
		rgb: Sequence[Num], 
		maxrgb: Sequence[Num]
	) -> bool: 
	""" Проверяет, попадает ли rgb в область между minrgb и maxrgb включительно """
	for i in range(len(rgb)):
		if not minrgb[i] <= rgb[i] <= maxrgb[i]:
			return False
	return True


def int_to_oneHEX(
		x: int
	) -> str:
	""" Переводит число в два символа HEX """
	if not 0 <= x <= 255:
		raise ValueError("x must be digit in [0; 255]")
	tohex = {
		0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 
		10:'a', 11:'b', 12:'c', 13:'d', 14:'e', 15:'f'}
	return tohex[x // 16] + tohex[x % 16]
	

def RGB_to_HEX(
		rgb: RGB
	) -> HEX:
	""" Переводит RGB в HEX """
	return reduce(lambda a, b: a+b, [int_to_oneHEX(c) for c in rgb])


T = ...
def ramp(
		ramp: dict[Num, T],
		val: Num,
		bright: bool = False,
	) -> T:
	""" 
	Плавный переход цветов
	 * ramp — Градиент
	          Если значения целые числа, то не округляет результат
	 * val — Значение точки на градиенте для получения цвета
	 * bright — Осветление. Переход цветов не по пропорциональному
	            изменению суммы, а по максимальному значению
	"""

	# Получение значений
	keys: list[Num] = list(ramp.keys())

	# Слишком большие и малые значения
	if val <= keys[0]:
		return ramp[keys[0]]
	elif val >= keys[-1]:
		return ramp[keys[-1]]

	# Поиск вхождения val в область между ключами [l; r)
	for l, r in it.pairwise(keys):
		if l <= val < r:
			break

	# Получение интерполяции (промежуточного значения)
	mixing: 'float in [0; 1)' = (val-l) / (r-l)

	if not isinstance(ramp[l], Sequence): # Число
		return ramp[l] + mixing*(ramp[r]-ramp[l])

	elements: int = len(ramp[l]) # Кол-во элементов
	mix: Callable[[int, int], int] = lambda a, b, coeff: \
		round(a + coeff*(b-a))
	mixrgb: Sequence[int] = [
		mix(ramp[l][i], ramp[r][i], mixing)
		for i in range(elements)
	] # Интерполяция

	# Осветление
	if bright:
		lmax, rmax = max(ramp[l]), max(ramp[l])
		needmax = mix(lmax, rmax, mixing) # Нужный максимум
		mixmax = max(mixrgb) # Текущий максимум

		mixrgb: Sequence[int] = [
			round(mixrgb[i] * needmax / mixmax)
			for i in range(elements)
		] # Пропорциональное изменение максимума

	return mixrgb


class Commands:
	""" Команды изменения цветов в консоли """
	nocolor: str = '\033[0;0m' # Очищение цвета
	fore: str = '\033[38;2;{};{};{}m' # Цвет букв
	bg: str = '\033[48;2;{};{};{}m' # Цвет фона
	fore_bg: str = fore + bg # Цвет букв и фона
	clean: str = '\033[H\033[J' # Очищение консоли (cls)


class Colors:
	""" Цвета в Sublime Text """
	name = clr((216, 222, 233))      # <a> = 1
	num = clr((249, 174, 87))      # a = <1> | class <classname> | (курсор: |)
	func = clr((102, 153, 204))      # <foo>()
	text = clr((153, 199, 148))      # "<text>"
	mark = clr((96, 180, 180))      # <">text" | def <foo>
	oper = clr((198, 149, 198))      # for return def class
	comm = comma = clr((166, 172, 185))  # # ,
	math = clr((249, 123, 87))      # | + - * /
	none = clr((236, 96, 102))          # None


class CmdClr:
	""" Цвета в консоли """
	_PROC = (200, 50, 0)
	_CMD = (12, 12, 12)
	SPEED = clr((200, 15, 30))  # ----- 2.0/5.9 kB<1.1 MB/s>eta 0:00:00 | ERROR
	PROC = clr(_PROC)      #<---  >2.0/5.9 kB 1.1 MB/s eta 0:00:00
	PROC_END = clr((200, 155, 0))  #<----->2.0/5.9 kB 1.1 MB/s eta 0:00:00
	TIME = clr((60, 150, 220))  # ----- 2.0/5.9 kB 1.1 MB/s eta<0:00:00>
	ELEM = clr((20, 160, 15))  # -----<2.0/5.9 kB>1.1 MB/s eta 0:00:00
	CMD = clr(_CMD)   # console color


class Ramp:
	""" Плавный переход цветов или значений """
	def __init__(self, ramp: dict[Num, T], bright: bool = False):
		self.ramp = ramp
		self.bright = bright


	def __call__(self, value: Num) -> T:
		""" Получить значение по value """
		return ramp(self.ramp, value, bright=self.bright)


def main():

	# Clr
	print(clr((0, 255, 200)) + 'Hello world!' + clr() + '\n')

	# Ramp
	text: str = 'Hello Ramp!'
	value: dict = {0: (255, 0, 200), len(text)-1: (255, 200, 0)}
	
	# Variant 1: function
	for i in range(len(text)):
		print(end = clr(ramp(value, i, bright=True)) + text[i])
	print(clr()) # Сброс цвета

	# Variant 2: class
	"""
	r: Ramp = Ramp(value)
	for i in range(len(text)):
		print(end = clr(r(i)) + text[i])
	print(clr()) # Сброс цвета
	"""

	print()


if __name__ == '__main__':
	main()
