import json
import os

# Функция для сохранения настроек в файл
def save_settings(settings_file, data):
    with open(settings_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Функция для загрузки настроек из файла
def load_settings(settings_file):
    if os.path.exists(settings_file):
        with open(settings_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# Функция для добавления пути до exe файла в настройки
def add_exe_path(command_name, exe_path, settings_file="settings.json"):
    settings = load_settings(settings_file)
    
    # Добавляем новый exe файл под определенной командой
    settings[command_name] = exe_path
    
    # Сохраняем настройки
    save_settings(settings_file, settings)

# Функция для получения пути к exe файлу по команде
def get_exe_path(command_name, settings_file="settings.json"):
    settings = load_settings(settings_file)
    
    # Возвращаем путь до exe файла для указанной команды
    return settings.get(command_name, None)

# Функция для получения всех команд и путей к exe файлам
def get_all_commands(settings_file="settings.json"):
    return load_settings(settings_file)

# Функция для сохранения выбранного голоса
def save_selected_voice(voice, settings_file="settings.json"):
    settings = load_settings(settings_file)
    settings['selected_voice'] = voice
    save_settings(settings_file, settings)

# Функция для получения выбранного голоса
def get_selected_voice(settings_file="settings.json"):
    settings = load_settings(settings_file)
    return settings.get('selected_voice', 'baya')  # По умолчанию 'baya'
