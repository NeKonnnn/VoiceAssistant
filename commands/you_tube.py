from configurations.listen_to_task import listen_to_task
import voice
import webbrowser
from numbers1 import *
from pywhatkit import playonyt
import keyboard
import re
from selenium import webdriver
from selenium.webdriver.common.by import By

# Глобальная переменная для хранения последнего поискового запроса
last_search_query = ""

def youtube():
    global last_search_query
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
    global last_search_query
    voice.speaker_silero("Что ищем, сэр?")  # Спрашиваем у пользователя
    task = listen_to_task()  # Слушаем ответ пользователя
    converted_task = text_to_number(task)  # Преобразуем текстовые числа в числовые

    if task:
        voice.speaker_silero("Ищу, сэр")
        webbrowser.open(f'https://www.youtube.com/results?search_query={converted_task}')
        voice.speaker_silero("Готово, сэр")
        # Сохраняем запрос для последующего использования
        last_search_query = converted_task
    else:
        voice.speaker_silero("Не удалось распознать запрос. Попробуйте еще раз.")

def open_video():
    voice.speaker_silero('Как пожелаете, сэр')
    playonyt(last_search_query)
    
def pause_video():
    voice.speaker_silero('Как пожелаете, сэр')
    keyboard.send('k')

def play_video():
    voice.speaker_silero('Как пожелаете, сэр')
    keyboard.send('k')
    
def rewind_5_seconds_back():
    voice.speaker_silero('Перематываю на 5 секунд назад')
    keyboard.send('left')

def rewind_5_seconds_forward():
    voice.speaker_silero('Перематываю на 5 секунд вперёд')
    keyboard.send('right')

def rewind_10_seconds_back():
    voice.speaker_silero('Перематываю на 10 секунд назад')
    keyboard.send('j')

def rewind_10_seconds_forward():
    voice.speaker_silero('Перематываю на 10 секунд вперёд')
    keyboard.send('l')

def previous_frame():
    voice.speaker_silero('Перехожу к предыдущему кадру')
    keyboard.send(',')

def next_frame():
    voice.speaker_silero('Перехожу к следующему кадру')
    keyboard.send('.')

def shift_p_previous_video():
    voice.speaker_silero('Перехожу к предыдущему видео')
    keyboard.send('shift+p')

def shift_n_next_video():
    voice.speaker_silero('Перехожу к следующему видео')
    keyboard.send('shift+n')

def decrease_playback_speed():
    voice.speaker_silero('Уменьшаю скорость воспроизведения')
    keyboard.send('shift+,')

def increase_playback_speed():
    voice.speaker_silero('Увеличиваю скорость воспроизведения')
    keyboard.send('shift+.')
    
###
def subtitles_on():
    voice.speaker_silero('Включаю субтитры')
    keyboard.send('c')
    
def subtitles_off():
    voice.speaker_silero('Отключаю субтитры')
    keyboard.send('c')
    
def change_font_size_plus():
    voice.speaker_silero('Увеличиваю размер шрифта')
    keyboard.send('+')
    
def change_font_size_minus():
    voice.speaker_silero('Уменьшаю размер шрифта')
    keyboard.send('-')


def fullscreen_on():
    voice.speaker_silero('Включаю полноэкранный режим')
    keyboard.send('f')
    
def fullscreen_off():
    voice.speaker_silero('Выключаю полноэкранный режим')
    keyboard.send('f')

def mini_player_on():
    voice.speaker_silero('Включаю мини-проигрыватель')
    keyboard.send('i')

def mini_player_off():
    voice.speaker_silero('Выключаю мини-проигрыватель')
    keyboard.send('i')

def mute_on():
    voice.speaker_silero('Включаю звук')
    keyboard.send('m')

def mute_off():
    voice.speaker_silero('Выключаю звук')
    keyboard.send('m')

def resize_player_window_increase():
    voice.speaker_silero('Увеличиваю окно проигрывателя')
    keyboard.send('t')

def resize_player_window_decrease():
    voice.speaker_silero('Уменьшаю окно проигрывателя')
    keyboard.send('t')

def adjust_volume_increase():
    voice.speaker_silero('Увеличиваю громкость на 5%')
    keyboard.send('up')

def adjust_volume_decrease():
    voice.speaker_silero('Уменьшаю громкость на 5%')
    keyboard.send('down')

def zoom_in():
    voice.speaker_silero('Приближаю')
    keyboard.send(']')

def zoom_out():
    voice.speaker_silero('Отдаляю')
    keyboard.send('[')
        
def close_player_or_dialog():
    voice.speaker_silero('Закрываю окно проигрывателя или текущее диалоговое окно')
    keyboard.send('esc')
    
def move_up():
    voice.speaker_silero('Передвигаю вверх')
    keyboard.send('w')

def move_left():
    voice.speaker_silero('Передвигаю влево')
    keyboard.send('a')

def move_down():
    voice.speaker_silero('Передвигаю вниз')
    keyboard.send('s')

def move_right():
    voice.speaker_silero('Передвигаю вправо')
    keyboard.send('d')    
###

def scaled_percent_value(percent):
    # Масштабируем проценты на диапазон от 1 до 9
    scaled_value = round(percent / 10)
    return min(max(scaled_value, 1), 9)

def jump_to_percent():
    # Создаем обратный словарь для преобразования числа в слово
    numbers_to_words = {v: k for k, v in words_to_numbers.items()}
    
    # Спрашиваем у пользователя желаемый процент перемотки
    voice.speaker_silero("На сколько вы хотите перемотать видео?")
    time_text = listen_to_task().replace("на ", "")
    
    # Извлекаем процент из ответа пользователя
    match = re.search(r'(\w+) процентов', time_text)
    if match:
        word = match.group(1)
        percent = words_to_numbers.get(word, None)
        
        if percent:
            # Получаем масштабированное значение процента
            scaled_percent = scaled_percent_value(percent)
            
            # Переходим к желаемому проценту
            keyboard.send(str(scaled_percent))
            word_percent = numbers_to_words.get(percent)
            voice.speaker_silero(f'Перематываю на {word_percent} процентов')
        else:
            voice.speaker_silero('Извините, я не могу понять ваш запрос.')
    else:
        voice.speaker_silero('Некорректный процент')