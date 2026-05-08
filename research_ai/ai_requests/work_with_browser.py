"""

Работа с браузером

"""

from __future__ import annotations
from typing import TypeAlias

import subprocess


Process: TypeAlias = subprocess.Popen[bytes]


class Browser:
    """ Работа с окном браузера """
    _process: Process  # PID браузера

    def __new__(cls):
        raise RuntimeError('Use class methods to create an instance')

    @staticmethod
    def __new_browser_process(*args):
        """ Открытие браузера с заданными аргументами
            Возвращает созданный процесс """
        cmds: list[tuple[str, ...]] = [
            # For X11 on Wayland: 'XDG_SESSION_TYPE=x11' or 'GDK_BADKEND=x11'
            # For new window: '--new-window'

            ('google-chrome-stable', *args),  # Linux
            ('google-chrome', *args),  # Linux
            ('start', 'chrome', *args),  # Win
            ('open', '-n', '-a', 'Google Chrome', '--args', *args)  # Mac
        ]

        for cmd in cmds:
            try:
                process: Process = subprocess.Popen(cmd,
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
    def open_new(cls, url: str = 'https://www.google.com',
                 size: tuple[int, int] = (1200, 700), pos: tuple[int, int] = (0, 0)) -> Browser:
        """ Создать окно браузера """
        obj = super().__new__(cls)

        size_arg: str = f'--window-size={size[0]},{size[1]}'
        pos_arg: str = f'--window-position={pos[0]},{pos[1]}'
        obj._process = Browser.__new_browser_process(size_arg, pos_arg, url)

        return obj

    def close(self):
        """ Закрыть окно браузера """
        self._process.terminate()
