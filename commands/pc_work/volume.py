import subprocess
import voice
from configurations.listen_to_task import listen_to_task
from numbers1 import words_to_numbers

def mute_volume():
    voice.speaker_silero("Выключаю звук, сэр")
    subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\volume\volume.exe'])

# def set_volume_min(volume=25):
#     subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\volume\sound.exe', str(volume)])

# def set_volume_half(volume=50):
#     subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\volume\sound.exe', str(volume)])

# def set_volume_max(volume=100):
#     subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\volume\sound.exe', str(volume)])

def change_volume(volume, volume_in_words):
    # Проверка на валидность ввода: должно быть число от 0 до 100
    if 0 <= volume <= 100:
        subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\volume\sound.exe', str(volume)])
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