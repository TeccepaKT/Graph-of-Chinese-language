"""

Смежные по составу иероглифы и их вывод в виде дерева

"""

__version__ = '2.1.0.002 Beta'

"""

Changelog:
	
	2.1.0 (проект)
		+ Раскраска иероглифов по любому параметру (функции)
		Улучшить раскраску на более презентативную
		+ Сортировка дерева усложения по частотности

	2.0.0
		Раскрашивание иероглифов по их частотности
		Функция get_frequency
		Класс Colors с найстройкой цветов
		Добавлен HanziDictionary — словарь с информацией об иероглифах

	1.2.0
		Функция complication_tree
		(удалено) Сортировка узлов в decompose_tree
		Очищение консоли при запуске программы
		Методы обхода дерева

		1.2.1
			Исправлены ошибки в complication_tree

	1.1.0
		Функция draw_tree для отображения дерева
		Использование Node в качестве узла дерева

	1.0.0
		Функция decompose_tree, возвращает словарь со словарями

"""

# 用（画）：
# 	《謌》，《岢》，《哿》

import sys

from typing import Callable, Optional, Any
from collections import Counter
from pprint import pprint
from string import ascii_lowercase

from .chinese import is_hieroglyph
from .pyclr import Ramp, clr, clean
from hanzipy.dictionary import HanziDictionary
from hanzipy.decomposer import HanziDecomposer


#type 
Num = int | float


dictionary: HanziDictionary = HanziDictionary()
decomposer: HanziDecomposer = HanziDecomposer()
frequency: Callable = dictionary.get_character_frequency
decompose: Callable = decomposer.decompose
complicate: Callable = decomposer.get_characters_with_component

decomposed: dict[str, tuple[str]] = {
	h: () for h in
	'丷⼀⼁⼂⼃⼄⼅⼆⼇⼈⼉⼊⼋⼌⼍⼎⼏⼐⼑⼒⼓⼔⼕⼖⼗⼘⼙⼚⼛⼜⼝口⼞'
} | {'𠂇': ('⼀', '⼃')}
# '⼟⼠⼡⼢⼣⼤⼥⼦⼧⼨⼩⼪⼫⼬⼭⼮⼯⼰⼱⼲⼳⼴⼵⼶⼷⼸⼹⼺⼻⼼⼽⼾⼿⽀⽁⽂⽃⽄⽅⽆⽇⽈⽉⽊⽋⽌⽍⽎⽏⽐⽑⽒⽓⽔⽕⽖⽗⽘⽙⽚⽛⽜⽝⽞⽟⽠⽡⽢⽣⽤⽥⽦⽧⽨'

loaded: int = 4645 # Загружено иероглифов


class Node:
	""" Узел дерева """
	def __init__(self, 
		value: Any,
		children: Optional[list['Node']] = None
	):
		self.value = value
		self.children = [] if children is None else children

	def __str__(self) -> str:
		return f'Node(value={self.value}, children={self.children})'

	def iter_ccn(self) -> 'Node':
		""" Обход Childs-Node """
		for ch in self.children:
			for n in ch.iter_ccn():
				yield n
		yield self

	def iter_ncc(self) -> 'Node':
		""" Обход Node-Childs """
		yield self
		for ch in self.children:
			for n in ch.iter_ncc():
				yield n

	def iter_ncncn(self) -> 'Node':
		""" Обход Node-Child1-Node-...-Node """
		yield self
		for ch in self.children:
			for n in ch.iter_ncncn():
				yield n
			yield self

	def add_child(self, node: 'Node'):
		self.children.append(node)

# class ParameterizedNode


def get_frequency(hier: str) -> int:
	""" Частота иероглифа в текстах """
	try:
		freq = int(frequency(hier)['count'])
	except:
		freq = 0

	return freq

def _hieroglyph_color(hier: str) -> str:
	""" Цвет иероглифа """
	freq: int = get_frequency(hier)
	return clr(Colors.frequency_clr(Colors.frequency_function(freq)))

