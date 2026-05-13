"""

Запросы к AI Deepseek через вкладку браузера
Открывает браузер и двигает мышью для получения ответов

Требования:
    Сессия X11 или дополнительный флаг для Wayland

"""

from typing import TypeAlias, Optional, Callable, Any
from time import time, sleep
from functools import wraps
from collections import deque

import pyautogui as pag
import pyperclip
from PIL.Image import Image
from PIL.ImageGrab import grab

from chinese.pyclr import RGB, hex_to_rgb, rgb_diff
from loggers import AIDebugLogger as Logger
from utils.functions import random_num
from research_ai.ai_requests.chat import AIChat
from research_ai.ai_requests.mouse_control import Mouse
from research_ai.ai_requests.keyboard_control import hotkey, write
from research_ai.ai_requests.work_with_browser import Browser


Coords: TypeAlias = tuple[int, int]
Box: TypeAlias = tuple[Coords, Coords]


pag.PAUSE = 0  # Без задержки


def trying(delay: float, timeout: float, timeout_message: str):
    """ Декоратор для создания функции, повторяющейся, пока не
        будет использовано yield <answer> или пройдёт timeout """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start: float = time()

            while time() - start < timeout:
                yielded: list[Any] = list(func(*args, **kwargs))

                if yielded:
                    return yielded[0]
                sleep(delay)

            else:
                raise TimeoutError(timeout_message)

        return wrapper

    return decorator


