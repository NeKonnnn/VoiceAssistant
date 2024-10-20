import time
import vosk
import pyaudio
import threading
import torch
import voice
import json

class VoiceTimer:
    def __init__(self, model):
        self.start_time = None
        self.recognizer = vosk.Model("path_to_your_model")
        self.rec = vosk.KaldiRecognizer(self.recognizer, 16000)
        self.model = model

    def ask_duration(self):
        voice.speaker_silero("На сколько секунд вы хотите установить таймер?")

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
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()

        while True:
            data = stream.read(2000)
            if self.rec.AcceptWaveform(data):
                text = json.loads(self.rec.Result())['text']
                if text.isdigit():
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    return int(text)

    def listen_for_stop(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()

        while True:
            data = stream.read(2000)
            if self.rec.AcceptWaveform(data):
                text = json.loads(self.rec.Result())['text']
                if "стоп" in text:
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    return self.stop()

if __name__ == "__main__":
    timer = VoiceTimer(model)
    timer.ask_duration()
    duration = timer.listen_for_duration()
    timer.start(duration)
    timer.listen_for_stop()