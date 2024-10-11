import subprocess
import os
import voice
from voice_assistant_gui.settings_manager import get_exe_path

def execute_command(command_name):
    # Получаем путь до файла по команде
    file_path = get_exe_path(command_name)
    
    if file_path:
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)  # Открываем файл через ассоциированное приложение
            elif os.name == 'posix':  # macOS и Linux
                subprocess.run(['open', file_path] if sys.platform == 'darwin' else ['xdg-open', file_path], check=True)

            voice.speaker_silero(f"Открываю {command_name}, сэр.")
        except Exception as e:
            voice.speaker_silero(f"Произошла ошибка при открытии {command_name}: {str(e)}")
    else:
        voice.speaker_silero(f"Не могу найти команду {command_name}. Проверьте настройки.")
