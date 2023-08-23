import time
import threading
from configurations.listen_to_task import listen_to_task
import voice
from num2words import num2words
from numbers1 import *

class VoiceStopwatch:
    def __init__(self):
        self.start_time = None
        self.is_paused = False
        self.paused_time = None

    def start(self):
        self.start_time = time.time()
        self.stopwatch_thread = threading.Thread(target=self._stopwatch_thread)
        self.stopwatch_thread.start()

    def _stopwatch_thread(self):
        while True:
            if self.is_paused:
                time.sleep(1)
                continue
            time.sleep(1)

    def pause(self):
        if self.start_time is None:
            raise Exception("Секундомер не был запущен")
        self.is_paused = True
        self.paused_time = time.time()
        voice.speaker_silero("Поставила секундомер на паузу")
    
    
    def resume(self):
        if self.start_time is None:
            raise Exception("Секундомер не был запущен")
        if not self.is_paused:
            raise Exception("Секундомер не был на паузе")
        self.is_paused = False
        self.total_paused_time += time.time() - self.paused_time
        self.paused_time = None
        voice.speaker_silero("Секундомер возобновлен")

    def stop(self):
        if self.start_time is None:
            raise Exception("Секундомер не был запущен")
        elapsed_time = int(time.time() - self.start_time)  # round is used here
        self.start_time = None
        elapsed_time_in_words = seconds_to_words(elapsed_time)
        voice.speaker_silero(f"Секундомер остановлен. Прошло {elapsed_time_in_words}")
        return elapsed_time
    
    def stop(self):
        if self.start_time is None:
            raise Exception("Секундомер не был запущен")
        elapsed_time = (time.time() - self.start_time)
        self.start_time = None
        elapsed_time_in_words = seconds_to_words(elapsed_time)
        voice.speaker_silero(f"Секундомер остановлен. Прошло {elapsed_time_in_words}")
        return elapsed_time

def start_stopwatch():
    global stopwatch
    stopwatch = VoiceStopwatch()
    stopwatch.start()
    voice.speaker_silero("Секундомер активирован, сэр")

def pause_stopwatch():
    if stopwatch is not None:
        stopwatch.pause()
    else:
        voice.speaker_silero("Секундомер еще не был запущен.")

def resume_stopwatch():
    if stopwatch is not None:
        stopwatch.resume()
    else:
        voice.speaker_silero("Секундомер еще не был запущен.")

def stop_stopwatch():
    if stopwatch is not None:
        stopwatch.stop()
    else:
        voice.speaker_silero("Секундомер еще не был запущен.")

def seconds_to_words(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    result = ""
    if hours > 0:
        result += num2words(hours, lang='ru') + " " + pluralize(hours, ["час", "часа", "часов"]) + " "
    if minutes > 0 and hours == 0: # добавляем минуты, только если нет часов
        result += num2words(minutes, lang='ru') + " " + pluralize(minutes, ["минута", "минуты", "минут"]) + " "
    if seconds > 0 and minutes == 0 and hours == 0: # добавляем секунды, только если нет минут и часов
        result += num2words(seconds, lang='ru') + " " + pluralize(seconds, ["секунда", "секунды", "секунд"])
    return result.strip()