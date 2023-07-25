import os
import webbrowser
import sys
import requests
import subprocess

import voice
 

def browser():
    #Открывает браузер заданнный по уполчанию в системе с url указанным здесь
    webbrowser.open('https://google.com', new=2)
 
 
    
def valheim():
    #Указываем путь с игрой вальхейм
    try:
        subprocess.Popen('E:\Programms\steam\steamapps\common\Valheim\valheim.exe')
    except:
        voice.speaker('Путь к файлу не найден, проверьте, правильный ли он')
    
def steam():
    #Указываем путь до стим
    try:
        subprocess.Popen('E:\Programms\steam\steam.exe')
    except:
        voice.speaker('Путь к файлу не найден, проверьте, правильный ли он')
    
def weather():
    #Для работы этого кода нужно зарегистрироваться на сайте
    #https://openweathermap.org или переделать на ваше усмотрение под что-то другое'''
    try:
        params = {'q': 'Moscow', 'units': 'metric', 'lang': 'ru', 'appid': '8a5b41c0119f14b24f6f95942cecbbbf'}
        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather', params=params)
        if not response:
            raise
        w = response.json()
        speaker(f"На улице {w['weather'][0]['description']} {round(w['main']['temp'])} градусов")
    except:
        voice.speaker('Произошла ошибка при попытке запроса к ресурсу API, проверь код')
    
def offpc():
    #Эта команда отключает ПК под управлением Windows
    os.system('shutdown \s')
    
def offBot():
    sys.exit()
    
def passive():
    pass