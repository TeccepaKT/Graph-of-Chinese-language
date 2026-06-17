"""

Управление мышью

"""

from random import randint

import pyautogui as pag
import pyHM


class Mouse:
    """ Имитация движений мыши, чтобы не выйти в спящий режим и обновлялась кнопка копирования """

    @staticmethod
    def moveTo(pos: tuple[int, int], slanting: int = 3):
        """ Движения мыши на координаты """
        pyHM.mouse.move(pos[0] + randint(-slanting, slanting), pos[1] + randint(-slanting, slanting))

    @staticmethod
    def move(pos: tuple[int, int], slanting: int = 3):
        """ Сдвиг мыши на вектор """
        cx, cy = pyHM.mouse.get_current_position()
        Mouse.moveTo((cx + pos[0], cy + pos[1]), slanting)

    @staticmethod
    def click():
        """ Нажатие кнопки мыши """
        pag.click()