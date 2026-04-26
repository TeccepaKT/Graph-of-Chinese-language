from time import sleep

import pyautogui as pag
import pyperclip


def hotkey(*keys):
	pag.hotkey(*keys)


def write(text):
	""" Вписать текст """
	original = pyperclip.paste()
	pyperclip.copy(text)
	hotkey('ctrl', 'v')
	sleep(0.05)
	pyperclip.copy(original)
