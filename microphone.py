import json
import queue
import os
import sys

from sklearn.feature_extraction.text import CountVectorizer     # pip install scikit-learn
from sklearn.linear_model import LogisticRegression
import sounddevice as sd    #pip install sounddevice
import vosk                 #pip install vosk

#import кастомных (наших) либ
import words
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
from commands.pc_work.blinds_up import *
from commands.backlog import add_to_backlog
# from commands.timer import *         
import voice
import chatGPT

q = queue.Queue()

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

def callback(indata, frames, time, status):
    '''Очередь с микрофона'''
    q.put(bytes(indata))

def recognize(data, vectorizer, clf):
    '''
    Анализ распознанной речи
    '''
    #Пропускаем все, если длина расспознанного текста меньше 7ми символов
    if len(data) < 7:
        return
    #если нет фразы обращения к ассистенту, то отправляем запрос gpt
    trg = words.TRIGGERS.intersection(data.split())
    if not trg:
        if not int(os.getenv("CHATGPT")):
            return
        voice.speaker_gtts(chatGPT.start_dialogue(data))
        return
    #если была фраза обращения к ассистенту
    #удаляем из команды имя асистента
    data = data.split()
    filtered_data = [word for word in data if word not in words.TRIGGERS]
    data = ' '.join(filtered_data)

    #получаем вектор полученного текста
    #сравниваем с вариантами, получая наиболее подходящий ответ
    # Преобразование команды пользователя в числовой вектор
    user_command_vector = vectorizer.transform([data])

    # Предсказание вероятностей принадлежности к каждому классу
    predicted_probabilities = clf.predict_proba(user_command_vector)

    # Задание порога совпадения
    threshold = 0.2

    # Поиск наибольшей вероятности и выбор ответа, если он превышает порог
    max_probability = max(predicted_probabilities[0])
    print(max_probability)
    if max_probability >= threshold:
        answer = clf.classes_[predicted_probabilities[0].argmax()]
    else:
        voice.speaker_silero("Команда не распознана")
        return
    

    #получение имени функции из ответа из data_set
    func_name = answer.split()[0]
    
    #запуск функции из commands
    if func_name == "get_city":
        get_weather()  # вызываем новую функцию get_weather
    # elif func_name == "get_volume":  # добавьте это условие
    #     set_volume()  # вызовите функцию set_volume
    else:
    # озвучка ответа из модели data_set
        response = answer.replace(func_name, '').strip()
        if response:  # проверка, что response не пустая строка
            voice.speaker_silero(response)
        else:
            exec(func_name + '()')  # для всех остальных функций просто их выполняем

def recognize_wheel():
    #Приветствие пользователя при запуске
    voice.speaker_silero("Здравствуйте, сэр. Чем могу помочь?")
    print('Слушаем')
    '''
    Обучаем матрицу ИИ для распознавания команд ассистентом
    и постоянно слушаем микрофон
    '''

    # Обучение матрицы на data_set модели
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(list(words.data_set.keys()))

    clf = LogisticRegression()
    clf.fit(vectors, list(words.data_set.values()))

    # постоянная прослушка микрофона
    with sd.RawInputStream(samplerate=samplerate, blocksize = 16000, device=device[0], dtype='int16',
                            channels=1, callback=callback):

        rec = vosk.KaldiRecognizer(model, samplerate)
        while True and int(os.getenv('MIC')):
            data = q.get()
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())['text']
                recognize(data, vectorizer, clf)

    print('Микрофон отключен')