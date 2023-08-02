import subprocess
import vosk
import voice
import pyaudio
import json
import re
from numbers1 import words_to_numbers

# def mute_volume():
#     subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\volume\volume.exe'])

# def set_volume_min(volume=25):
#     subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\volume\sound.exe', str(volume)])

# def set_volume_half(volume=50):
#     subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\volume\sound.exe', str(volume)])

# def set_volume_max(volume=100):
#     subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\volume\sound.exe', str(volume)])

def change_volume(volume):
    # Проверка на валидность ввода: должно быть число от 0 до 100
    if 0 <= volume <= 100:
        subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\volume\sound.exe', str(volume)])
    else:
        voice.speaker_silero("Уровень громкости должен быть числом от 0 до 100.")

def listen_to_volume():
    model = vosk.Model("model_small")
    rec = vosk.KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    while True:
        data = stream.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = rec.Result()
            res_dict = json.loads(res)
            if 'text' in res_dict:
                return res_dict['text']

def get_volume():
    voice.speaker_silero("Пожалуйста, назовите уровень громкости, который вы хотите установить.")
    try:
        volume = listen_to_volume()
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
            change_volume(volume)
        else:
            voice.speaker_silero("Уровень громкости должен быть числом от 0 до 100.")