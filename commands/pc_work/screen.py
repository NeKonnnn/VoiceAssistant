import os
import subprocess
import voice

def screenshot():
    # Получаем путь к директории на уровень выше
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Это текущая директория
    parent_dir = os.path.dirname(current_dir)  # Это директория на уровень выше

    # Путь к исполняемому файлу
    exe_path = os.path.join(parent_dir, 'exe', 'screenshot.exe')

    # Отладочный вывод
    # print(f"Путь к исполняемому файлу: {exe_path}")

    # Проверка, существует ли файл
    if not os.path.exists(exe_path):
        print("Файл не найден по указанному пути!")
        return

    # Запускаем команду
    subprocess.run([exe_path])

    # Голосовое уведомление
    voice.speaker_silero("Скриншот готов, сэр")