import os
import subprocess
import voice

def get_executable_path(exe_name):
    # Получаем путь к текущей директории
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # Это директория на уровень выше

    # Путь к исполняемому файлу
    exe_path = os.path.join(parent_dir, 'exe', exe_name)

    # Проверка, существует ли файл
    if not os.path.exists(exe_path):
        print(f"Файл {exe_name} не найден по пути: {exe_path}")
        return None

    return exe_path

def task_manager():
    exe_path = get_executable_path('task_manager.exe')
    if exe_path:
        subprocess.run([exe_path])
        voice.speaker_silero("Открыла диспетчер задач, сэр")
