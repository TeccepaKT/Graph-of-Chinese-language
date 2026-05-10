"""

Запросы к AI по API через ollama

"""

from typing import Generator

import ollama

from loggers import AIDebugLogger as Logger
from research_ai.ai_requests.chat import AIChat


class APIChat(AIChat):
    """ Получение ответов через API """
    _model: str = 'qwen3.5'  # Модель, к которой поступают запросы

    def __init__(self):
        """ Скачивание модели, если её нет """
        try:
            ollama.show(self._model)

        except ollama.ResponseError:
            print('Downloading the model...')
            ollama.pull(self._model)

    def get_response(self, text: str) -> str:
        """ Получить ответ по API """
        Logger.log('Запуск ollama.generate')
        stream: Generator[ollama.GenerateResponse] = ollama.generate(model=self._model, prompt=text)

        Logger.log('Генерация ответа')
        ret: str = ''
        for chunk in stream:
            ret += chunk['response']

        Logger.log('Возврат ответа')
        return ret


def main():
    """ Тестирование чата """
    chat = APIChat()

    answer: str = chat.get_response('Hi!')
    print('Received response:', repr(answer))


if __name__ == '__main__':
    main()
