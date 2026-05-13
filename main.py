"""

Основная программа для визуализации графа

## P.S. Зайдите в документацию visualization.ai_viewer.shpw_graph
## P.P.S. Это тестовый вариант программы

"""

import argparse
from typing import Any


modes: dict[str, str] = {
    'ai': 'use ai base to build graph'
}  # Режимы отображения графа с их описаниями в документации


def main():
    """ Основная функция """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='A program for creating a graph of hieroglyphs.',
        epilog='modes:\n' + '\n'.join([
            f'  - {k} — {v}'
            for k, v in modes.items()
        ]),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-m', '--mode', type=str, default='ai', choices=modes.keys(),
                        help='mode')
    args: Any = parser.parse_args()

    print(' [*] Launch...')

    if args.mode == 'ai':
        from visualization.ai_viewer import view_graph

        view_graph()


if __name__ == '__main__':
    main()
