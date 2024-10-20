import requests
from bs4 import BeautifulSoup
from configurations.listen_to_task import listen_to_task
from num2words import num2words
import re

import voice

def time_to_words(time_string):
    """
    Преобразует строку времени в слова на русском языке.
    Ожидается формат 'часы:минуты'.
    """
    try:
        hours, minutes = map(int, time_string.split(':'))
        hours_in_words = num2words(hours, lang='ru')
        minutes_in_words = num2words(minutes, lang='ru')
        return f"{hours_in_words} часов {minutes_in_words} минут"
    except ValueError:
        # Если время не в формате 'часы:минуты', возвращаем исходную строку
        return time_string

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

        time_info = soup.select('#wob_dts')  # Извлечение времени и даты
        precipitation = soup.select('#wob_dc')  # Извлечение информации об осадках
        weather = soup.select('#wob_tm')  # Извлечение температуры

        if time_info and precipitation and weather:  
            # Получаем время и преобразуем его
            time_text = time_info[0].getText().strip()
            # Попробуем извлечь только время (формат 'часы:минуты'), если есть
            time_match = re.search(r'(\d{1,2}:\d{2})', time_text)
            if time_match:
                time_in_words = time_to_words(time_match.group(1))  # Преобразуем время в слова
            else:
                time_in_words = time_text  # Если формат не 'часы:минуты', используем исходный текст

            # Получаем температуру и преобразуем её в слова
            temperature = weather[0].getText().strip()
            temperature_number = re.findall(r'\d+', temperature)
            if temperature_number:
                temperature_word = num2words(int(temperature_number[0]), lang='ru')
            else:
                temperature_word = temperature

            # Озвучиваем результат
            voice.speaker_silero(f'''День недели и время: {time_in_words}
            Информация об осадках: {precipitation[0].getText().strip()}
            Температура воздуха: {temperature_word} градусов''')
        else:
            voice.speaker_silero("Не удалось получить данные о погоде.")
    except Exception as e:
        voice.speaker_silero(f'Произошла ошибка при попытке запроса к ресурсу API. Ошибка: {e}')

def get_city():
    voice.speaker_silero("Пожалуйста, назовите город, для которого вы хотите узнать погоду.")
    city = listen_to_task()
    return city

def get_weather():
    city_input = get_city()
    weather_check(f'{city_input} погода')   
    