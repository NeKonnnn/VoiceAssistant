import os
import datetime
import winsound
import threading
from num2words import num2words
import voice
from configurations.listen_to_task import listen_to_task
import re
from numbers1 import words_to_numbers

def number_to_text(n):
    return num2words(n, lang='ru')

ALARM_THREAD = None

class AlarmThread(threading.Thread):
    def __init__(self, hour, minute):
        super().__init__()
        self.hour = hour
        self.minute = minute
        self._stop_event = threading.Event()

    def run(self):
        count = 0
        alarm_time = datetime.datetime.now().replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
        # Формируем путь к файлу alarm.wav относительно текущей директории
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        alarm_sound_path = os.path.join(parent_dir, 'icons', 'alarm.wav')
        
        while not self._stop_event.is_set():
            if datetime.datetime.now() >= alarm_time:
                if count < 5:
                    print('Будильник сработал!')
                    winsound.PlaySound(alarm_sound_path, winsound.SND_LOOP)
                    count += 1
                else:
                    break

    def stop(self):
        self._stop_event.set()

def alarm():
    global ALARM_THREAD
    try:
        voice.speaker_silero("На какое время установить будильник, сэр?")
        time_text = listen_to_task().replace("на ", "")  # Remove preposition "на"
        print(f"Ответ на вопрос о времени: {time_text}")
        
        # Convert words to numbers
        words_list = time_text.split()
        numbers_list = [words_to_numbers[word] if word in words_to_numbers else word for word in words_list]
        time_text_numbers = " ".join(map(str, numbers_list))
        
        # Use regex to find numbers and words "hour" and "minute" in various forms
        matches = re.findall(r'\d+|час[ова]?|минут[уы]?', time_text_numbers)
        
        alarm_hour = None
        alarm_minute = None
        
        for match in matches:
            if match.isdigit():
                if alarm_hour is None:
                    alarm_hour = int(match)
                else:
                    alarm_minute = int(match)
            elif "час" in match:
                alarm_hour = words_to_numbers[num2words(1)]
            elif "минут" in match:
                alarm_minute = words_to_numbers[num2words(1)]
        
        if alarm_hour is None or alarm_minute is None:
            raise ValueError("Неверный формат времени")

        # Ask for the day of the week
        voice.speaker_silero("На какой день недели установить будильник?")
        day_text = listen_to_task().replace("на ", "").lower()  # Remove preposition "на"
        print(f"Ответ на вопрос о дне недели: {day_text}")

        days_of_week = {
            "понедельник": 0,
            "понедельника": 0,
            "вторник": 1,
            "вторника": 1,
            "среда": 2,
            "среду": 2,
            "четверг": 3,
            "четверга": 3,
            "пятница": 4,
            "пятницу": 4,
            "суббота": 5,
            "субботу": 5,
            "воскресенье": 6,
            "воскресенья": 6
        }
        
        current_time = datetime.datetime.now()
        if day_text == "сегодня":
            alarm_date = current_time.date()
        elif day_text in days_of_week:
            today = current_time.date()
            days_until_alarm = (days_of_week[day_text] - today.weekday() + 7) % 7
            alarm_date = today + datetime.timedelta(days=days_until_alarm)
        else:
            raise ValueError("Неверный формат дня")
        
        alarm_time = datetime.datetime.combine(alarm_date, datetime.time(hour=alarm_hour, minute=alarm_minute))
        
        if alarm_time < current_time:
            alarm_time += datetime.timedelta(days=1)
        
        hours, remainder = divmod((alarm_time - current_time).seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        print(f"Указанное время: {number_to_text(alarm_hour)} часов {number_to_text(alarm_minute)} минут.")
        voice.speaker_silero(f"Будильник установлен на {number_to_text(alarm_hour)} часов {number_to_text(alarm_minute)} минут. До срабатывания будильника осталось {number_to_text(hours)} часов и {number_to_text(minutes)} минут.")
        
        ALARM_THREAD = AlarmThread(alarm_hour, alarm_minute)
        ALARM_THREAD.start()
        
    except ValueError:
        voice.speaker_silero("Извините, я не могу понять указанное время или день. Пожалуйста, попробуйте еще раз.")
    except Exception as e:
        voice.speaker_silero(f"Произошла ошибка: {str(e)}. Пожалуйста, попробуйте еще раз.")

def stop_alarm():
    global ALARM_THREAD
    if ALARM_THREAD:
        ALARM_THREAD.stop()
        ALARM_THREAD = None
        winsound.PlaySound(None, winsound.SND_ASYNC)
        voice.speaker_silero("Будильник остановлен.")

def cancel_alarm():
    global ALARM_THREAD
    if ALARM_THREAD:
        ALARM_THREAD.stop()
        ALARM_THREAD = None
        voice.speaker_silero("Будильник отменен.")
