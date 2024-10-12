import os

from gtts import gTTS
from io import BytesIO
import torch
import sounddevice as sd
import soundfile as sf
import time
import microphone_new

from voice_assistant_gui.settings_manager import get_selected_voice

def speaker_gtts(text):
    # Отключаем микрофон перед ответом
    microphone_new.is_listening = False
    print("Микрофон отключен на время ответа")

    lang = os.getenv('LANG')
    with BytesIO() as f:
        gTTS(text=text, lang=lang, slow=False).write_to_fp(f)
        f.seek(0)
        data, fs = sf.read(f)
        sd.play(data, fs, blocking=True)

    # Включаем микрофон после завершения ответа
    microphone_new.is_listening = True
    print("Микрофон снова включен")

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
put_accent = True
put_yo = True

# Добавляем параметр для передачи голоса, который нужно использовать
def speaker_silero(text, speaker=None):
    try:
        # Отключаем микрофон перед ответом
        microphone_new.is_listening = False
        print("Микрофон отключен на время ответа")

        # Если голос не передан, используем голос по умолчанию из настроек
        if not speaker:
            speaker = get_selected_voice()

        audio = model_ru.apply_tts(text=text,
                                   speaker=speaker,
                                   sample_rate=sample_rate,
                                   put_accent=put_accent,
                                   put_yo=put_yo)

        # Воспроизведение
        sd.play(audio, sample_rate * 1.05)
        time.sleep((len(audio) / sample_rate) + 0.5)
        sd.stop()

        # Включаем микрофон после завершения ответа
        microphone_new.is_listening = True
        print("Микрофон снова включен")
    except ValueError:
        raise
    
    

# speaker_silero('привет')
