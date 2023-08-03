import time
import vosk
import pyaudio
import threading
import torch
import json

class VoiceStopwatch:
    def __init__(self, model):
        self.start_time = None
        self.recognizer = vosk.Model("path_to_your_model")
        self.rec = vosk.KaldiRecognizer(self.recognizer, 16000)
        self.model = model

    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time is None:
            raise Exception("Секундомер не был запущен")
        elapsed_time = time.time() - self.start_time
        self.start_time = None
        speaker_silero(f"Прошло {elapsed_time} секунд")
        return elapsed_time

    def listen_for_commands(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()

        while True:
            data = stream.read(2000)
            if self.rec.AcceptWaveform(data):
                text = json.loads(self.rec.Result())['text']
                if "старт" in text and self.start_time is None:
                    self.start()
                    speaker_silero("Секундомер запущен")
                elif "стоп" in text and self.start_time is not None:
                    elapsed_time = self.stop()
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    return elapsed_time

if __name__ == "__main__":
    stopwatch = VoiceStopwatch(model)
    stopwatch.listen_for_commands()