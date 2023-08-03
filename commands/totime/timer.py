import time
import threading
from configurations.listen_to_task import listen_to_task
import voice
from num2words import num2words

class VoiceTimer:
    def __init__(self, model):
        self.start_time = None
        self.model = model

    def ask_duration(self):
        voice.speaker_silero("На сколько активируем таймер?")

    def start(self, duration):
        self.start_time = time.time()
        self.end_time = self.start_time + duration
        self.timer_thread = threading.Thread(target=self._timer_thread)
        self.timer_thread.start()

    def _timer_thread(self):
        while time.time() < self.end_time:
            time.sleep(1)
        voice.speaker_silero("Таймер закончился")

    def stop(self):
        if self.start_time is None:
            raise Exception("Таймер не был запущен")
        elapsed_time = time.time() - self.start_time
        self.start_time = None
        return elapsed_time

    def listen_for_duration(self):
        while True:
            text = listen_to_task()
            total_seconds = 0

            time_units = {
                'секунд': 1,
                'минут': 60,
                'час': 3600,
            }

            for unit, multiplier in time_units.items():
                if unit in text:
                    number_words, _ = text.split(unit, 1)
                    number = words_to_numbers(number_words.strip())
                    total_seconds += number * multiplier

            if total_seconds > 0:
                return total_seconds

    def listen_for_stop(self):
        while True:
            text = listen_to_task()
            if "стоп" in text:
                return self.stop()

def start_timer():
    timer = VoiceTimer(model)
    timer.ask_duration()
    duration = timer.listen_for_duration()
    timer.start(duration)
    duration_in_words = seconds_to_words(duration)
    voice.speaker_silero(f"Запустила таймер на {duration_in_words}")

def seconds_to_words(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    result = ""
    if hours > 0:
        result += num2words(hours, lang='ru') + " часов "
    if minutes > 0:
        result += num2words(minutes, lang='ru') + " минут "
    if seconds > 0:
        result += num2words(seconds, lang='ru') + " секунд"
    return result.strip()

def pause_timer():
    if timer is not None:
        timer.pause()
    else:
        voice.speaker_silero("Таймер еще не был запущен.")

def resume_timer():
    if timer is not None:
        timer.resume()
    else:
        voice.speaker_silero("Таймер еще не был запущен.")

def stop_timer():
    if timer is not None:
        timer.stop()
    else:
        voice.speaker_silero("Таймер еще не был запущен.")

def start_timer():
    global timer
    timer = VoiceTimer(model)
    timer.ask_duration()
    duration = timer.listen_for_duration()
    timer.start(duration)
    duration_in_words = seconds_to_words(duration)
    voice.speaker_silero(f"Запустила таймер на {duration_in_words}")
    timer.listen_for_stop()