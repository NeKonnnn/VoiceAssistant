import queue
import json

import sounddevice as sd
import vosk


#import ML библиотек
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

#import наших модулей
import words
from commands.main_commands import *
from commands.weather import *

# Создаем объект очереди
q = queue.Queue()
model = vosk.Model('model_small')
# Устанавливаем устройство по умолчанию. Здесь 0 - это входное устройство, а 4 - выходное устройство
device = sd.default.device = 0, 4
# Запрашиваем частоту дискретизации входного устройства
samplerate = int(sd.query_devices(device, 'input')['default_samplerate'])

# Определяем функцию обратного вызова. Эта функция вызывается, когда доступны новые аудиоданные
# Аудиоданные помещаются в очередь для дальнейшей обработки
def callback(indata, frames, time, status):
    q.put(bytes(indata))
    
def recognize(data, vectorizer, clf):
    trg = words.TRIGGERS.intersection(data.split())
    if not trg:
        return
    
    data.replace(list(trg)[0], '')
    text_vector = vectorizer.transform([data]).toarray()[0]
    answer = clf.predict([text_vector])[0]
    
    func_name = answer.split()[0]
    voice.speaker(answer.replace(func_name, ''))
    if func_name == "get_city":
        get_weather()  # вызываем новую функцию get_weather
    else:
        exec(func_name + '()')  # для всех остальных функций просто их выполняем
    
def main():
    #Приветствие пользователя при запуске
    voice.speaker("Здравствуйте, сэр. Чем могу помочь?")
    
    #Обучение матрицы на data_set модели
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(list(words.data_set.keys()))
    
    clf = LogisticRegression()
    clf.fit(vectors, list(words.data_set.values()))

    del words.data_set
    
    # Начинаем запись с указанными настройками
    with sd.RawInputStream(samplerate=samplerate, blocksize = 16000, device=device[0],
                        dtype="int16", channels=1, callback=callback):

        # Инициализируем объект KaldiRecognizer
        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            # Получаем данные из очереди
            data = q.get()
            # Если распознаватель принимает форму волны, обрабатываем ее
            if rec.AcceptWaveform(data):
                # Декодируем результат, чтобы получить текст, преобразованный из речи в текст
                data = json.loads(rec.Result())['text']
                recognize(data, vectorizer, clf)

if __name__ == '__main__':
    main()