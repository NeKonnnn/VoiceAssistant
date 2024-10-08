import os
import subprocess
import voice
import pyautogui
import time

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

def swap_windows():
    # Переключаемся на другое окно
    pyautogui.keyDown('alt')
    time.sleep(0.1)
    pyautogui.press('tab')
    pyautogui.keyUp('alt')
    
    # Ждем, пока окно переключится
    time.sleep(0.5)
    
    # Получаем размеры экрана
    screen_width, screen_height = pyautogui.size()
    
    # Кликаем по центру экрана
    pyautogui.click(screen_width / 2, screen_height / 2)
    voice.speaker_silero("Свапнула окно, сэр")

def windows_down():
    exe_path = get_executable_path('blind.exe')
    if exe_path:
        subprocess.Popen([exe_path])
        voice.speaker_silero("Готово, сэр")

def windows_up():
    exe_path = get_executable_path('upwindows.exe')
    if exe_path:
        subprocess.Popen([exe_path])
        voice.speaker_silero("Готово, сэр")

def close_current_window():
    # Закрывает активное окно
    pyautogui.hotkey('alt', 'F4')
    voice.speaker_silero("Готово, сэр")


