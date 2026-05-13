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
    'dicts': 'researching with downloaded dictionaries '
             'and vector bases',
    'ai_browser': 'researching with ai via browser',
    'ai_api': 'researching with ai via api'
}  # Режимы изучения с их описаниями в документации


def infinite_research(researcher: Researcher):
    """ Изучение иероглифов по списку """
    for i, hier in enumerate(subtlex_dictionary.get_frequency_list()):
        researcher.deep_research(hier)
        Logger.log(f'Ended {hier} (№{i + 1}), go forward\n', type=Logger.MessageType.UNDERSCORE)
        sleep(0.01)


def main():
    """ Основная функция """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='A program for collecting information about Chinese hieroglyphs. '
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

    Logger.log('Launch...', type=Logger.MessageType.STAR)

    if args.silent:
        Logger.log('Silent mode on', type=Logger.MessageType.I)
    if args.safety:
        Logger.log('Safety mode on', type=Logger.MessageType.I)

    if args.mode == 'ai_browser':
        from research_ai.hier_research import AIChatResearcher
        from research_ai.ai_requests.deepseek_chat import DeepseekChat

        chat = DeepseekChat()
        chat.load()
        infinite_research(AIChatResearcher(chat, safety_mode=args.safety))

    if args.mode == 'ai_api':
        from research_ai.hier_research import AIChatResearcher
        from research_ai.ai_requests.api_chat import APIChat

        infinite_research(AIChatResearcher(APIChat(), safety_mode=args.safety))

    elif args.mode == 'dicts':
        from research_dictionaries.hier_research import DictsResearcher

        infinite_research(DictsResearcher())


if __name__ == '__main__':
    main()
