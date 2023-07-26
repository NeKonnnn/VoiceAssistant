import os
import subprocess
import webbrowser
import sys
import requests
from bs4 import BeautifulSoup
import vosk
import pyaudio
import json

import voice
 
    
# def valheim():
#     #Указываем путь с игрой вальхейм
#     try:
#         subprocess.Popen(r'E:\Programms\steam\steamapps\common\Valheim\valheim.exe')
#     except:
#         voice.speaker('Путь к файлу не найден, проверьте, правильный ли он')
    
def steam():
    #Указываем путь до стим
    try:
        subprocess.Popen(r'E:\Programms\steam\steam.exe')
    except:
        voice.speaker('Путь к файлу не найден, проверьте, правильный ли он')
        
def browser():
    #Открывает браузер заданнный по уполчанию в системе с url указанным здесь
    webbrowser.open('https://google.com', new=2)
    
# def weather(city):
#     try:
#         params = {'q': city, 'units': 'metric', 'lang': 'ru', 'appid': '5cdc96c4ca5c7ee9fb82efc43f0d2799'}
#         response = requests.get(f'https://api.openweathermap.org/data/2.5/weather', params=params)
#         if not response:
#             raise Exception("API request failed")
#         w = response.json()
#         voice.speaker(f"В городе {city} сейчас {w['weather'][0]['description']}, температура {round(w['main']['temp'])} градусов")
#     except Exception as e:
#         voice.speaker('Произошла ошибка при попытке запроса к ресурсу API, проверь код')
#         print(e)
    
def offPc():
    os.system("shutdown /s /t 1")
    
def offBot():
    sys.exit()
    
def passive():
    pass