"""

Получение частотности иероглифов, списков частотностей; упрощение иероглифов

Используемые словари:
  - BCC - основан на новостях, статьях, литературный и официальный языки
  - SUBTLEX-CH - основан на субтитрах, разговорный язык
  - hanzipy - неизвестно

Используйте переменные:
  - <dict>_hier_freq_list
  - <dict>_hier_in_freq_list_by_position
  - <dict>_hier_freq_dict[hier][any_stat...]

  , где dict - bcc или subtlex

"""

from statistics import mean

from opencc import OpenCC
from hanzipy.dictionary import HanziDictionary

from chinese.chinese import is_hieroglyph


simplify = OpenCC('t2s').convert  # Конвертирование иероглифа в упрощенный, если он был традиционный
INF = float('inf')


def get_frequency_position(hier):
	""" Вернуть позицию иероглифа в списках частотности
		Использует INF, если не найдено в списке """
	try:
		hanzipy_stat = dictionary.get_character_frequency(hier)['number']
	except:
		hanzipy_stat = INF

	return {
		'bcc': bcc_hier_in_freq_list_by_position[hier] if hier in bcc_hier_in_freq_list_by_position else INF,
		'subtlex': subtlex_hier_in_freq_list_by_position[hier] if hier in subtlex_hier_in_freq_list_by_position else INF,
		'hanzipy': hanzipy_stat
	}

def get_mean_frequency_position(hier):
	""" Среднее по словарям, в которых есть этот иероглиф """
	d = get_frequency_position(hier)
	return mean(val for val in d.values() if val != INF)


def get_count_per_million(hier):
	""" Вернуть характеристику иероглифа
		Использует INF, если не найдено в списке """
	try:
		hanzipy_stat = int(dictionary.get_character_frequency(hier)['count']) / 1.95e8 * 1e6
	except:
		hanzipy_stat = INF

	return {
		'bcc': bcc_hier_freq_dict[hier] / 2.85e10 * 1e6 if hier in bcc_hier_freq_dict else INF,
		'subtlex': subtlex_hier_freq_dict[hier]['CHR/million'] if hier in subtlex_hier_freq_dict else INF,
		'hanzipy': hanzipy_stat
	} # Почти точные значения для этого иероглифа иер./миллион

def get_mean_count_per_million(hier):
	""" Среднее по словарям, в которых есть этот иероглиф """
	d = get_count_per_million(hier)
	return mean(val for val in d.values() if val != INF)


## Загрузка списков частотности иероглифов
# BCC
with open('hieroglyph_frequency_lists/lists/BCC/global_wordfreq.release.txt', 'r', encoding='GB18030') as f:
	bcc_word_freq_dict = f.readlines()
	bcc_word_freq_dict = [l.strip().split('\t') for l in bcc_word_freq_dict]
	bcc_word_freq_dict = {t[0]: int(t[1]) for t in bcc_word_freq_dict if len(t) == 2}

bcc_hier_freq_dict = {}
for word, count in bcc_word_freq_dict.items():
	for symb in word:
		if not is_hieroglyph(symb):
			continue

		if symb in bcc_hier_freq_dict:
			bcc_hier_freq_dict[symb] += count
		else:
			bcc_hier_freq_dict[symb] = count

bcc_hier_freq_list = sorted(bcc_hier_freq_dict, key=lambda h: bcc_hier_freq_dict[h], reverse=True)
bcc_hier_in_freq_list_by_position = {bcc_hier_freq_list[i]: i
	for i in range(len(bcc_hier_freq_list))}

# SUBTLEX-CH
with open('hieroglyph_frequency_lists/lists/SUBTLEX-CH/SUBTLEX-CH-CHR', 'r', encoding='GB18030') as f:
	subtlex_hier_freq_dict = f.readlines()[3:]
	subtlex_hier_freq_dict = [l.strip().split('\t') for l in subtlex_hier_freq_dict]
	subtlex_hier_freq_dict = {t[0]: {
		'CHRCount': int(t[1]),
		'CHR/million': float(t[2]),
		'logCHR': float(t[3]),
		'CHR-CD': int(t[4]),
		'CHR-CD%': float(t[5]),
		'logCHR-CD': float(t[6])
	} for t in subtlex_hier_freq_dict}

subtlex_hier_freq_list = sorted(subtlex_hier_freq_dict, key=lambda h:
	subtlex_hier_freq_dict[h]['CHRCount'], reverse=True)
subtlex_hier_in_freq_list_by_position = {subtlex_hier_freq_list[i]: i
	for i in range(len(subtlex_hier_freq_list))}

# HanZi
dictionary = HanziDictionary()  # Словарь Hanzi для получения частотностей иероглифов

