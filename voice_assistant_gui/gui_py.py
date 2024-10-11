import sys
import os
from threading import Thread
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel
from PyQt6.QtGui import QIcon, QMouseEvent
from PyQt6.QtCore import QTimer, QSize, QRect, Qt, QPropertyAnimation, QThread

# Импортируем функции из вашего проекта
from microphone_new import recognize_wheel  # Возврат на один уровень вверх к файлу microphone_new.py
from chatGPT import write_history, new_dialogue

# Импортируем функцию для запуска команд
from commands.command_executor import execute_command

# Импортируем функции для работы с настройками
from voice_assistant_gui.settings_window import SettingsWindow
from voice_assistant_gui.settings_manager import add_exe_path, get_exe_path

class AssistantThread(QThread):
    """
    Класс для запуска голосового ассистента в отдельном потоке с использованием QThread
    """
    def run(self):
        recognize_wheel()  # Запускаем функцию распознавания

class VoiceAssistantApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Убираем стандартный заголовок окна
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Voice Assistant")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(300, 200)  # Устанавливаем минимальный размер окна

        # Установка основного фона окна
        self.setStyleSheet("background-color: #25171A;")  # Основной фон

        # Полоса заголовка окна (панель управления окном)
        self.title_bar = QWidget(self)
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: #333;")

        # Логика для передвижения и изменения размера окна
        self.drag_pos = None
        self.resizing = False

        # Кнопка для закрытия окна (X в кружочке)
        self.close_button = QPushButton("X", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                border-radius: 15px;  /* Круглая кнопка */
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff784e;
            }
        """)
        self.close_button.clicked.connect(self.close)

        # Кнопка для сворачивания окна (-)
        self.minimize_button = QPushButton("-", self.title_bar)
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border-radius: 15px;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.minimize_button.clicked.connect(self.showMinimized)

        # Кнопка для разворачивания окна (□)
        self.maximize_button = QPushButton("□", self.title_bar)
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                border-radius: 15px;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)

        # Располагаем кнопки на панели заголовка
        self.title_bar.move(0, 0)
        self.close_button.move(self.width() - 40, 5)
        self.minimize_button.move(self.width() - 120, 5)
        self.maximize_button.move(self.width() - 80, 5)

        # Статус для активации/деактивации
        self.assistant_active = False
        self.chatgpt_active = False
        self.menu_open = False  # Статус открытия меню

        # Создаем центральную круглую кнопку для активации/деактивации голосового помощника
        self.assistant_button = QPushButton(self)  # Убрали текст "Voice Assistant"
        self.assistant_button.setIcon(QIcon("icons/microphone_off_red.png"))  # Иконка перечеркнутого микрофона
        self.assistant_button.setIconSize(QSize(60, 60))
        self.assistant_button.setStyleSheet(self.round_button_style())
        self.assistant_button.clicked.connect(self.toggle_assistant)  # Подключаем метод

        # Создаем кнопки для функционала, которые будут скрыты в боковом меню
        self.chatgpt_button = QPushButton("ChatGPT", self)
        self.chatgpt_button.setIcon(QIcon("icons/chatgpt.png"))
        self.chatgpt_button.setIconSize(QSize(40, 40))
        self.chatgpt_button.setStyleSheet(self.blue_button_style())
        self.chatgpt_button.clicked.connect(self.toggle_chatgpt)

        self.refresh_button = QPushButton("Refresh Dialog", self)
        self.refresh_button.setIcon(QIcon("icons/refresh.png"))
        self.refresh_button.setIconSize(QSize(40, 40))
        self.refresh_button.setStyleSheet(self.blue_button_style())
        self.refresh_button.clicked.connect(self.refresh_dialog)

        self.settings_button = QPushButton("Settings", self)
        self.settings_button.setIcon(QIcon("icons/settings.png"))
        self.settings_button.setIconSize(QSize(40, 40))
        self.settings_button.setStyleSheet(self.blue_button_style())
        self.settings_button.clicked.connect(self.open_settings)

        self.commands_button = QPushButton("Commands", self)
        self.commands_button.setIcon(QIcon("icons/commands.png"))
        self.commands_button.setIconSize(QSize(40, 40))
        self.commands_button.setStyleSheet(self.blue_button_style())
        self.commands_button.clicked.connect(self.open_commands)

        # Меню в виде 3 черточек (гамбургер-меню)
        self.menu_button = QPushButton(self)
        self.menu_button.setIcon(QIcon("icons/menu.png"))
        self.menu_button.setIconSize(QSize(30, 30))
        self.menu_button.setFixedSize(50, 40)
        self.menu_button.setStyleSheet(self.brown_button_style())
        self.menu_button.move(0, 0)
        self.menu_button.clicked.connect(self.toggle_menu)

        # Layout для кнопок, скрытых в боковом меню
        self.menu_layout = QVBoxLayout()
        self.menu_layout.addWidget(self.chatgpt_button)
        self.menu_layout.addWidget(self.refresh_button)
        self.menu_layout.addWidget(self.settings_button)
        self.menu_layout.addWidget(self.commands_button)

        self.menu_widget = QWidget(self)
        self.menu_widget.setLayout(self.menu_layout)
        self.menu_widget.setGeometry(10, 60, 0, self.height())  # Меню будет изменять свою высоту в зависимости от окна
        self.menu_widget.hide()

        # Центрирование кнопки при изменении размера
        self.centralize_button()

        # Анимации для ассистента, ChatGPT и обновления
        self.wheel_mic_animation = None
        self.wheel_gpt_animation = None
        self.wheel_refresh_animation = None
        

    def resizeEvent(self, event):
        """Центрирование кнопки и изменение размеров меню при изменении размера окна."""
        self.centralize_button()
        self.resize_menu()
        self.title_bar.resize(self.width(), 40)  # Изменение ширины заголовка при изменении размера окна
        self.close_button.move(self.width() - 40, 5)
        self.minimize_button.move(self.width() - 120, 5)
        self.maximize_button.move(self.width() - 80, 5)

    def centralize_button(self):
        """Функция для центрирования кнопки голосового помощника и изменения её размера в зависимости от размеров экрана."""
        button_size = min(self.width(), self.height()) // 4  # Размер кнопки = 1/4 от минимального размера окна
        self.assistant_button.setFixedSize(button_size, button_size)
        self.assistant_button.setIconSize(QSize(button_size // 2, button_size // 2))  # Размер иконки 1/2 от кнопки
        self.assistant_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #533A7B;
                border-radius: {button_size // 2}px;  /* Круглая форма */
                color: white;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #6A4B9A;
            }}
        """)
        self.assistant_button.move(self.width() // 2 - self.assistant_button.width() // 2,
                                   self.height() // 2 - self.assistant_button.height() // 2)

    def resize_menu(self):
        """Функция для изменения ширины меню в зависимости от ширины окна."""
        menu_width = min(self.width() // 4, 300)  # Меню занимает 1/4 ширины окна, но не больше 300px
        self.menu_widget.setGeometry(10, 60, menu_width, self.height())  # Меню также увеличивает свою высоту

    def toggle_menu(self):
        """Функция для открытия/закрытия шторки меню по клику."""
        if self.menu_open:
            self.animate_menu_close()
        else:
            self.animate_menu_open()

    def animate_menu_open(self):
        """Анимация раскрытия меню."""
        self.menu_widget.show()
        menu_width = min(self.width() // 4, 300)  # Меню занимает 1/4 ширины окна, но не больше 300px
        self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
        self.animation.setDuration(300)  # Длительность анимации
        self.animation.setStartValue(QRect(10, 60, 0, self.height()))
        self.animation.setEndValue(QRect(10, 60, menu_width, self.height()))  # Раскрытие до ширины 1/4 экрана
        self.animation.start()
        self.menu_open = True

    def animate_menu_close(self):
        """Анимация закрытия меню."""
        menu_width = min(self.width() // 4, 300)  # Меню занимает 1/4 ширины окна, но не больше 300px
        self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
        self.animation.setDuration(300)  # Длительность анимации
        self.animation.setStartValue(QRect(10, 60, menu_width, self.height()))
        self.animation.setEndValue(QRect(10, 60, 0, self.height()))  # Закрытие до ширины 0
        self.animation.finished.connect(self.menu_widget.hide)  # Скрываем после анимации
        self.animation.start()
        self.menu_open = False

    # Функция для анимации ассистента
    def animate_mic(self, frame_index=0):
        frames = ['icons/microphone_frame1.png', 'icons/microphone_frame2.png']  # примеры кадров
        self.assistant_button.setIcon(QIcon(frames[frame_index]))
        self.wheel_mic_animation = QTimer.singleShot(100, lambda: self.animate_mic((frame_index + 1) % len(frames)))

    def stop_mic_animation(self):
        if self.wheel_mic_animation:
            self.wheel_mic_animation = None

    # Запуск/остановка ChatGPT
    def toggle_chatgpt(self):
        if int(os.getenv('CHATGPT', '0')):
            os.environ.update(CHATGPT='0')
            self.chatgpt_button.setText("Connect to ChatGPT")
            self.stop_gpt_animation()
        elif not int(os.getenv('MIC', '0')):
            return
        else:
            os.environ.update(CHATGPT='1')
            self.animate_gpt()

    def animate_gpt(self, frame_index=0):
        frames = ['icons/chatgpt_frame1.png', 'icons/chatgpt_frame2.png']  # примеры кадров
        self.chatgpt_button.setIcon(QIcon(frames[frame_index]))
        self.wheel_gpt_animation = QTimer.singleShot(100, lambda: self.animate_gpt((frame_index + 1) % len(frames)))

    def stop_gpt_animation(self):
        if self.wheel_gpt_animation:
            self.wheel_gpt_animation = None

    # Обновление диалога (очистка)
    def refresh_dialog(self):
        new_dialogue()
        os.environ.update(NEW_DIALOGUE='1')
        self.refresh_button.setIcon(QIcon("icons/refresh.png"))

    # Открытие настроек
    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    # Открытие доступных команд
    def open_commands(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Available Commands")
        dialog.setGeometry(100, 100, 300, 200)
        dialog.setStyleSheet("background-color: #98C1D9;")  # Устанавливаем фон окна команд

        label = QLabel("List of available commands:\n\n- Command 1\n- Command 2\n- Command 3", dialog)
        layout = QVBoxLayout()
        layout.addWidget(label)
        dialog.setLayout(layout)

        dialog.exec()

    # Стиль для круглой кнопки ассистента
    def round_button_style(self):
        return """
        QPushButton {
            background-color: #533A7B;  /* Фиолетовый цвет */
            border-radius: 75px;
            color: white;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #6A4B9A;  /* Более светлый фиолетовый при наведении */
        }
        """

    # Стиль для кнопок ChatGPT, Обновить диалог, Настройки, Команды
    def blue_button_style(self):
        return """
        QPushButton {
            background-color: #6969B3;  /* Синий цвет */
            color: white;
            padding: 10px;
            font-size: 18px;
            text-align: left;
            border: none;
            width: 200px;
            height: 50px;
            border-radius: 25px;
        }
        QPushButton:hover {
            background-color: #7A7AC1;  /* Более светлый синий при наведении */
        }
        """

    # Стиль для кнопки гамбургер-меню
    def brown_button_style(self):
        return """
        QPushButton {
            background-color: #4B244A;  /* Коричневый цвет */
            color: white;
            font-size: 16px;
            font-weight: bold;
            border: none;
        }
        QPushButton:hover {
            background-color: #6A356D;  /* Более светлый коричневый при наведении */
        }
        """

    def toggle_maximize_restore(self):
        """Функция для разворачивания и восстановления окна"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        """Функция для перетаскивания окна и изменения размеров"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            if event.position().x() > self.width() - 10 and event.position().y() > self.height() - 10:
                self.resizing = True  # Начинаем изменять размер, если мышь находится в правом нижнем углу

    def mouseMoveEvent(self, event: QMouseEvent):
        """Функция для перемещения окна или изменения его размеров"""
        if self.resizing:
            self.setGeometry(self.x(), self.y(), event.globalPosition().toPoint().x() - self.x(),
                             event.globalPosition().toPoint().y() - self.y())
        elif self.drag_pos:
            diff = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + diff)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Сброс позиции перетаскивания и изменения размеров"""
        self.drag_pos = None
        self.resizing = False

    def toggle_assistant(self):
        """Метод для активации и деактивации ассистента."""
        if self.assistant_active:
            # Отключаем ассистент, меняем иконку на перечеркнутый микрофон
            self.assistant_button.setIcon(QIcon("icons/microphone_off_red.png"))
            self.statusBar().showMessage("Voice Assistant deactivated", 2000)
            os.environ['MIC'] = '0'  # Отключаем ассистент через переменную окружения
            self.assistant_thread.quit()  # Останавливаем поток ассистента
        else:
            # Включаем ассистент, меняем иконку на обычный микрофон
            self.assistant_button.setIcon(QIcon("icons/microphone.png"))
            self.statusBar().showMessage("Voice Assistant activated", 2000)
            os.environ['MIC'] = '1'  # Активируем ассистент через переменную окружения

            # Запускаем ассистент в потоке QThread
            self.assistant_thread = AssistantThread()
            self.assistant_thread.start()

        # Инвертируем статус активности ассистента
        self.assistant_active = not self.assistant_active

    def run_assistant(self):
        """Функция для запуска голосового ассистента."""
        try:
            recognize_wheel()  # Запуск функции распознавания
        except Exception as e:
            self.statusBar().showMessage(f"Error running assistant: {str(e)}", 2000)

def main():
    app = QApplication(sys.argv)
    main_window = VoiceAssistantApp()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()






# C ANIMATION___________________________
# import sys
# from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QDialog
# from PyQt6.QtGui import QIcon, QPainter, QBrush, QColor
# from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QRect, QEasingCurve

# class VoiceAssistantApp(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Voice Assistant")
#         self.setGeometry(100, 100, 800, 600)

#         # Статус для активации/деактивации
#         self.assistant_active = False
#         self.chatgpt_active = False
#         self.menu_open = False  # Статус открытия меню

#         # Создаем центральную круглую кнопку для активации/деактивации голосового помощника
#         self.assistant_button = QPushButton("Voice Assistant", self)
#         self.assistant_button.setIcon(QIcon("icons/microphone.png"))
#         self.assistant_button.setIconSize(QSize(60, 60))
#         self.assistant_button.setStyleSheet(self.round_button_style())
#         self.assistant_button.clicked.connect(self.toggle_assistant)

#         # Анимация для кнопки - анимация изменения размера кнопки и ее положения
#         self.pulse_animation = QPropertyAnimation(self.assistant_button, b"geometry")
#         self.pulse_animation.setDuration(1000)  # Длительность анимации 1 секунда
#         self.pulse_animation.setLoopCount(-1)  # Зацикленная анимация
#         self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # Плавная анимация

#         # Создаем кнопки для функционала, которые будут скрыты в боковом меню
#         self.chatgpt_button = QPushButton("ChatGPT", self)
#         self.chatgpt_button.setIcon(QIcon("icons/chatgpt.png"))
#         self.chatgpt_button.setIconSize(QSize(40, 40))
#         self.chatgpt_button.setStyleSheet(self.menu_button_style())
#         self.chatgpt_button.clicked.connect(self.toggle_chatgpt)

#         self.refresh_button = QPushButton("Refresh Dialog", self)
#         self.refresh_button.setIcon(QIcon("icons/refresh.png"))
#         self.refresh_button.setIconSize(QSize(40, 40))
#         self.refresh_button.setStyleSheet(self.menu_button_style())
#         self.refresh_button.clicked.connect(self.refresh_dialog)

#         self.settings_button = QPushButton("Settings", self)
#         self.settings_button.setIcon(QIcon("icons/settings.png"))
#         self.settings_button.setIconSize(QSize(40, 40))
#         self.settings_button.setStyleSheet(self.menu_button_style())
#         self.settings_button.clicked.connect(self.open_settings)

#         self.commands_button = QPushButton("Commands", self)
#         self.commands_button.setIcon(QIcon("icons/commands.png"))
#         self.commands_button.setIconSize(QSize(40, 40))
#         self.commands_button.setStyleSheet(self.menu_button_style())
#         self.commands_button.clicked.connect(self.open_commands)

#         # Меню в виде 3 черточек (гамбургер-меню)
#         self.menu_button = QPushButton(self)
#         self.menu_button.setIcon(QIcon("icons/menu.png"))
#         self.menu_button.setIconSize(QSize(30, 30))
#         self.menu_button.setFixedSize(50, 50)
#         self.menu_button.setStyleSheet(self.menu_button_style())
#         self.menu_button.move(10, 10)
#         self.menu_button.clicked.connect(self.toggle_menu)

#         # Layout для кнопок, скрытых в боковом меню
#         self.menu_layout = QVBoxLayout()
#         self.menu_layout.addWidget(self.chatgpt_button)
#         self.menu_layout.addWidget(self.refresh_button)
#         self.menu_layout.addWidget(self.settings_button)
#         self.menu_layout.addWidget(self.commands_button)

#         self.menu_widget = QWidget(self)
#         self.menu_widget.setLayout(self.menu_layout)
#         self.menu_widget.setGeometry(10, 60, 0, self.height())  # Меню будет изменять свою высоту в зависимости от окна
#         self.menu_widget.hide()

#         # Центрирование кнопки при изменении размера
#         self.centralize_button()

#     def resizeEvent(self, event):
#         """Центрирование кнопки и изменение размеров меню при изменении размера окна."""
#         self.centralize_button()
#         self.resize_menu()

#     def centralize_button(self):
#         """Функция для центрирования кнопки голосового помощника и изменения её размера в зависимости от размеров экрана."""
#         button_size = min(self.width(), self.height()) // 4  # Размер кнопки = 1/4 от минимального размера окна
#         self.assistant_button.setFixedSize(button_size, button_size)
#         self.assistant_button.setIconSize(QSize(button_size // 2, button_size // 2))  # Размер иконки 1/2 от кнопки
#         self.assistant_button.setStyleSheet(f"""
#             QPushButton {{
#                 background-color: #555;
#                 border-radius: {button_size // 2}px;  /* Круглая форма */
#                 color: white;
#                 font-size: 16px;
#                 font-weight: bold;
#             }}
#             QPushButton:hover {{
#                 background-color: #777;
#             }}
#         """)
#         self.assistant_button.move(self.width() // 2 - self.assistant_button.width() // 2,
#                                    self.height() // 2 - self.assistant_button.height() // 2)

#     def resize_menu(self):
#         """Функция для изменения ширины меню в зависимости от ширины окна."""
#         menu_width = min(self.width() // 4, 300)  # Меню занимает 1/4 ширины окна, но не больше 300px
#         self.menu_widget.setGeometry(10, 60, menu_width, self.height())  # Меню также увеличивает свою высоту

#     def toggle_menu(self):
#         """Функция для открытия/закрытия шторки меню по клику."""
#         if self.menu_open:
#             self.animate_menu_close()
#         else:
#             self.animate_menu_open()

#     def animate_menu_open(self):
#         """Анимация раскрытия меню."""
#         self.menu_widget.show()
#         menu_width = min(self.width() // 4, 300)  # Меню занимает 1/4 ширины окна, но не больше 300px
#         self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
#         self.animation.setDuration(300)  # Длительность анимации
#         self.animation.setStartValue(QRect(10, 60, 0, self.height()))
#         self.animation.setEndValue(QRect(10, 60, menu_width, self.height()))  # Раскрытие до ширины 1/4 экрана
#         self.animation.start()
#         self.menu_open = True

#     def animate_menu_close(self):
#         """Анимация закрытия меню."""
#         menu_width = min(self.width() // 4, 300)  # Меню занимает 1/4 ширины окна, но не больше 300px
#         self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
#         self.animation.setDuration(300)  # Длительность анимации
#         self.animation.setStartValue(QRect(10, 60, menu_width, self.height()))
#         self.animation.setEndValue(QRect(10, 60, 0, self.height()))  # Закрытие до ширины 0
#         self.animation.finished.connect(self.menu_widget.hide)  # Скрываем после анимации
#         self.animation.start()
#         self.menu_open = False

#     def toggle_assistant(self):
#         """Функция для активации и деактивации голосового помощника"""
#         if self.assistant_active:
#             self.assistant_button.setIcon(QIcon("icons/microphone.png"))
#             self.stop_pulse_animation()
#             self.statusBar().showMessage("Voice Assistant deactivated", 2000)
#         else:
#             self.assistant_button.setIcon(QIcon("icons/microphone_active.png"))
#             self.start_pulse_animation()
#             self.statusBar().showMessage("Voice Assistant activated", 2000)

#         self.assistant_active = not self.assistant_active

#     def start_pulse_animation(self):
#         """Запуск пульсирующей анимации кнопки"""
#         button_geometry = self.assistant_button.geometry()
#         expanded_geometry = button_geometry.adjusted(-10, -10, 10, 10)  # Увеличиваем размеры на 10 пикселей

#         # Анимация будет изменять размер и позицию кнопки (чтобы оставаться по центру)
#         self.pulse_animation.setStartValue(button_geometry)
#         self.pulse_animation.setEndValue(expanded_geometry)
#         self.pulse_animation.start()

#     def stop_pulse_animation(self):
#         """Остановка пульсирующей анимации кнопки"""
#         self.pulse_animation.stop()

#     def toggle_chatgpt(self):
#         """Функция для активации и деактивации ChatGPT"""
#         if self.chatgpt_active:
#             self.chatgpt_button.setText("Connect to ChatGPT")
#             self.statusBar().showMessage("ChatGPT disconnected", 2000)
#         else:
#             self.chatgpt_button.setText("Disconnect from ChatGPT")
#             self.statusBar().showMessage("ChatGPT connected", 2000)

#         self.chatgpt_active = not self.chatgpt_active

#     def open_settings(self):
#         self.statusBar().showMessage("Opening Assistant Settings...", 2000)

#     def open_commands(self):
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Available Commands")
#         dialog.setGeometry(100, 100, 300, 200)

#         label = QLabel("List of available commands:\n\n- Command 1\n- Command 2\n- Command 3", dialog)
#         layout = QVBoxLayout()
#         layout.addWidget(label)
#         dialog.setLayout(layout)

#         dialog.exec()

#     def refresh_dialog(self):
#         self.statusBar().showMessage("Refreshing dialog...", 2000)

#     def round_button_style(self):
#         """Стиль для круглой кнопки голосового ассистента"""
#         return """
#         QPushButton {
#             background-color: #555;
#             border-radius: 75px;
#             color: white;
#             font-size: 16px;
#             font-weight: bold;
#         }
#         QPushButton:hover {
#             background-color: #777;
#         }
#         """

#     def menu_button_style(self):
#         """Стиль для кнопок в боковом меню"""
#         return """
#         QPushButton {
#             background-color: #333;
#             color: white;
#             padding: 10px;
#             font-size: 18px;
#             text-align: left;
#             border: none;
#             width: 200px;  /* Фиксированная ширина кнопки */
#             height: 50px;  /* Фиксированная высота кнопки */
#         }
#         QPushButton:hover {
#             background-color: #555;
#         }
#         """

# def main():
#     app = QApplication(sys.argv)
#     main_window = VoiceAssistantApp()
#     main_window.show()
#     sys.exit(app.exec())

# if __name__ == "__main__":
#     main()