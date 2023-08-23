import os
import subprocess
import webbrowser
import sys
import requests
from bs4 import BeautifulSoup

import voice

def open_valheim():
    #Указываем путь с игрой вальхейм
    try:
        subprocess.Popen([r'E:\Programms\steam\steamapps\common\Valheim\valheim.exe'])
    except Exception as e:
        voice.speaker_silero('Не удалось открыть вальхейм. Проверьте, правильный ли путь к файлу.')
        print(f"Error: {e}")  # Вывод ошибки в консоль для отладки
    else:
        voice.speaker_silero('Запустила, наслаждайтесь игрой.')   
    
def open_steam():
    try:
        subprocess.Popen(r'E:\Programms\steam\steam.exe')
    except Exception as e:
        voice.speaker_silero('Не удалось открыть стим. Проверьте, правильный ли путь к файлу.')
        print(f"Error: {e}")  # Вывод ошибки в консоль для отладки
    else:
        voice.speaker_silero('стим открыт.')
    
# def weather(city):
#     try:
#         params = {'q': city, 'units': 'metric', 'lang': 'ru', 'appid': '5cdc96c4ca5c7ee9fb82efc43f0d2799'}
#         response = requests.get(f'https://api.openweathermap.org/data/2.5/weather', params=params)
#         if not response:
#             raise Exception("API request failed")
#         w = response.json()
#         voice.speaker_silero_selero(f"В городе {city} сейчас {w['weather'][0]['description']}, температура {round(w['main']['temp'])} градусов")
#     except Exception as e:
#         voice.speaker_silero_selero('Произошла ошибка при попытке запроса к ресурсу API, проверь код')
#         print(e)
    
def offPc():
    voice.speaker_silero('выполняю, сэр')
    os.system("shutdown /s /t 1")
    
def offBot():
    voice.speaker_silero('до скорой встречи, сэр')
    sys.exit()
    
def passive():
    pass