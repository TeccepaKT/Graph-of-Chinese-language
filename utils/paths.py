"""

Пути к ресурсам проекта

"""

from pathlib import Path

class Paths:
    """ Пути """
    bcc_dictionary: Path = Path('hieroglyph_frequency_lists/lists/BCC/global_wordfreq.release.txt')  # Словарь BCC
    subtlex_dictionary: Path = Path('hieroglyph_frequency_lists/lists/SUBTLEX-CH/SUBTLEX-CH-CHR')  # Словарь SUBTLEX-CH
    prompt_file: Path = Path('research_ai/Prompt.txt')  # Prompt для генерации файлов
    format_file: Path = Path('research_ai/Format.txt')  # Формат генерируемых файлов
    research_logger_output: Path = Path('research_ai/ai_requests/logger_output.log')

    class Fonts:
        """ Пути к шрифтам """
        vertex_annotations: Path = Path('assets/fonts/NotoSansCJK-Regular.ttc')

    class Base:
        """ Относительные пути для базы иероглифов """
        path_to_saves: str = 'save_raw'
        validate_format_file: str = '.valid_format.json'
