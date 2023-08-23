import os

from gtts import gTTS
from io import BytesIO
import torch
import sounddevice as sd
import soundfile as sf
import time


def speaker_gtts(text):
    lang = os.getenv('LANG')
    with BytesIO() as f:
        gTTS(text=text, lang=lang, slow=False).write_to_fp(f)
        f.seek(0)
        data, fs = sf.read(f)
        sd.play(data, fs, blocking=True)


models_urls = ['https://models.silero.ai/models/tts/en/v3_en.pt',
               'https://models.silero.ai/models/tts/ru/v3_1_ru.pt']

model_ru = 'silero_models/ru/model.pt'
model_en = 'silero_models/en/model.pt'

device = torch.device('cpu')
torch.set_num_threads(4)

# Загрузка русской модели
local_file_ru = model_ru

if not os.path.isfile(local_file_ru):
    torch.hub.download_url_to_file(models_urls[1], local_file_ru)  

model_ru = torch.package.PackageImporter(local_file_ru).load_pickle("tts_models", "model")
model_ru.to(device)

# Загрузка английской модели
local_file_en = model_en

if not os.path.isfile(local_file_en):
    torch.hub.download_url_to_file(models_urls[0], local_file_en)  

model_en = torch.package.PackageImporter(local_file_en).load_pickle("tts_models", "model")
model_en.to(device)

sample_rate = 48000
speaker='baya'   #aidar, baya, kseniya, xenia, eugene
en_speaker = 'en_6' # от 0 до 117
put_accent = True
put_yo = True

def speaker_silero(text):
    try:
        audio = model_ru.apply_tts(text=text,
                                    speaker=speaker,
                                    sample_rate=sample_rate,
                                    put_accent=put_accent,
                                    put_yo=put_yo)

        # sd.play(audio, blocking=True)
        sd.play(audio, sample_rate * 1.05)
        time.sleep((len(audio) / sample_rate) + 0.5)
        sd.stop()
    except ValueError:
        raise
    
    

# speaker_silero('привет')
