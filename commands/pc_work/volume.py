import os
import subprocess
import voice
from configurations.listen_to_task import listen_to_task
from numbers1 import words_to_numbers

def get_executable_path(exe_name, subdir=''):
    # Получаем путь к текущей директории
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # Это директория на уровень выше

    # Если указана поддиректория, включаем её в путь
    if subdir:
        exe_path = os.path.join(parent_dir, subdir, exe_name)
    else:
        exe_path = os.path.join(parent_dir, exe_name)

    # Проверка, существует ли файл
    if not os.path.exists(exe_path):
        print(f"Файл {exe_name} не найден по пути: {exe_path}")
        return None

    return exe_path

def mute_volume():
    voice.speaker_silero("Выключаю звук, сэр")
    exe_path = get_executable_path('volume.exe', 'exe/volume')
    if exe_path:
        subprocess.run([exe_path])

# def set_volume_min(volume=25):
#     exe_path = get_executable_path('sound.exe', 'exe/volume')
#     if exe_path:
#         subprocess.run([exe_path, str(volume)])

# def set_volume_half(volume=50):
#     exe_path = get_executable_path('sound.exe', 'exe/volume')
#     if exe_path:
#         subprocess.run([exe_path, str(volume)])

# def set_volume_max(volume=100):
#     exe_path = get_executable_path('sound.exe', 'exe/volume')
#     if exe_path:
#         subprocess.run([exe_path, str(volume)])

def change_volume(volume, volume_in_words):
    # Проверка на валидность ввода: должно быть число от 0 до 100
    if 0 <= volume <= 100:
        exe_path = get_executable_path('sound.exe', 'exe/volume')
        if exe_path:
            subprocess.run([exe_path, str(volume)])
            voice.speaker_silero(f"Изменила уровень громкости на {volume_in_words}, сэр.")
    else:
        voice.speaker_silero("Уровень громкости должен быть числом от 0 до 100.")

def get_volume():
    voice.speaker_silero("Пожалуйста, назовите уровень громкости, который вы хотите установить.")
    try:
        volume = listen_to_task()
        if volume == "":
            voice.speaker_silero("Модель не слышит вас. Пожалуйста, говорите громче или проверьте ваш микрофон.")
            return None
        return volume
    except Exception as e:
        voice.speaker_silero(f"Произошла ошибка при распознавании вашей речи: {str(e)}")
        return None

def set_volume():
    volume_input = get_volume()
    if volume_input is not None:
        # Используйте словарь для замены слов на числа
        volume_input = volume_input.split()
        volume_numbers = [words_to_numbers[word] if word in words_to_numbers else 0 for word in volume_input]
        
        # Складываем числа вместе, чтобы получить итоговый объем
        volume = sum(volume_numbers)

        # Проверяем, что объем находится в допустимом диапазоне
        if 0 <= volume <= 100:
            change_volume(volume, volume_input)  # Передаем текстовое представление уровня громкости
        else:
            voice.speaker_silero("Уровень громкости должен быть числом от 0 до 100.")
