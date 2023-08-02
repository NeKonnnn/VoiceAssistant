import vosk
import pyaudio
import json

def listen_to_task():
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