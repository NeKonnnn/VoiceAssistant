import subprocess
import voice
import pyautogui
import time

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

def blinds_down():
    subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\blind.exe'])
    voice.speaker_silero("Готово, сэр")
    
def windows_up():
    subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\upwindows.exe'])
    voice.speaker_silero("Готово, сэр")
    
def close_current_window():
    # Закрывает активное окно
    pyautogui.hotkey('alt', 'F4')
    voice.speaker_silero("Готово, сэр")

