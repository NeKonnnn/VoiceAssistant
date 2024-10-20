import os
from configurations.listen_to_task import listen_to_task
import voice

def add_to_backlog():
    # Получаем путь к директории на уровень выше
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Текущая директория
    parent_dir = os.path.dirname(current_dir)  # Директория на уровень выше

    # Путь к файлу backlog.txt
    backlog_path = os.path.join(parent_dir, 'back_log', 'backlog.txt')

    # Уведомление для пользователя
    voice.speaker_silero("Пожалуйста, назовите задачу, которую вы хотите занести в бэклог.")
    task = listen_to_task()
    
    if task is not None:
        with open(backlog_path, "a", encoding='utf-8') as backlog_file:
            backlog_file.write("❗️ " + task + "\n")  # Добавляем символ ❗️ перед задачей
        voice.speaker_silero("Задача успешно добавлена в бэклог.")
    else:
        voice.speaker_silero("Не удалось распознать задачу. Попробуйте еще раз.")
