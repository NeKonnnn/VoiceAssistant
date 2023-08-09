from configurations.listen_to_task import listen_to_task
import voice
import webbrowser
from numbers1 import words_to_numbers

def browser():
    #Открывает браузер заданнный по уполчанию в системе с url указанным здесь
    voice.speaker_silero('Готово, сэр')
    webbrowser.open('https://google.com', new=2)

def text_to_number(text):
    # Разделяем текст на слова
    words = text.split()
    # Преобразуем каждое слово в его числовой эквивалент с использованием words_to_numbers
    numbers = [words_to_numbers.get(word, word) for word in words]
    # Объединяем числа, чтобы получить преобразованный текст
    return ' '.join(map(str, numbers))

def web_search():
    voice.speaker_silero("Что ищем, сэр?")  # Спрашиваем у пользователя
    task = listen_to_task()  # Слушаем ответ пользователя
    converted_task = text_to_number(task)  # Преобразуем текстовые числа в числовые

    if task:
        voice.speaker_silero(f"Ищу {task} в интернете")
        webbrowser.open(f'https://www.google.com/search?q={converted_task}')
        voice.speaker_silero("Готово, сэр")
    else:
        voice.speaker_silero("Не удалось распознать запрос. Попробуйте еще раз.")