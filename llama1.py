import os
from llama_cpp import Llama
import subprocess
import string
import logging
from langchain_community.llms import LlamaCpp

# Начальное системное сообщение
system_message = "Ты дружелюбный и полезный ассистент. Отвечай только на русском языке, кратко и по делу."

# Путь к файлу модели GGUF
model_path = ".local_model_cache/llama-3.1-8b-instruct.Q8_0.gguf"

# # Параметры модели
# n_gpu_layers = 0  # Установите 1 или более, если используете GPU
# n_ctx = 2048 # Контекстное окно
# max_tokens = 512  # Максимальное количество токенов для генерации
# temperature = 0.7  # Параметр случайности в ответах модели

# Переменная для ленивой загрузки модели
llm = None
max_tokens = 4096

def get_model():
    """Лениво загружает модель LLaMA через LlamaCpp."""
    global llm
    if llm is None:
        print("Загрузка модели Llama...")
        llm = Llama(
            model_path=model_path,
            n_gpu_layers=0,  # Установите 0, если у вас нет GPU
            n_batch=512,  # Уменьшите размер пакета
            n_ctx=4096,  # Уменьшите размер контекста
            f16_kv=True,  # Используйте FP16, если у вас есть GPU
            verbose=True  # Включите отладочный вывод
        )
        print("Модель успешно загружена!")
    return llm

def preprocess_text(text):
    """Предварительная обработка текста перед отправкой в модель."""
    return text.lower()


def start_llama_dialogue(text):
    """Функция для запроса в LLaMA с использованием langchain."""
    try:
        print("Запрос в LLaMA:", text)

        # Формируем ввод с системным сообщением и текущим запросом пользователя
        input_text = f"system: {system_message}\nuser: {text}\nassistant:"

        # Загружаем модель
        model = get_model()

        # Генерация ответа
        response = model(input_text, max_tokens=max_tokens, temperature=temperature)
        print("Ответ от LLaMA:", response)

        # Очищаем ответ
        clean_response = extract_last_assistant_response(response)
        print("Чистый ответ:", clean_response)

        return clean_response

    except Exception as e:
        print(f"Ошибка в работе LLaMA: {str(e)}")
        return f"Произошла ошибка: {str(e)}"


def extract_last_assistant_response(raw_response):
    """
    Извлекает только последний ответ ассистента.
    """
    # Разделяем по строкам и извлекаем последний ответ
    parts = raw_response.split("assistant:")
    if len(parts) > 1:
        clean_response = parts[-1].strip()
        return clean_response
    else:
        return "Не удалось извлечь ответ ассистента."


def clear_text(response):
    """Очищает текст ответа от ненужных символов перед озвучкой."""
    table = str.maketrans({'`': '', '(': '', ')': ' ', '@': 'at ', '_': ' '})
    response = response.translate(table)
    return response


def save_code(code):
    """Сохраняет код в файл для последующего просмотра."""
    with open('temporary_files/code.py', 'w', encoding='utf-8') as r:
        r.write(code)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    code_path = os.path.join(dir_path, 'temporary_files', 'code.py')

    subprocess.Popen(['python', '-m', 'idlelib', '-e', code_path])


def remove_punctuation(file_name):
    """Удаляет всю пунктуацию из строки."""
    translator = str.maketrans('', '', string.punctuation)
    return file_name.translate(translator)

# llm = Llama(model_path="F:/voice_assistant/VoiceAssistant/local_model_cache/llama-3.2-8b-instruct.Q8_0.gguf")
# print("Llama успешно загружена!")


# from langchain_community.llms import LlamaCpp

# model_path = "F:/voice_assistant/VoiceAssistant/local_model_cache/llama-3.1-8b-instruct.Q8_0.gguf"

# try:
#     llm = LlamaCpp(model_path=model_path)
#     print("Модель успешно загружена!")
# except Exception as e:
#     print(f"Ошибка загрузки модели: {e}")
