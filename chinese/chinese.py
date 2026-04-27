"""

Основной модуль

Китайский шрифт в консоли: chcp 936

"""

__version__ = '1.3.0.011 HT'

"""

Changelog:

	1.3.0
		Получение разложения иероглифа перенесено в модуль adjacency.py
		Другой способ получения изображений иероглифов

	1.2.0
		Подключение wikipedia
		Получение разложения иероглифа

	1.1.0
		Использование шрифтов для быстрого получения изображений

	1.0.1
		Настройка получаемых значений

	1.0.0
		Получение изображения иероглифа через trainchinese.com
		Класс Hieroglyph

"""

from typing import TypeAlias, Optional

import pinyin
import urllib.request

from PIL import Image, ImageFont
from PIL.ImageDraw import Draw


HierSymb: TypeAlias = str # Одиночный символ иероглифа
HierStr: TypeAlias = str # Строка иероглифов
Pinyin: TypeAlias = str # Пиньинь

FONTPATH: str = 'C:/Python/P/fonts/KaiTi.ttf'


def is_hieroglyph(symb: str) -> int:
	""" Является ли символ иероглифом """
	return 19968 <= ord(symb) <= 40959


def get_hieroglyph_images(
	text: HierStr, 
	width: int = 400, 
	font_path: str = None
) -> list[Image.Image]:
	""" Дать массив с изображениями иероглифов из строки """
	len_text = len(text)

	# новое изображение
	img = Image.new('1', (width*len_text, width), True)
	draw = Draw(img)
	
	# вставить текст
	font = ImageFont.truetype(font_path or FONTPATH, width, encoding='utf-8')
	draw.text((0, 0), text, font=font, size=width)
	
	# получение изображений
	return [img.crop((width*i, 0, width*(i+1), width)) for i in range(len_text)]


# def get_hieroglyph_gif(symb: HierSymb) -> Image.Image:
# 	""" Дать изображение иероглифа """
# 	urllib.request.urlretrieve(f'https://www.trainchinese.com/v2/charTracing/Simplified/{ord(symb)}.gif', 'P/1.gif')
# 	img: Image = Image.open('P/1.gif')

# 	return img


class Hieroglyph:
	""" Китайский иероглиф """

	def __init__(self, 
		symb: HierSymb, 
		*, image: Optional[Image.Image] = None
	):
		if not is_hieroglyph(symb):
			raise ValueError("Parameter 'symb' must be a hieroglyph")

		# Параметры
		self.symb: HierSymb = symb
		self.pinyin: Pinyin = pinyin.get(symb)
		self.image: Optional[Image.Image] = image
		# self.gif: Optional[GifImageFile] = None
		# self.traits: Optional[list[Image.Image | GifImageFile]] = None


	@classmethod
	def hieroglyphs_from_text(cls,
		text: str,
		*args, **kwargs
	) -> list['Hieroglyph']:
		""" Дать список Hieroglyph с изображениями из текста.
			Дополнительные аргументы использутся для get_hieroglyph_images.
			При большом количестве иероглифов работает быстрее, так как создаёт
				все изображения сразу """
		text: str = ''.join([s for s in text if is_hieroglyph(s)])
		images: iter = get_hieroglyph_images(text, *args, **kwargs)
		return [cls(h, image=im) for h, im in zip(text, images)]


	def get_image(self, *args, **kwargs) -> Image.Image:
		""" Получить изображение иероглифа """
		return self.image or get_hieroglyph_images(self.symb, *args, **kwargs)[0]


	def add_image(self, *args, **kwargs):
		""" Добавить или обновить изображение иероглифа и сохранить в переменной """
		self.image = get_hieroglyph_images(self.symb, *args, **kwargs)[0]


	def __repr__(self):
		symb = self.symb
		pinyin = self.pinyin
		image = self.image
		return 'Hieroglyph' f'({symb=}, {pinyin=}, {image=})'

	def __str__(self):
		return self.symb


def main():
	hier: Hieroglyph = Hieroglyph('家')
	hier.add_image(width=500)
	
	print(hier)
	hier.image.show()


if __name__ == '__main__':
	main()
