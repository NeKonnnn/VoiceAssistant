import sys
import os
from threading import Thread
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel
from PyQt6.QtGui import QIcon, QMovie, QMouseEvent
from PyQt6.QtCore import QTimer, QSize, QRect, Qt, QPropertyAnimation, QThread, pyqtSignal, pyqtSlot
import voice
from PyQt6.QtCore import QMetaObject
# Импортируем функции из проекта
from microphone_new import recognize_wheel, set_nn_active  # Импорт функции распознавания
from chatGPT import write_history, new_dialogue
from commands.command_executor import execute_command
from voice_assistant_gui.settings_window import SettingsWindow
from voice_assistant_gui.settings_manager import add_exe_path, get_exe_path, get_selected_model, get_all_commands
import multiprocessing
from llama_utils import call_llama_via_subprocess

multiprocessing.set_start_method("spawn", force=True)

# Для вызова LLaMA через subprocess
import subprocess

class ClickableLabel(QLabel):
    """
    Класс для создания кликабельного QLabel, который будет использоваться для отображения
    анимированной гифки и обрабатывать нажатия.
    """
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Чтобы QLabel корректно обрабатывал события мыши:
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit()
        super().mousePressEvent(event)

class AssistantThread(QThread):
    """
    Класс для запуска голосового ассистента в отдельном потоке с использованием QThread.
    """
    def run(self):
        recognize_wheel()  # Запускаем функцию распознавания

class LlamaWorkerProcess(QThread):
    """
    Класс для вызова LLaMA через subprocess в отдельном потоке.
    При запуске вызывается скрипт llama_worker.py и результат эмитируется через сигнал.
    """
    finished = pyqtSignal(str)

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)
        self.prompt = prompt

    def run(self):
        response = call_llama_via_subprocess(self.prompt)
        self.finished.emit(response)

class VoiceAssistantApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Убираем стандартный заголовок окна
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Voice Assistant")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(300, 200)

        # Основной фон окна
        self.setStyleSheet("background-color: #25171A;")

        # Полоса заголовка окна
        self.title_bar = QWidget(self)
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: #333;")

        # Логика для перемещения и изменения размера окна
        self.drag_pos = None
        self.resizing = False

        # Кнопка для закрытия окна (X)
        self.close_button = QPushButton("X", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5722;
                border-radius: 15px;
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

        # Расположение кнопок на панели заголовка
        self.title_bar.move(0, 0)
        self.close_button.move(self.width() - 40, 5)
        self.minimize_button.move(self.width() - 120, 5)
        self.maximize_button.move(self.width() - 80, 5)

        # Кнопка для подключения нейронки
        self.nn_button = QPushButton("Подключить нейронку", self)
        self.nn_button.setIconSize(QSize(40, 40))
        self.nn_button.setStyleSheet(self.blue_button_style())
        self.nn_button.clicked.connect(self.toggle_neural_network)
        self.nn_active = False  # Статус подключения нейронки

        # Метка для отображения статуса загрузки нейронки
        self.loading_label = QLabel("", self)
        self.loading_label.setStyleSheet("color: white; font-size: 14px;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide()

        # Статус активации ассистента
        self.assistant_active = False
        self.chatgpt_active = False
        self.menu_open = False

        # Заменяем круглую кнопку на кликабельную метку с анимированной гифкой
        self.assistant_button = ClickableLabel(self)
        # Загружаем анимированную гифку button.gif из папки icons
        self.movie = QMovie("icons/button.gif")
        self.assistant_button.setMovie(self.movie)
        self.movie.start()
        self.assistant_button.setScaledContents(True)
        self.assistant_button.clicked.connect(self.toggle_assistant)

        # Кнопки меню
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

        # Кнопка гамбургер-меню
        self.menu_button = QPushButton(self)
        self.menu_button.setIcon(QIcon("icons/menu.png"))
        self.menu_button.setIconSize(QSize(30, 30))
        self.menu_button.setFixedSize(50, 40)
        self.menu_button.setStyleSheet(self.brown_button_style())
        self.menu_button.move(0, 0)
        self.menu_button.clicked.connect(self.toggle_menu)

        # Layout для меню
        self.menu_layout = QVBoxLayout()
        self.menu_layout.addWidget(self.refresh_button)
        self.menu_layout.addWidget(self.nn_button)
        self.menu_layout.addWidget(self.settings_button)
        self.menu_layout.addWidget(self.commands_button)

        self.menu_widget = QWidget(self)
        self.menu_widget.setLayout(self.menu_layout)
        self.menu_widget.setGeometry(10, 60, 0, self.height())
        self.menu_widget.hide()

        # Центрирование кнопки при изменении размера окна
        self.centralize_button()

        # Анимации (при необходимости)
        self.wheel_mic_animation = None
        self.wheel_gpt_animation = None
        self.wheel_refresh_animation = None

    def resizeEvent(self, event):
        """Центрирование кнопки и изменение размеров меню при изменении размера окна."""
        self.centralize_button()
        self.resize_menu()
        self.title_bar.resize(self.width(), 40)
        self.close_button.move(self.width() - 40, 5)
        self.minimize_button.move(self.width() - 120, 5)
        self.maximize_button.move(self.width() - 80, 5)

    def centralize_button(self):
        """Центрирование кнопки голосового ассистента и изменение её размера."""
        button_size = min(self.width(), self.height()) // 4
        self.assistant_button.setFixedSize(button_size, button_size)
        self.assistant_button.move(self.width() // 2 - self.assistant_button.width() // 2,
                                   self.height() // 2 - self.assistant_button.height() // 2)
        # Центрируем кнопку подключения нейронки и метку загрузки под ней
        self.nn_button.move(self.width() // 2 - self.nn_button.width() // 2,
                            self.height() // 2 + self.assistant_button.height())
        self.loading_label.setFixedWidth(self.nn_button.width())
        self.loading_label.move(self.width() // 2 - self.loading_label.width() // 2,
                                self.height() // 2 + self.nn_button.height() + 10)

    def resize_menu(self):
        """Изменение ширины меню в зависимости от ширины окна."""
        menu_width = min(self.width() // 4, 300)
        self.menu_widget.setGeometry(10, 60, menu_width, self.height())

    def toggle_menu(self):
        """Открытие/закрытие шторки меню по клику."""
        if self.menu_open:
            self.animate_menu_close()
        else:
            self.animate_menu_open()

    def animate_menu_open(self):
        """Анимация раскрытия меню."""
        self.menu_widget.show()
        menu_width = min(self.width() // 4, 300)
        self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(10, 60, 0, self.height()))
        self.animation.setEndValue(QRect(10, 60, menu_width, self.height()))
        self.animation.start()
        self.menu_open = True

    def animate_menu_close(self):
        """Анимация закрытия меню."""
        menu_width = min(self.width() // 4, 300)
        self.animation = QPropertyAnimation(self.menu_widget, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(10, 60, menu_width, self.height()))
        self.animation.setEndValue(QRect(10, 60, 0, self.height()))
        self.animation.finished.connect(self.menu_widget.hide)
        self.animation.start()
        self.menu_open = False

    def animate_mic(self, frame_index=0):
        frames = ['icons/microphone_frame1.png', 'icons/microphone_frame2.png']
        # Данная функция осталась для анимации микрофона (если потребуется)
        self.assistant_button.setPixmap(QIcon(frames[frame_index]).pixmap(self.assistant_button.size()))
        self.wheel_mic_animation = QTimer.singleShot(100, lambda: self.animate_mic((frame_index + 1) % len(frames)))

    def stop_mic_animation(self):
        if self.wheel_mic_animation:
            self.wheel_mic_animation = None

    def refresh_dialog(self):
        new_dialogue()
        os.environ.update(NEW_DIALOGUE='1')
        self.refresh_button.setIcon(QIcon("icons/refresh.png"))

    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def open_commands(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Available Commands")
        dialog.setGeometry(100, 100, 300, 200)
        dialog.setStyleSheet("background-color: #98C1D9;")
        label = QLabel("List of available commands:\n\n- Command 1\n- Command 2\n- Command 3", dialog)
        layout = QVBoxLayout()
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.exec()

    def blue_button_style(self):
        return """
        QPushButton {
            background-color: #6969B3;
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
            background-color: #7A7AC1;
        }
        """

    def brown_button_style(self):
        return """
        QPushButton {
            background-color: #4B244A;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border: none;
        }
        QPushButton:hover {
            background-color: #6A356D;
        }
        """

    def toggle_maximize_restore(self):
        """Разворачивание и восстановление окна."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            if event.position().x() > self.width() - 10 and event.position().y() > self.height() - 10:
                self.resizing = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.resizing:
            self.setGeometry(self.x(), self.y(), event.globalPosition().toPoint().x() - self.x(),
                             event.globalPosition().toPoint().y() - self.y())
        elif self.drag_pos:
            diff = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + diff)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.drag_pos = None
        self.resizing = False

    def toggle_neural_network(self):
        """
        Активация/деактивация нейронки (ChatGPT или LLaMA).
        """
        if self.nn_active:
            self.nn_button.setText("Подключить нейронку")
            self.loading_label.hide()
            self.nn_active = False
            set_nn_active(False)
            print("Нейронка отключена")
        else:
            self.loading_label.setText("Подгружаю нейронку...")
            self.loading_label.show()
            selected_model = get_selected_model()
            print(f"[DEBUG] Выбранная модель: {selected_model}")
            if selected_model == "LLaMA":
                self.llama_thread = LlamaWorkerProcess("Привет!")
                self.llama_thread.finished.connect(self.on_llama_finished)
                self.llama_thread.start()
            elif selected_model == "ChatGPT":
                from chatGPT import start_dialogue as start_chatgpt_dialogue
                response = start_chatgpt_dialogue("Привет!")
                self.loading_label.setText("Нейронка подключена!")
                voice.speaker_silero("Нейронка активна")
                print(f"[DEBUG] Ответ нейронки: {response}")
            else:
                self.loading_label.setText("Ошибка: модель не выбрана.")
            self.nn_button.setText("Выключить нейронку")
            self.nn_active = True
            set_nn_active(True)
            print("Нейронка подключена")

    @pyqtSlot(str)
    def on_llama_finished(self, response: str):
        self.loading_label.setText("Нейронка подключена!")
        self.loading_label.setStyleSheet("color: #00FF00; font-size: 14px;")
        QTimer.singleShot(3000, self.loading_label.hide)
        voice.speaker_silero("Нейронка активна")
        print(f"[DEBUG] Ответ нейронки: {response}")

    def toggle_assistant(self):
        """Активация и деактивация ассистента."""
        if self.assistant_active:
            # Можно добавить изменение гифки или остановку анимации, если требуется
            self.statusBar().showMessage("Voice Assistant deactivated", 2000)
            os.environ['MIC'] = '0'
            self.assistant_thread.quit()
        else:
            self.statusBar().showMessage("Voice Assistant activated", 2000)
            os.environ['MIC'] = '1'
            self.assistant_thread = AssistantThread()
            self.assistant_thread.start()
        self.assistant_active = not self.assistant_active

    def run_assistant(self):
        try:
            recognize_wheel()
        except Exception as e:
            self.statusBar().showMessage(f"Error running assistant: {str(e)}", 2000)

def main():
    print("[DEBUG] Используется Python:", sys.executable)
    app = QApplication(sys.argv)
    main_window = VoiceAssistantApp()
    print("[DEBUG] Загружаем LLaMA перед запуском GUI...")
    from llama1 import get_model
    get_model()  # Попытка предварительной загрузки модели
    print("[DEBUG] LLaMA загружена, запускаем GUI")
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Для поддержки многопроцессности на Windows
    main()