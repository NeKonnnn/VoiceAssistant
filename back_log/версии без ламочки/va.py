import sys
import os
from PyQt6.QtWidgets import QApplication 

# Импортируем класс VoiceAssistantApp 
from voice_assistant_gui.gui_py import VoiceAssistantApp
from configuration import SETTINGS

# Устанавливаем переменные окружения из словаря SETTINGS
for key, value in SETTINGS.items():
    if key == 'KEYWORD_PATH':
        os.environ[key] = value[0]  # Извлекаем первый элемент списка
    else:
        os.environ[key] = str(value)  # Преобразуем все значения в строки

if __name__ == '__main__':
    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Инициализируем главное окно
    root = VoiceAssistantApp()

    # Показываем главное окно
    root.show()

    # Запускаем основной цикл приложения PyQt6
    sys.exit(app.exec())


# ------------------------------
# Работает с TKinter
# import os

# from gui import Application

# from configuration import SETTINGS
# #устанавливаем переменные окружения из словаря SETTINGS
# for key, value in SETTINGS.items():
#     os.environ[key] = value

# if __name__ == '__main__':
#     root = Application()
#     root.mainloop()
# --------------------------------

# для PyQT6
# import os
# import sys
# from PyQt6.QtWidgets import QApplication
# from gui import Application  # PyQt6-based Application class
# from configuration import SETTINGS

# # Устанавливаем переменные окружения из словаря SETTINGS
# for key, value in SETTINGS.items():
#     os.environ[key] = value

# if __name__ == '__main__':
#     # Создаем экземпляр QApplication (обязательно)
#     app = QApplication(sys.argv)
    
#     # Создаем основное окно приложения
#     window = Application()
    
#     # Показываем окно
#     window.show()

#     # Запускаем основной цикл приложения
#     sys.exit(app.exec())



# import os
# from voice_assistant_gui import run_gui

# from configuration import SETTINGS
# #устанавливаем переменные окружения из словаря SETTINGS
# # Устанавливаем переменные окружения
# for key, value in SETTINGS.items():
#     os.environ[key] = value

# # Запускаем GUI из Rust
# if __name__ == '__main__':
#     run_gui()  # Вызываем функцию run_gui, которая была экспортирована из Rust