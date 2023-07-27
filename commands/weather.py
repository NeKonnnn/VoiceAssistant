
import requests
import subprocess
from bs4 import BeautifulSoup
import vosk
import pyaudio
import json

import voice


def weather_check(city):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    try:
        res = requests.get(
            f'https://www.google.com/search?q={city}&oq={city}&aqs=chrome.0.35i39l2j0l4j46j69i60.6128j1j7&sourceid=chrome&ie=UTF-8',
            headers=headers
        )
        res.raise_for_status()  

        soup = BeautifulSoup(res.text, 'html.parser')

        time = soup.select('#wob_dts')
        precipitation = soup.select('#wob_dc')
        weather = soup.select('#wob_tm')

        if time and precipitation and weather:  
            voice.speaker(f'''День недели и время: {time[0].getText().strip()}
            Информация об осадках: {precipitation[0].getText().strip()}
            Температура воздуха: {weather[0].getText().strip()}°''')
        else:
            voice.speaker("Не удалось получить данные о погоде.")
    except Exception as e:
        voice.speaker(f'Произошла ошибка при попытке запроса к ресурсу API. Ошибка: {e}')

def listen_to_city():
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

def get_city():
    voice.speaker("Пожалуйста, назовите город, для которого вы хотите узнать погоду.")
    city = listen_to_city()
    return city

def get_weather():
    city_input = get_city()
    weather_check(f'{city_input} погода')