class DeepseekBrowserTab:
    """ Работа с вкладкой DeepSeek в браузере """

    # Параметры окна
    _window_size = (1200, 800)  # Размер открываемого браузера
    _window_pos = (10, 10)  # Левый верхний угол
    _frame = (16, 16, 16, 32)  # (пкс.) Рамка, которую нужно обрезать при скриншоте браузера

    # Поля
    _loaded: bool = False
    _start_input_widget_box: Box  # Координаты виджета ввода текста (относительно окна)
    _browser: Browser  # Управление браузером

    @staticmethod
    def if_loaded(func: Callable):
        """ Декоратор для всех функций, требующих полной загрузки браузера """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._loaded:
                raise ValueError('Чат не был загружен')
            return func(self, *args, **kwargs)

        return wrapper

    @Logger.logging(importance=1)
    def load(self):
        """ Открытие чата, если он ещё не был открыт
            Load - так как загружается сайт """
        if self._loaded:
            return

        # Открытие сайта
        self._browser = Browser.open_new(
            url='https://chat.deepseek.com/',
            size=self._window_size, pos=self._window_pos
        )  # No noexcept
        sleep(1)

        self._wait_preload()  # No noexcept
        sleep(0.5)

        self._wait_and_update_input_widget_box()  # No noexcept
        self._loaded = True

    @Logger.logging()
    @trying(delay=0.2, timeout=10, timeout_message='Не удалось загрузить сайт или он не опознан')
    def _wait_preload(self):
        """ Ожидание загрузки сайта chat.deepseek.com
            Условие ожидания: недостаточно пикселей определенного цвета """
        deepseek_bg_clr: RGB = hex_to_rgb('151517')

        img = self._shot_browser()
        if img is None:
            Logger.log('Ожидание загрузки сайта: не удалось получить снимок экрана')
            return

        # Просмотр пикселей
        pix: 'PixelAccess' = img.load()
        step: int = 2  # Шаг в изображении при обработке

        good_pix: int = 0  # Нужных пикселей среди проверенных
        total_pix: int = 0  # Всего проверено пикселей

        for y in range(0, img.size[1], step):
            for x in range(0, img.size[0], step):
                if pix[x, y] == deepseek_bg_clr:
                    good_pix += 1
                total_pix += 1

        # Выход
        coef: float = good_pix / total_pix
        
        if 0.6 < coef:
            sleep(0.3)
            yield  # Достаточно пикселей: выход из @trying

        Logger.log(f'Ожидание загрузки сайта: недостаточно ожидаемых пикселей ({round(coef * 100, 1)}%)')

    def _shot_browser(self) -> Optional[Image]:
        """ Получить изображение браузера (он должен быть не передвинут)
            Если не удалось, возвращает None
            Noexcept """
        try:
            img: Image = grab(tuple(
                self._window_pos[i] + rb * self._window_size[i]  # Положение браузера
                - (2 * rb - 1) * self._frame[2 * rb + i]  # Рамки
                for rb in range(2) for i in range(2)
            )).convert('RGB')

            if img.size[0] == 0 or img.size[1] == 0:
                Logger.log('Попытка получить изображение браузера: получено некорректное изображение')
                return None

            return img

        except Exception as e:
            Logger.log(f'Попытка получить изображение браузера: ошибка ({e})')
            return None

    @Logger.logging()
    @trying(delay=0.2, timeout=10, timeout_message="Не удалось обновить поле ввода текста")
    def _wait_and_update_input_widget_box(self):
        """ Обновление информации о позиции поля ввода текста """
        input_widget_box = self._get_input_widget_box()
        if input_widget_box is None:
            return
        
        self._start_input_widget_box = input_widget_box
        yield  # Выйти из цикла @trying

    def _get_input_widget_box(self) -> Optional[Box]:
        """ Найти виджет в формате Box
            Если не найдено, возвращает None
            Noexcept """
        step: int = 2  # Разреженность поиска
        min_area_at_screen: float = 0.04  # Минимальное покрытие экрана поля ввода

        img = self._shot_browser()
        if img is None:
            return None

        # Поиск пикселей
        input_widget_clr = hex_to_rgb('2c2c2e')  # Это цвет поля ввода И сообщений
        input_widget_boxes: list[Box] = []  # Нахождение Box всех объектов, похожих на поле

        pix: 'PixelAccess' = img.load()
        been: set[Coords] = set()  # Однажды обработанные пиксели

        for y in range(0, img.size[1], step):
            for x in range(0, img.size[0], step):
                if (x, y) in been:
                    continue
                clr: RGB = pix[x, y]

                if clr == input_widget_clr:
                    # BFS
                    pixels: set[Coords] = set()
                    adds: set[Coords] = {(x, y)}
                    next_adds: set[Coords] = set()
                    neighbours: list[Coords] = [(step, 0), (0, step), (-step, 0), (0, -step)]

                    while adds:  # BFS добавление
                        for px, py in adds:
                            for add_x, add_y in neighbours:
                                nx: int = px + add_x
                                ny: int = py + add_y
                                pos: Coords = (nx, ny)

                                if nx < 0 or nx >= img.size[0] or ny < 0 or ny >= img.size[1]:
                                    continue  # Не на изображении
                                if pix[nx, ny] != input_widget_clr:
                                    continue  # Не тот цвет
                                if pos in pixels or pos in adds:
                                    continue  # Уже известная позиция
                                next_adds.add(pos)

                        # Добавление слоя в pixels
                        for pos in adds:
                            pixels.add(pos)
                            been.add(pos)
                        adds = next_adds
                        next_adds = set()

                    # Всё добавлено в pixels
                    if (len(pixels) * step**2) / (img.size[0] * img.size[1]) < min_area_at_screen:
                        for px, py in pixels:
                            pix[px, py] = (200, 150, 0)
                        continue  # Слишком мало пикселей

                    # Запоминание поля
                    xs, ys = zip(*pixels)

                    left_border: int = min(xs)  # Левая координата
                    right_border: int = max(xs)  # Правая координата
                    top_border: int = min(ys)  # Верхняя координата (перевёрнуто)
                    bottom_border: int = max(ys)  # Нижняя координата

                    width: int = right_border - left_border + (step - 1)  # Ширина виджета
                    height: int = abs(top_border - bottom_border) + (step - 1)  # Высота виджета

                    # Проверка корректности
                    if width == 0 or height == 0 or \
                       len([t for t in pixels if t[1] == top_border]) * step \
                            / width < 0.8 or \
                       len([t for t in pixels if t[1] == bottom_border]) * step \
                            / width < 0.8 or \
                       len([t for t in pixels if t[0] == left_border]) * step \
                            / height < 0.55 or \
                       len([t for t in pixels if t[0] == right_border]) * step \
                            / height < 0.55:  # Проверка, что область похожа
                                              # на прямоугольник: левые и др. границы содержат много пикселей
                        Logger.log('Очередной объект не похож на прямоугольное поле')
                        
                        for px, py in pixels:
                            pix[px, py] = (200, 150, 0)
                        continue

                    for px, py in pixels:
                        pix[px, py] = (255, 255, 0)
                    input_widget_boxes.append(((left_border, top_border),
                                               (right_border, bottom_border)))  # Добавление поля

        if len(input_widget_boxes) == 0:
            Logger.log('Попытка нахождения виджета ввода текста: не найдено ни одного поля')
            return None

        Logger.log(f'Все найденные поля: {input_widget_boxes}')
        return input_widget_boxes[-1]  # Возвращается последнее найденное поле, т.к. поле ввода самое нижнее


    @Logger.logging()
    def _wait_answer(self):
        """ Ожидать, пока генерируется ответ
            Условие ожидания: есть изменяющиеся пиксели на экране и не найдено copy_button """
        delay: float = 0.15  # Ожидание перед созданием нового изображения
        max_count: int = 24  # (Изображения начинают сравниваться только по достижении этого количества)

        sleep(2)
        start_img = self._shot_browser()  # Окно с ответом не должно совпадать с этим
        Logger.log('Создано начальное изображение')
        
        sleep(1)
        Logger.log('Поиск виджета ввода текста для просмотра определенной части экрана')
        Logger.add_depth()
        input_widget_box: Box = self._get_input_widget_box()  # Просмотрим пиксели до начала поля ввода (поле сдвигается
                                                              # после первого запроса, поэтому его координаты
                                                              # нужно обновить)
        if input_widget_box is None:
            input_widget_box = (
                (self._start_input_widget_box[0][0], round(0.8 * start_img.size[1])),
                (self._start_input_widget_box[1][0], round(0.95 * start_img.size[1]))
            )  # Приблизительные значения в случае неудачи
            Logger.log('Так как виджет найти не удалось, просматривается какая-то часть экрана')

        Logger.reduce_depth()

        # Обрезание изображений
        crop: tuple[int, int, int, int] = (
            self._start_input_widget_box[0][0],
            round(0.25 * start_img.size[1]),
            self._start_input_widget_box[1][0],
            input_widget_box[0][1]
        )
        start_img: Image = start_img.crop(crop)

        # Ожидание совпадения изображений с экрана
        Logger.log('Начало проверок условия выхода')
        images: deque[Image] = deque(maxlen=max_count)  # Изображения
            # Для завершения ожидания должны совпать все изображения в очереди

        cycled: int = 0
        while True:
            img: Image = self._shot_browser()
            if img is None:
                sleep(delay)
                continue

            img: Image = img.crop(crop)

            images.append(img)
            cycled = (cycled + 1) % max_count

            if images[-1] == start_img:  # Пока что изображения такие же, как начальное
                Logger.log('Содержимое экрана не изменялось')
                sleep(6)
                continue

            if cycled == 0 and len(images) == max_count:
                # mouse_imitate()  # Также могла не появиться кнопка копирования

                for i in range(max_count-1, -1, -1):
                    if images[i] != images[i - 1]:
                        Logger.log('Ожидание ответа: содержимое экрана ещё меняется')
                        break

                else:  # Изображения совпали
                    Logger.log('Содержимое экрана больше не меняется')
                    break

            sleep(delay)

        # Ожидание появления кнопки копирования
        Logger.log('Ожидание появления кнопки копирования')
        while self._get_copy_button_pos() is None:
            sleep(delay)

        Logger.log('Получено, проверки пройдены')


    @Logger.logging()
    def _get_generated_response(self) -> str:
        """ Дать ответ после его генерации (копирование и вставка) """
        pos = self._get_copy_button_pos()
        if pos is None:
            raise ValueError('Получение ответа: не удалось найти кнопку копирования ответа')

        Mouse.moveTo(pos, slanting=1)
        sleep(random_num(0.1, 0.15))
        Mouse.click()
        sleep(1.6)  # Скопированный текст не сразу становится доступен
        
        return pyperclip.paste()

    def _get_copy_button_pos(self) -> Optional[tuple[int, int]]:
        """ Найти кнопку копирования ответа по цвету (во время генерации
             может найтись "многоточие") """
        borders_x: tuple[float, float] = (0, 0.15)  # Границы поиска по x относительно виджета ввода текста
        borders_y: tuple[float, float] = (0.5, 0.9)  # Границы поиска по y относительно окна браузера

        # Поиск по цвету
        copy_widget_clr: RGB = hex_to_rgb('adb2b8')
        copy_widget_pixels: list[Coords] = []

        img: Image = self._shot_browser()
        pix: 'PixelAccess' = img.load()
        for y in range(round(borders_y[0] * img.size[1]), 
                       round(borders_y[1] * img.size[1])):  # Не нужно делать step

            width: int = self._start_input_widget_box[1][0] - self._start_input_widget_box[0][0]
            for x in range(round(borders_x[0] * width),
                           round(borders_x[1] * width)):
                x += self._start_input_widget_box[0][0]

                if rgb_diff(pix[x, y], copy_widget_clr) <= 3:
                    pix[x, y] = (255, 0, 0)
                    copy_widget_pixels.append((x, y))
                else:
                    pix[x, y] = (110, 0, 0)

        if not copy_widget_pixels:
            Logger.log('Попытка найти кнопку копирования текста: не найдено')
            return None

        # Координаты лево-правого найденного пикселя
        pos: Coords = list(min(copy_widget_pixels, key=lambda t: t[0] - t[1]))
        for i in range(2):
            pos[i] += self._window_pos[i] + self._frame[i]  # Настоящие координаты

        return pos

    @if_loaded
    @Logger.logging()
    def close(self):
        """ Закрыть чат """
        self._browser.close()
        del self._start_input_widget_box
        del self._browser
        self._loaded = False


