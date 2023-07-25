import pyttsx3

#Инициализация голосового движка при запуске программы
engine = pyttsx3.init()
engine.setProperty('rate', 180) #скорость речи

def speaker(text):
    '''Озвучка текста'''
    engine.say(text)
    engine.runAndWait()