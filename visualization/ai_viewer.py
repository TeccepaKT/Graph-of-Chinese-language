"""

Отображение графа с базой AI

"""

from typing import Optional, Any

import matplotlib
import numpy as np
import mplcursors
import matplotlib.font_manager as fm
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from chinese import Hieroglyph
from utils.paths import Paths
from work_with_bases.ai_base import ai_base
from visualization.ai_builder import ai_builder


max_vertices: int = 300  # Максимум отображаемых вершин
# Будет добавлено больше настроек


def init_fonts():
    """ Инициализация шрифтов """
    font_path: str = Paths.Fonts.vertex_annotations
    font_prop: fm.FontProperties = fm.FontProperties(fname=font_path)
    fm.fontManager.addfont(font_path)

    plt.rcParams['font.family'] = font_prop.get_name()  # Установка как стандартного
    plt.rcParams['axes.unicode_minus'] = False


def view_graph():
    """ Вывод целого графа
        При нажатии кнопкой мыши на вершину графа выводится информация о нём:
         HSK (уровень иероглифа) и описание для изучения """
    graph, nodes_coords, hieroglyphs = ai_builder.get_graph(max_vertices=max_vertices)

    # Создание графика, размещение вершин и проведение рёбер
    fig: plt.Figure = plt.figure()
    ax: 'plt.Axes3D' = fig.add_subplot(projection='3d')
    ax.set_proj_type('ortho')  # Отключение перспективы
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    xs, ys, zs = nodes_coords.T  # Вершины
    scatter = ax.scatter(xs, ys, zs, s=50, label='Hieroglyphs', rasterized=True)

    lines: list[np.ndarray] = [
        np.vstack((nodes_coords[u, :], nodes_coords[v, :]))
        for u in graph for v in graph[u] if u < v and graph[u][v] >= 0.93
    ]  # Линии; граф неориентированный
    line_collection: Line3DCollection = Line3DCollection(lines, rasterized=True)
    ax.add_collection(line_collection)

    # Интерактивное наведение и нажатия
    cursor: mplcursors.Cursor = mplcursors.cursor(scatter, hover=True)
    selected: Optional[mplcursors.Selection] = None  # Информация о наведении мыши
    last_press_data: dict[str, Any] = {'x': 0, 'y': 0}  # Информация о последнем нажатии

    @cursor.connect('add')
    def on_add(sel: mplcursors.Selection):
        """ Поведение при наведении на узел графа """
        nonlocal selected
        selected = sel

        id: int = selected.index
        text: str = hieroglyphs[id]

        selected.annotation.set_text(text)
        selected.annotation.set_fontsize(20)
        sel.annotation.set_wrap(True)
        selected.annotation.get_bbox_patch().set(fc='white', alpha=0.9)

    def on_click():
        """ Поведение при щелчке мыши """
        nonlocal selected
        if selected is None:
            return

        id: int = selected.index
        hier: Hieroglyph = hieroglyphs[id]

        data: dict = ai_base.read_json(hier)
        level: str = '{}–{}'.format(data['level']['value'][0] / 10, data['level']['value'][1] / 10)
        text: str = f'Иероглиф {hier} (HSK {level})\n\n' + data['level']['comment']

        selected.annotation.set_text(text)
        selected.annotation.set_fontsize(12)
        selected.annotation.get_bbox_patch().set(fc='white', alpha=0.9)

        fig.canvas.draw_idle()  # Перерисовка

    def on_press(event: 'matplotlib.backend_bases.MouseEvent'):
        """ Регистрация нажатия на кнопку мыши """
        nonlocal last_press_data
        last_press_data['x'] = event.x
        last_press_data['y'] = event.y

    def on_release(event: 'matplotlib.backend_bases.MouseEvent'):
        """ Регистрация отпускания кнопки мыши, регистрация клика """
        if event.x == last_press_data['x'] and event.y == last_press_data['y']:
            on_click()

    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('button_release_event', on_release)

    # Вывод
    plt.show()


init_fonts()
