import json
import queue
import os
import sys
import numpy as np
import torch
import pickle
import re
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

from sklearn.feature_extraction.text import CountVectorizer     # pip install scikit-learn
# from sklearn.linear_model import LogisticRegression
import sounddevice as sd    #pip install sounddevice
import vosk                 #pip install vosk

#import кастомных (наших) либ
import words
import configuration
from commands.alarm import *
from commands.you_tube import *
from commands.pc_work.creaters import *
from commands.map_search import *
from commands.totime.stopwatch import *
from commands.totime.timer import *
from commands.totime.time_check import tell_time
from commands.main_commands import *
from commands.weather import *
from commands.pc_work.volume import * 
from commands.pc_work.sleep_lock import *
from commands.pc_work.clipboard import clipboard
from commands.pc_work.swap import swap_language
from commands.pc_work.screen import screenshot
from commands.pc_work.trash import clear_trash
from commands.pc_work.task_manager import task_manager
from commands.pc_work.windows import *
from commands.backlog import add_to_backlog
from commands.internet_search import *
from commands.command_executor import execute_command
from voice_assistant_gui.settings_manager import get_all_commands, load_amplitude_threshold
from configurations.times import *
# from commands.timer import *         
import voice
import chatGPT

# from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score
from sklearn.linear_model import SGDClassifier

AMPLITUDE_THRESHOLD = 100  # Экспериментальное значение
SIMILARITY_THRESHOLD = 0.7  # Порог для косинусного сходства

triggered = False
q = queue.Queue()
is_listening = True

model = vosk.Model('model_small')        #голосовую модель vosk нужно поместить в папку с файлами проекта
                                        #https://alphacephei.com/vosk/
                                        #https://alphacephei.com/vosk/models
try:
    device = sd.default.device  # <--- по умолчанию
                                #или -> sd.default.device = 1, 3 или python -m sounddevice просмотр 
    samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])  #получаем частоту микрофона
except:
    voice.speaker_silero('Включи микрофон!')
    sys.exit(1)

# Загрузка предобученной модели, токенизатора и классификатора
with open("model/model.pkl", "rb") as f:
    tokenizer, bert_model, clf = pickle.load(f)

def preprocess_text(text):
    """Предобработка текста для модели."""
    text = text.lower()  # Приведение к нижнему регистру
    text = re.sub(r'[^а-яё\s]', '', text)  # Удаление всех символов, кроме русских букв и пробелов
    text = re.sub(r'\s+', ' ', text).strip()  # Удаление лишних пробелов
    return text

def encode_text(text):
    """Получение эмбеддинга текста с использованием RuBERT."""
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = bert_model(**inputs)
        sentence_embedding = outputs.pooler_output.squeeze().numpy()
    return sentence_embedding
    
def calculate_amplitude(data):
    samples = np.frombuffer(data, dtype=np.int16)
    amplitude = np.mean(np.abs(samples))
    return amplitude

def callback(indata, frames, time, status):
    '''Очередь с микрофона'''
    if is_listening:  # Микрофон активен
        q.put(bytes(indata))

def get_most_similar_command(input_text, known_commands):
    """Возвращает наиболее похожую команду на основе косинусного сходства."""
    input_vector = encode_text(preprocess_text(input_text)).reshape(1, -1)
    known_vectors = [encode_text(preprocess_text(cmd)).reshape(1, -1) for cmd in known_commands]
    similarities = [cosine_similarity(input_vector, vec)[0][0] for vec in known_vectors]
    most_similar_idx = np.argmax(similarities)
    most_similar_command = known_commands[most_similar_idx]
    return most_similar_command, similarities[most_similar_idx]

def recognize(data):
    """
    Анализ распознанной речи и выполнение команды.
    """
    global triggered
    print(f"Распознанная команда: {data}")  # Логирование команды
    
    # Пропускаем все, если длина распознанного текста меньше 7 символов
    if len(data) < 7:
        print("Команда слишком короткая, пропускаем.")
        return

    # Логика для записи распознанной команды в файл
    log_command_to_file(data)

    # Проверяем триггерные слова
    trg = words.TRIGGERS.intersection(data.split())
    print(f"Триггеры: {trg}")

    # Если триггерное слово не обнаружено и ChatGPT отключен, пропускаем
    if not trg and not triggered:
        if not int(os.getenv("CHATGPT")):
            print("Триггер не обнаружен и ChatGPT отключен, пропускаем.")
            return
        voice.speaker_gtts(chatGPT.start_dialogue(data))
        return
    else:
        triggered = True
        start_timeout()

    # Удаляем триггерные слова из команды
    data = preprocess_text(data)
    data = ' '.join([word for word in data.split() if word not in words.TRIGGERS])
    print(f"Команда после удаления триггеров: {data}")

    # Получаем все сохраненные команды
    all_commands = get_all_commands()
    print(f"Доступные команды: {all_commands}")

    # Проверяем, если команда соответствует какой-то из сохраненных команд
    for command in all_commands:
        if command in data:
            print(f"Команда распознана как: {command}")
            execute_command(command)
            return

    # Если команда не найдена, продолжаем предсказание через модель
    command_vector = encode_text(data).reshape(1, -1)
    predicted_label = clf.predict(command_vector)[0]

    # Выполнение команды
    func_name = predicted_label.split()[0]
    print(f"Распознана команда: {func_name}")
    
    if func_name == "get_city":
        get_weather()  # вызываем функцию get_weather для получения погоды
    else:
        response = predicted_label.replace(func_name, '').strip()
        if response:
            voice.speaker_silero(response)
        else:
            exec(func_name + '()')

#--------------------
# Функция предназначена для сбора датасета, для последующего обучения командам (модельки)
def log_command_to_file(command):
    log_file_path = "commands_log.txt"  # Вы можете указать другой путь или файл
    with open(log_file_path, "a", encoding="utf-8") as file:
        file.write(command + "\n")
#--------------------

def recognize_wheel():
    print("Функция recognize_wheel вызвана!") 
    voice.speaker_silero("Здравствуйте, сэр. Чем могу помочь?")
    print('Слушаем')

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device[0], dtype='int16',
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        listen_for_command = False
        command_end_time = 0

        while True and int(os.getenv('MIC')):
            data = q.get()
            amplitude = calculate_amplitude(data)
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())['text']
                print(f'Я сказал: {data}')

                if words.TRIGGERS.intersection(data.split()) and not listen_for_command:
                    while not q.empty():
                        q.get()
                    listen_for_command = True
                    command_end_time = time.time() + 15

                if listen_for_command:
                    if time.time() > command_end_time:
                        listen_for_command = False
                    else:
                        recognize(data)

    print('Микрофон отключен')