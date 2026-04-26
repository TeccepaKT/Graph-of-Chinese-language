print('[ ] Launch...')

import sys
import re

from time import sleep

from chinese.chinese import is_hieroglyph

from loggers import ResearchLogger as Logger
from work_with_bases.bases import base_ai
from hieroglyph_frequency_lists.hier_dictionaries import \
	subtlex_hier_freq_list, get_frequency_position, simplify
from research_ai.ai_requests.ai_requests import DeepseekChat, DummyChat, rnum


def get_request_text(hier: str) -> str:
	""" Дать prompt для получения информации о иероглифе hier """
	with open('research_ai/Prompt.txt', 'r') as f:
		request = f.read().replace('$HIER', hier)
	with open('research_ai/Format.txt', 'r') as f:
		request = request + f'\n\nНапишите строго в формате:\n```json\n{f.read()}\n```'
	return request


researched: int = 0

def research(hier: str):
	""" Изучить иероглиф hier (добавить файл о нём), если его ещё нет в базе """
	global researched

	hier = simplify(hier)
	if hier in base_ai:
		Logger.log(f'[ ] Already in base: {hier}')
		return

	# Получение информации
	Logger.log(f'    Considering {hier}...', end='\n')
	json = chat.get_response(get_request_text(hier))

	# Запись
	if not json:
		raise ValueError('Возвращён пустой ответ. Возможно, он не был скопирован.')
	base_ai.save_raw(hier, json)

	# Исправление формата
	json = json.strip('`')
	if json.startswith('json'):
		json = json[4:]
	json = json.strip()
	
	# Запись в базу
	if not SAFETY_MODE:
		base_ai.form_and_write(hier, json)
	else:
		Logger.log("SAFETY: Добавить PHONY-файл")

	researched += 1
	Logger.log(f'[i] Added: {hier}')
	sleep(rnum(5, 8))  # Не слишком частые запросы


def deep_research(hier, level: int = 1):
	""" Глубокое изучение: рекурсивно изучать все (или некоторые) связи """
	max_number: int = 1100 # Наименьший номер в списке частотности для перехода
	min_relation: int = 8 # Наименьшая связь с данным (из базы) для перехода
	max_level: int = 2 # Наибольшая глубина рекурсии (1 - без рекурсии)
	max_researched: int = 1 # Наибольшее кол-во изучений

	if researched == max_researched:
		exit(Logger.log("[/] The greatest knowledge has been reached"))

	# Изучение данного иероглифа
	research(hier)
	if level == max_level:
		return

	# Глубокое изучение
	data = base_ai.read_json(hier)  # Получение информации о иероглифе
	been = set()  # Запоминание, какие иероглифы уже были рассмотрены
	Logger.log(f"[>] Deep research of {hier}:")
	Logger.add_depth()

	for word, relation in data['related_words']:  # Просмотр всех связанных слов

		for h in word:  # По иероглифам
			if not is_hieroglyph(h) or h in been:
				continue  # Не иероглиф или уже был
			if relation < min_relation or \
					get_frequency_position(h)['hanzipy'] > max_number:
				continue  # Недостаточно хорошие характеристики частотности
			deep_research(h, level + 1)  # Рекурсия
			been.add(h)  # Запоминание

	Logger.reduce_depth()


def run(safety: bool = False):
    global SAFETY_MODE, chat  # TODO: Это надо сделать по-другому...
    SAFETY_MODE = safety
    
    if not SAFETY_MODE:
        chat = DeepseekChat()
        chat.load()
    else:
        chat = DummyChat()
    
    for i, hier in enumerate(subtlex_hier_freq_list):
        deep_research(hier)
        Logger.log(f'[_] Ended {hier} (№{i + 1}), go forward\n')
        sleep(0.01)

