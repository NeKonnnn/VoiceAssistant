from configurations.listen_to_task import listen_to_task
import voice
import webbrowser
from numbers1 import *
from pywhatkit import playonyt

def youtube():
    voice.speaker_silero('Да, сэр')
    webbrowser.open('https://www.youtube.com/', new=2)

def text_to_number(text):
    # Разделяем текст на слова
    words = text.split()
    # Преобразуем каждое слово в его числовой эквивалент с использованием words_to_numbers
    numbers = [words_to_numbers.get(word, word) for word in words]
    # Объединяем числа, чтобы получить преобразованный текст
    return ' '.join(map(str, numbers))

def youtube_search():
    voice.speaker_silero("Что ищем, сэр?")  # Спрашиваем у пользователя
    task = listen_to_task()  # Слушаем ответ пользователя
    converted_task = text_to_number(task)  # Преобразуем текстовые числа в числовые

    if task:
        voice.speaker_silero("Ищу, сэр")
        webbrowser.open(f'https://www.youtube.com/results?search_query={converted_task}')
        voice.speaker_silero("Готово, сэр")
    else:
        voice.speaker_silero("Не удалось распознать запрос. Попробуйте еще раз.")

def open_video():
    voice.speaker_silero('Как пожелаете, сэр')
    playonyt(topic=None)