class DeepseekChat(AIChat, DeepseekBrowserTab):
    """ Chat с DeepSeek V4 """

    @DeepseekBrowserTab.if_loaded
    @Logger.logging(importance=1)
    def get_response(self, text: str) -> str:
        pyperclip.copy('')  # Копирование пустого ответа на всякий случай, чтобы если полученный
                            # ответ не скопировался, то не вставился бы полученный ранее. (Ответы ИИ копируются,
                            # как ответ возвращается скопированное)
        if text == '':
            return ''

        # Активация поля ввода
        Logger.log('Нажатие на поле ввода')
        input_widget_box = self._get_input_widget_box()
        if input_widget_box is None:
            Logger.log('Так как не найдено поле ввода, возвращается пустой ответ')
            return ''
        
        Mouse.moveTo((
            (input_widget_box[0][0] + input_widget_box[1][0]) // 2,
            (input_widget_box[0][1] + input_widget_box[1][1]) // 2
        ), slanting=15)
        sleep(random_num(0.05, 0.1))
        Mouse.click()
        sleep(0.1)

        # Отправление запроса
        Logger.log('Печать запроса')
        write(text)  # Печать текста (поле ввода должно быть/стать активно)
        hotkey('enter')  # Отправить
        
        # Ожидание ответа
        self._wait_answer()

        res: str = self._get_generated_response()
        return res

    @DeepseekBrowserTab.if_loaded
    @Logger.logging(importance=1)
    def reload(self):
        """ Перезагрузить чат """
        self.close()
        self.load()


def main():
    """ Тестирование чата """
    chat = DeepseekChat()
    chat.load()

    answer: str = chat.get_response('Hi!')
    print('Received response:', repr(answer))

    chat.close()


if __name__ == '__main__':
    main()
