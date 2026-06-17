"""

Программа для добавления в базы иероглифов новые данные
Для справки запусктите с флагом --help

"""

import argparse
from typing import Any
from time import sleep

from loggers import ResearchLogger as Logger
from researcher import Researcher
from hieroglyph_frequency_lists.hier_dictionaries import subtlex_dictionary


modes: dict[str, str] = {
    'dicts': 'researching with downloaded dictionaries and vector bases',
    'ai': 'researching with ai'
}  # Режимы изучения с их описаниями в документации


def infinite_research(researcher: Researcher):
    """ Изучение иероглифов по списку """
    for i, hier in enumerate(subtlex_dictionary.get_frequency_list()):
        researcher.deep_research(hier)
        Logger.log(f'[_] Ended {hier} (№{i + 1}), go forward\n')
        sleep(0.01)


def main():
    """ Основная функция """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='A program for researching Chinese hieroglyphs. '
                    'It generates new words in the chosen research mode, '
                    'and then adds them to hieroglyph databases.',
        epilog='research modes:\n' + '\n'.join([
            f'  - {k} — {v}'
            for k, v in modes.items()
        ]),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-m', '--mode', type=str, required=True, choices=modes.keys(),
                        help='research mode')
    parser.add_argument('-s', '--silent', action='store_true',
                        help='silent mode')
    parser.add_argument('-S', '--safety', action='store_true',
                        help='safety mode — data will not be changed')
    args: Any = parser.parse_args()

    Logger.log('[*] Launch...')

    if args.silent:
        Logger.log('[i] Silent mode on')
    if args.safety:
        Logger.log('[i] Safety mode on')

    if args.mode == 'ai':
        from research_ai.hier_research import AIChatResearcher
        from research_ai.ai_requests.chats import DeepseekChat

        infinite_research(AIChatResearcher(DeepseekChat(), safety_mode=args.safety))

    elif args.mode == 'dicts':
        from research_dictionaries.hier_research import DictsResearcher

        infinite_research(DictsResearcher())


if __name__ == '__main__':
    main()
