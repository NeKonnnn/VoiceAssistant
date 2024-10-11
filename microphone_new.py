import json
import queue
import os
import sys
import numpy as np

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
from configurations.times import *
# from commands.timer import *         
import voice
import chatGPT

# from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score
from sklearn.linear_model import SGDClassifier

AMPLITUDE_THRESHOLD = 100  # Экспериментальное значение

triggered = False

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
    
def calculate_amplitude(data):
    samples = np.frombuffer(data, dtype=np.int16)
    amplitude = np.mean(np.abs(samples))
    return amplitude

def callback(indata, frames, time, status):
    '''Очередь с микрофона'''
    q.put(bytes(indata))

def recognize(data, vectorizer, clf):
    '''
    Анализ распознанной речи
    '''
    #Пропускаем все, если длина расспознанного текста меньше 7ми символов
    global triggered
    if len(data) < 7:
        return
    #-------------потом можно будет удалить------------------
    # Логика для записи распознанной команды в файл
    log_command_to_file(data)
    #--------------------------------------------------------

    #если нет фразы обращения к ассистенту, то отправляем запрос gpt
    trg = words.TRIGGERS.intersection(data.split())
    print(f"Триггеры: {trg}, данные: {data}")
    if not trg and not triggered:  # измените условие на это
        if not int(os.getenv("CHATGPT")):
            return
        voice.speaker_gtts(chatGPT.start_dialogue(data))
        return
    else:
        triggered = True  # устанавливаем triggered в True, когда триггерное слово сказано
        start_timeout()  # и запускаем таймер
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

#--------------------
# Функция предназначена для сбора датасета, для последующего обучения командам (модельки)
def log_command_to_file(command):
    log_file_path = "commands_log.txt"  # Вы можете указать другой путь или файл
    with open(log_file_path, "a", encoding="utf-8") as file:
        file.write(command + "\n")
#--------------------

def recognize_wheel():
    print("Функция recognize_wheel вызвана!") 
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

    # Ваши метки
    labels = list(words.data_set.values())

    # Разделение на обучающий и тестовый наборы
    X_train, X_test, y_train, y_test = train_test_split(vectors, labels, test_size=0.2, random_state=42)

    # Обучение SGDClassifier
    clf = SGDClassifier(loss='log_loss')
    clf.fit(X_train, y_train)

     # Оценка производительности модели
    print("Качество классификации:", clf.score(X_test, y_test))

    # постоянная прослушка микрофона
    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, device=device[0], dtype='int16',
                            channels=1, callback=callback):

        rec = vosk.KaldiRecognizer(model, samplerate)
        listen_for_command = False
        command_end_time = 0

        while True and int(os.getenv('MIC')):
            data = q.get()
            amplitude = calculate_amplitude(data)
            # временно убираем вывод амплитуды
            # print(f"Амплитуда: {amplitude}")  # Debugging line
            #if amplitude > AMPLITUDE_THRESHOLD:
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())['text']
                print(f'Я сказал: {data}')

                # Если обнаружено ключевое слово и не прослушивается команда
                if words.TRIGGERS.intersection(data.split()) and not listen_for_command:
                    # очищаем очередь
                    while not q.empty():
                        q.get()
                    # Начать прослушивание команды
                    listen_for_command = True
                    command_end_time = time.time() + 15  # Продолжать прослушивание в течение 15 секунд

                # Если прослушивается команда
                if listen_for_command:
                    # Если время прослушивания команды истекло
                    if time.time() > command_end_time:
                        listen_for_command = False
                    else:
                        # Распознать и выполнить команду
                        recognize(data, vectorizer, clf)

    print('Микрофон отключен')