def _check_parameter(hier: str):
	""" Проверить правильность аргумента для построения дерева """
	if len(hier) != 1 or not is_hieroglyph(hier):
		raise ValueError('Is not hieroglyph')


def draw_tree(tree: Node):
	""" Рисование дерева разложения """
	write: Callable = sys.stdout.write # Faster

	# Определение глубины дерева
	m: int = (depth := lambda n: (
		max(depth(ch) for ch in n.children) if n.children else 0
	)+1)(tree) # dfs 
	
	# Таблица дерева
	line: list[Optional[str]] = [None]*m # Пустая линия таблицы для заполнения
	table: list['lineType'] = [line.copy()] # Рисование дерева на поле

	def fill_table(node: Node, depth: int = 0):
		""" Заполнение таблицы ячейками """
		n: int = len(table)-1
		table[n][depth] = str(node.value) # Вставка иероглифа

		for i in range(len(node.children)):
			if i > 0:
				table.append(line.copy()) # Добавление строки в таблицу
			fill_table(node.children[i], depth+1)

	fill_table(tree)
	n: int = len(table)

	# Заполнение таблицы связей между клетками
	connections_table: list[list[int]] = [[View.ConnectionsID.empty]*(m-1) for _ in range(n)]
		# Показывает связь после table[y][x]
	for y in range(n):
		for x in range(m-1):
			if not table[y][x] and table[y][x+1]:
				connections_table[y][x] = View.ConnectionsID.curved
			if table[y][x] and table[y][x+1]:
				connections_table[y][x] = View.ConnectionsID.horizontal

	# Заполнение горизонтальных связей
	pulling: list[bool] = [False]*(m-1) # Ведём curved связи снизу-вверх до пересечения
	for y in range(n-1, -1, -1):
		for x in range(m-1):
			if pulling[x]: # Здесь поднимаем вверх
				match connections_table[y][x]:
					case View.ConnectionsID.curved: # Соединение с другой изогнутой
						connections_table[y][x] = View.ConnectionsID.vertical_intersect
					case View.ConnectionsID.horizontal: # Соединение со связью узла-родителя
						connections_table[y][x] = View.ConnectionsID.horizontal_intersect
						pulling[x] = False # Соединено
					case _:
						connections_table[y][x] = View.ConnectionsID.vertical # Продлеваем
			else:
				if connections_table[y][x] == View.ConnectionsID.curved:
					pulling[x] = True
	
	# Вывод
	for y in range(n):
		for x in range(m):
			if table[y][x]: # Вывод иероглифа
				color: str = _hieroglyph_color(table[y][x]) # Colors.hieroglyph_clr
				write(color + table[y][x])
			else:
				write(View.element_empty)
			if x != m-1: # Вывод связи
				write(Colors.connection_clr + View.connections[connections_table[y][x]])
		write('\n')
	write(clr()) # Сброс цвета


def _decompose_tree(hier: str) -> tuple[Node, list[str]]:
	""" Рекурсивное построение дерева разложения с использованными символами
		-> tuple[node, has|been|was] """

	# Получение разложения
	n: Node = Node(hier)
	dec: dict = decompose(hier)
	been: set[str] = set()

	dec['once'] = set(dec['once']) - {hier}
	dec['radical'] = set(dec['radical']) - {hier}

	# Получение потомков
	for h in dec['once']: # Разложение
		if len(h) != 1: # Не иероглиф
			continue
		if h in decomposed: # Не надо раскладывать
			node: Node = Node(h)
			for p in decomposed[h]:
				node.add_child(_decompose_tree(p)[0])
			n.add_child(node)

			been.add(h)
			been |= set(decomposed[h])
			continue

		node, hbeen = _decompose_tree(h) # Рекурсивное разложение
		n.add_child(node)

		been.add(h)
		been |= hbeen # Использовано

	# Нераскладываемые потомки
	if 'No glyph available' in dec['once']: # Если был неизвестный иероглиф
		for h in dec['radical'] - dec['once'] - been: # Радикалы
			n.add_child(Node(h))
			been.add(h)

	return n, been

