import os
from configurations.listen_to_task import *
import voice
from numbers1 import *

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

def text_to_number(text):
    # Разделяем текст на слова
    words = text.split()
    # Преобразуем каждое слово в его числовой эквивалент с использованием words_to_numbers
    numbers = [words_to_numbers.get(word, word) for word in words]
    # Объединяем числа, чтобы получить преобразованный текст
    return ' '.join(map(str, numbers))

def create_folder():
    voice.speaker_silero("Как назвать папку, сэр?")
    folder_name = text_to_number(listen_to_task())
    folder_path = os.path.join(desktop_path, folder_name)
    try:
        os.mkdir(folder_path)
        voice.speaker_silero("Готово, сэр")
    except FileExistsError:
        voice.speaker_silero("Папка с таким именем уже существует.")

def create_excel_file():
    voice.speaker_silero("Как назвать файл, сэр?")
    file_name = text_to_number(listen_to_task())
    file_path = os.path.join(desktop_path, f"{file_name}.xlsx")
    try:
        with open(file_path, "xb") as f:
            pass
        voice.speaker_silero("Готово, сэр")
    except FileExistsError:
        voice.speaker_silero("Excel файл с таким именем уже существует.")

def create_word_file():
    voice.speaker_silero("Как назвать файл, сэр?")
    file_name = text_to_number(listen_to_task())
    file_path = os.path.join(desktop_path, f"{file_name}.docx")
    try:
        with open(file_path, "xb") as f:
            pass
        voice.speaker_silero("Готово, сэр")
    except FileExistsError:
        voice.speaker_silero("Word файл с таким именем уже существует.")

def create_ppt_file():
    voice.speaker_silero("Как назвать файл, сэр?")
    file_name = text_to_number(listen_to_task())
    file_path = os.path.join(desktop_path, f"{file_name}.pptx")
    try:
        with open(file_path, "xb") as f:
            pass
        voice.speaker_silero("Готово, сэр")
    except FileExistsError:
        voice.speaker_silero("PowerPoint файл с таким именем уже существует.")

def create_txt_file():
    voice.speaker_silero("Как назвать файл, сэр?")
    file_name = text_to_number(listen_to_task())
    file_path = os.path.join(desktop_path, f"{file_name}.txt")
    try:
        with open(file_path, "x") as f:
            pass
        voice.speaker_silero("Готово, сэр")
    except FileExistsError:
        voice.speaker_silero("Текстовый файл с таким именем уже существует.")