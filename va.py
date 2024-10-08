import os

from gui import Application

from configuration import SETTINGS
#устанавливаем переменные окружения из словаря SETTINGS
for key, value in SETTINGS.items():
    os.environ[key] = value

if __name__ == '__main__':
    root = Application()
    root.mainloop()


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