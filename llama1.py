import os
import subprocess
import string
import logging
from llama_cpp import Llama
# from langchain_community.llms import LlamaCpp
import threading  # Добавляем защиту от многопоточного доступа

# Блокировка для предотвращения одновременной загрузки модели в нескольких потоках
model_lock = threading.Lock()

# Настройка логирования для отладки
logging.basicConfig(level=logging.DEBUG, filename="llama_debug.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Начальное системное сообщение
SYSTEM_PROMPT = "Ты дружелюбный и полезный ассистент. Отвечай только на русском языке, кратко и по делу."

# Путь к файлу модели GGUF
model_path = os.path.join(os.getcwd(), "local_model_cache/Q8_0.gguf")

# Проверяем, существует ли модель
if not os.path.exists(model_path):
    logging.error(f"Файл модели не найден по пути: {model_path}")
    raise FileNotFoundError(f"Файл модели {model_path} не найден!")

logging.info(f"Файл модели найден: {model_path}")

llm = None

n_ctx = 8192
top_k = 30
top_p = 0.9
temperature = 0.0
repeat_penalty = 1.1

def get_model():
    """Лениво загружает модель LLaMA через LlamaCpp."""
    global llm
    with model_lock:  # ✅ Блокируем одновременную загрузку модели из разных потоков
        if llm is None:
            print("Загрузка модели Llama...")
            logging.info("Запускаем загрузку модели LLaMA.")
            try:
                llm = Llama(
                    model_path=model_path,
                    n_gpu_layers=0,  # Если нет GPU
                    n_ctx=n_ctx,  # Ограничиваем контекст
                    verbose=True,
                    n_threads=4  # ✅ Уменьшаем потоки, если в системе мало ресурсов
                )
                print("Модель успешно загружена!")
                logging.info("Модель LLaMA успешно загружена.")
            except Exception as e:
                logging.error(f"Ошибка загрузки модели: {e}")
                raise
    return llm

def start_llama_dialogue(user_message):
    """Функция для запроса в LLaMA."""
    print("Запрос в LLaMA:", user_message)
    logging.debug(f"Запрос в LLaMA: {user_message}")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    
    # Проверяем, загружена ли модель перед вызовом
    model = get_model()
    if model is None:
        logging.error("Ошибка: модель не загружена!")
        raise RuntimeError("Модель LLaMA не была загружена!")

    logging.info("Модель успешно загружена, отправляем запрос.")

    answer = ""
    try:
        for part in model.create_chat_completion(
            messages,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            stream=True,
        ):
            delta = part["choices"][0]["delta"]
            if "content" in delta:
                answer += delta["content"]
                print(delta["content"], end="", flush=True)  # Потоковый вывод в консоль

    except Exception as e:
        logging.error(f"Ошибка при генерации ответа: {e}")
        raise

    print("\nОтвет от LLaMA:", answer)
    logging.debug(f"Ответ от LLaMA: {answer}")

    return answer  # Теперь возвращает строку, а не генератор

def clear_text(response):
    """Очищает текст ответа от ненужных символов перед озвучкой."""
    table = str.maketrans({"`": "", "(": "", ")": " ", "@": "at ", "_": " "})
    return response.translate(table)

def save_code(code):
    """Сохраняет код в файл для последующего просмотра."""
    temp_dir = os.path.join(os.getcwd(), "temporary_files")
    os.makedirs(temp_dir, exist_ok=True)  # Создаёт директорию, если её нет
    code_path = os.path.join(temp_dir, "code.py")
    
    with open(code_path, "w", encoding="utf-8") as r:
        r.write(code)
    
    subprocess.Popen(["python", "-m", "idlelib", "-e", code_path])

def remove_punctuation(file_name):
    """Удаляет всю пунктуацию из строки."""
    translator = str.maketrans("", "", string.punctuation)
    return file_name.translate(translator)

if __name__ == "__main__":
    # Простой тестовый запуск скрипта
    try:
        user_input = input("Введите ваш запрос для LLaMA: ")
        print("\nНачинаем диалог с LLaMA...\n")
        start_llama_dialogue(user_input)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
