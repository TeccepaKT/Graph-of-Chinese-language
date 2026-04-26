import os
import subprocess

from time import sleep
from threading import Thread as th


class Browser:
	_process: subprocess.CompletedProcess  # Процесс браузера 
	# _window_id: int  # Id окна браузера


	def __init__(self):
		raise RuntimeError('Используйте мета-функции для создания объекта')


	def __new__(self):
		raise RuntimeError('Используйте мета-функции для создания объекта')


	@staticmethod
	def __new_browser_process(*args) -> subprocess.CompletedProcess:
		""" Открытие браузера с заданными аргументами
			Возвращает созданный процесс """
		cmds = (
			# For X11 on Wayland: 'XDG_SESSION_TYPE=x11' or 'GDK_BADKEND=x11'
			# For new window: '--new-window'

			('google-chrome-stable', *args),  # Linux
			('google-chrome', *args),  # Linux
			('start', 'chrome', *args),  # Win
			('open', '-n', '-a', 'Google Chrome', '--args', *args)  # Mac
		)
		
		for cmd in cmds:
			try:
				process = subprocess.Popen(cmd,
					stdout=subprocess.DEVNULL,
					stderr=subprocess.DEVNULL)  # Перенаправление кучи вывода
				break
			except Exception as e:
				print(e)
				continue

		else:
			raise SystemError('Не удалось открыть Chrome.')

		return process


	@classmethod
	def open_new(cls,
		url: str = 'https://www.google.com',
		size: tuple[int, int] = (1200, 700),
		pos: tuple[int, int] = (0, 0)
	) -> 'Browser':
		""" Создать окно браузера """
		obj = super().__new__(cls)

		size = f'--window-size={size[0]},{size[1]}' #'--start-fullscreen' #'--window-size=1200,800'
		pos = f'--window-position={pos[0]},{pos[1]}'
		obj._process = Browser.__new_browser_process(size, pos, url)
		
		return obj


	def close(self):
		self._process.terminate()


	# def hide():
	#	subprocess.run(['xdotool', 'windowminimize', window_id])



'''
def get_window_id_by_process_id(pid: int) -> Optional[int]:
	""" Получить id окна по id соотв. процесса
		Если ничего не найдено, возвращает None """

	# print(subprocess.run(
	# 	['xdotool', 'search', '--pid', str(pid)],
	# 	capture_output=True,
	# 	text=True,
	# 	check=True
	# ).stdout)
	# exit()  # Лучше искать по имени

	#### try...
	processes = subprocess.run(
		['xdotool_gdfgdfgfdffsdfsd', 'search', '--pid', str(pid)],
		capture_output=True,
		text=True,
		check=True
	)
	out = processes.stdout.strip().splitlines()

	if not out:
		return None
	return out[0]
'''


def main():
	b = Browser.open_new()
	sleep(1)
	b.close()


if __name__ == '__main__':
	main()