def decompose_tree(hier: str) -> Node:
	""" Дерево разложения иероглифа """
	_check_parameter(hier)

	# Построение
	tree: Node = _decompose_tree(hier)[0]
	
	# Сортировка
	def key(ch: Node):
		""" Ключ сортировки """
		n_graphical: list[str] = decompose(n.value)['graphical']  # (global) n
		ch_graphical: list[str] = decompose(ch.value)['graphical']

		return [n_graphical.index(trait) for trait in ch_graphical if trait in n_graphical]

	for n in tree.iter_ccn():
		n.children.sort(key=key, reverse=True) # По заданному hanzipy порядку черт

	return tree


def _complication_tree(hier: str, ancestors: set[str]) -> Node:
	""" Рекурсивное построение дерева усложнения с иероглифами-предками """
	n: Node = Node(hier)
	try:
		comp: Optional[list[str]] = complicate(hier)
	except:
		n.add_child(Node('·····'))
		return n

	# Построение
	if comp:
		ancestors.add(hier) # Вход
		for ch in comp: # DFS
			if ch in ancestors: # Уже был
				continue
			ch: Node = _complication_tree(ch, ancestors)
			n.add_child(ch)
		ancestors.remove(hier) # Выход

	return n

def complication_tree(hier: str) -> Node:
	""" Дерево усложнения иероглифа """
	_check_parameter(hier)

	# Построение
	tree: Node = _complication_tree(hier, set())

	# Сортировка
	for n in tree.iter_ccn():
		n.children.sort(key=lambda n: \
		get_frequency(n.value), reverse=True) # По заданному hanzipy порядку черт

	return tree


s__r: Ramp = Ramp({0.0: 0, 0.1: 0.00342, 0.2: 0.00733, 
			       0.3: 0.02098, 0.4: 0.06536, 0.5: 0.14785, 
			       0.6: 0.24033, 0.7: 0.30385, 0.8: 0.32893, 
			       0.9: 0.33442, 1.0: 0.33648})

class Colors:
	""" Цвета """
	connection_clr = clr((100,)*3) # Цвет соединений
	# hieroglyph_clr = clr((255,)*3) # Цвет иероглифа

	frequency_function: Callable = \
	    lambda x: s__r((x**0.05 - 1) / 1.2035 + 0.03) \
	              if x else 0 # Функция сглаживания непропорциональности

	s__min_frequency: Num = frequency_function(2)
	s__max_frequency: Num = frequency_function(get_frequency('一')) # Максимальное значение

	frequency_clr: Ramp = Ramp({
	                               0: (180, 0, 0), # no used
	     (3/loaded)*s__max_frequency: (220, 20, 0), # used
	(1-2000/loaded)*s__max_frequency: (200, 200, 0), # 2000
	(1-1000/loaded)*s__max_frequency: (30, 200, 0), # 1000
	 (1-100/loaded)*s__max_frequency: (0, 255, 50), # 100
	                s__max_frequency: (0, 255, 150)
	}, bright=True) # Цвета иероглифов при разных значениях частотности


class View:
	""" Вывод """
	element_empty: str = '  '
	
	connections: list[str] = [
		 '     ',
		f' ─── ',
		f' ─┬─ ',
		f'  │  ',
		f'  ├─ ',
		f'  └─ ']

	class ConnectionsID:
		""" Связи между узлами при выводе """
		empty: int = 0
		horizontal: int = 1
		horizontal_intersect: int = 2
		vertical: int = 3
		vertical_intersect: int = 4
		curved: int = 5


def main():
	clean()
	inp: str = input('Input hieroglyph (text): ')

	if len(inp) == 1:
		hier: str = inp
		print('\nComplication tree:')
		draw_tree(complication_tree(hier))

		print('\nDecompose tree:')
		draw_tree(decompose_tree(hier))

	else:
		for hier in inp:
			print(f'\nDecompose tree for {hier}:')
			draw_tree(decompose_tree(hier))

	print()


if __name__ == '__main__':
	main()
