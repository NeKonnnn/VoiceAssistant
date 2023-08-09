from configurations.listen_to_task import listen_to_task
import voice
import webbrowser
from numbers1 import *

def text_to_number(text):
    # Разделяем текст на слова
    words = text.split()
    # Преобразуем каждое слово в его числовой эквивалент с использованием words_to_numbers
    numbers = [words_to_numbers.get(word, word) for word in words]
    # Объединяем числа, чтобы получить преобразованный текст
    return ' '.join(map(str, numbers))

def map_search():
    voice.speaker_silero("Что ищем, сэр?")  # Спрашиваем у пользователя местоположение
    task = listen_to_task()  # Слушаем ответ пользователя
    converted_task = text_to_number(task)  # Преобразуем текстовые числа в числовые

    if task:
        voice.speaker_silero("Ищу, сэр")
        webbrowser.open(f'https://google.com/maps/search/{converted_task}')
        voice.speaker_silero("Готово, сэр")
    else:
        voice.speaker_silero("Не удалось распознать местоположение. Попробуйте еще раз.")