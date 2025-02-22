from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QSlider, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from voice_assistant_gui.settings_manager import add_exe_path, save_selected_voice, get_selected_voice, save_amplitude_threshold, load_amplitude_threshold
from voice import speaker_silero


class CustomMessageBox(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setStyleSheet("background-color: #25171A;")  # Основной фон окна
        self.setFixedSize(300, 150)  # Размер окна

        layout = QVBoxLayout()

        # Сообщение
        label = QLabel(message)
        label.setStyleSheet("color: white; font-size: 16px;")
        layout.addWidget(label)

        # Кнопка OK
        ok_button = QPushButton("OK", self)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #533A7B;  /* Цвет кнопок */
                color: white;               /* Цвет текста */
                border-radius: 10px;
                padding: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #6A4B9A;  /* Цвет кнопок при наведении */
            }
        """)
        ok_button.clicked.connect(self.accept)  # Закрытие окна при нажатии на кнопку
        layout.addWidget(ok_button)

        self.setLayout(layout)

# Пример использования CustomMessageBox
def show_custom_message(title, message):
    dialog = CustomMessageBox(title, message)
    dialog.exec()

# Новое окно для создания команды запуска файла
class CreateCommandWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Создать команду запуска файла")
        self.setGeometry(100, 100, 400, 200)
        self.setStyleSheet("background-color: #25171A;")  # Основной фон окна

        layout = QVBoxLayout()

        # Поле для ввода пути к программе
        self.exe_path_label = QLabel("Путь до файла:")
        self.exe_path_label.setStyleSheet("color: white; font-size: 16px;")  # Стиль текста
        layout.addWidget(self.exe_path_label)
        self.exe_path_input = QLineEdit(self)
        self.exe_path_input.setStyleSheet(self.get_line_edit_style())
        layout.addWidget(self.exe_path_input)

        # Кнопка для выбора файла через проводник
        self.browse_button = QPushButton("Выбрать файл", self)
        self.browse_button.setStyleSheet(self.get_button_style())
        self.browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_button)

        # Поле для ввода команды
        self.command_label = QLabel("Команда для запуска:")
        self.command_label.setStyleSheet("color: white; font-size: 16px;")  # Стиль текста
        layout.addWidget(self.command_label)
        self.command_input = QLineEdit(self)
        self.command_input.setStyleSheet(self.get_line_edit_style())
        layout.addWidget(self.command_input)

        # Кнопка для добавления команды
        self.add_button = QPushButton("Добавить команду", self)
        self.add_button.setStyleSheet(self.get_button_style())
        self.add_button.clicked.connect(self.add_command)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "All Files (*);;Executable Files (*.exe)")
        if file_path:
            self.exe_path_input.setText(file_path)
    

    def add_command(self):
        exe_path = self.exe_path_input.text().strip()
        command_name = self.command_input.text().strip()

        if exe_path and command_name:
            add_exe_path(command_name, exe_path)  # Сохранение в файл
            show_custom_message("Успех", f"Команда '{command_name}' добавлена.")
            self.close()  # Закрываем окно после успешного добавления
        else:
            show_custom_message("Ошибка", "Пожалуйста, введите путь до файла и команду.")

    def get_button_style(self):
        return """
        QPushButton {
            background-color: #6969B3;  /* Синий цвет */
            color: white;
            padding: 10px;
            font-size: 18px;
            text-align: center;
            border: none;
            width: 200px;
            height: 50px;
            border-radius: 25px;
        }
        QPushButton:hover {
            background-color: #7A7AC1;  /* Более светлый синий при наведении */
        }
        """

    def get_line_edit_style(self):
        return """
        QLineEdit {
            background-color: #333333;
            color: white;
            padding: 5px;
            font-size: 16px;
            border-radius: 10px;
        }
        """
    

# Словарь для сопоставления отображаемых имен голосов с их идентификаторами
voice_mapping = {
    "женский голос 1": "baya",
    "женский голос 2": "kseniya",
    "женский голос 3": "xenia",
    "мужской голос 1": "aidar",
    "мужской голос 2": "eugene"
}

# Новое окно для выбора голоса
class ChooseVoiceWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Выбрать голос")
        self.setGeometry(100, 100, 400, 150)
        self.setStyleSheet("background-color: #25171A;")  # Основной фон окна

        layout = QVBoxLayout()

        self.voice_label = QLabel("Выберите голос ассистента:")
        self.voice_label.setStyleSheet("color: white; font-size: 16px;")
        layout.addWidget(self.voice_label)

        # Выпадающий список с отображаемыми именами
        self.voice_combo = QComboBox(self)
        self.voice_combo.addItems(voice_mapping.keys())  # Добавляем отображаемые названия голосов
        self.voice_combo.setStyleSheet(self.get_combo_box_style())

        # Устанавливаем текущий выбранный голос
        current_voice = get_selected_voice()
        for display_name, voice_id in voice_mapping.items():
            if voice_id == current_voice:
                self.voice_combo.setCurrentText(display_name)
                break

        layout.addWidget(self.voice_combo)

        # Кнопка для сохранения выбора голоса
        self.save_button = QPushButton("Сохранить выбор", self)
        self.save_button.setStyleSheet(self.get_button_style())
        self.save_button.clicked.connect(self.save_voice_choice)
        layout.addWidget(self.save_button)

        # Кнопка для прослушивания выбранного голоса
        self.listen_button = QPushButton("Прослушать голос", self)
        self.listen_button.setStyleSheet(self.get_button_style())
        self.listen_button.clicked.connect(self.listen_to_voice)
        layout.addWidget(self.listen_button)

        self.setLayout(layout)

    def save_voice_choice(self):
        # Получаем выбранное отображаемое имя
        selected_display_name = self.voice_combo.currentText()
        # Определяем реальный идентификатор голоса
        selected_voice = voice_mapping[selected_display_name]
        save_selected_voice(selected_voice)  # Сохраняем реальный идентификатор голоса
        show_custom_message("Успех", f"Голос '{selected_display_name}' выбран.")
        self.close()

    def listen_to_voice(self):
        # Получаем выбранное отображаемое имя
        selected_display_name = self.voice_combo.currentText()
        # Определяем реальный идентификатор голоса
        selected_voice = voice_mapping[selected_display_name]
        # Воспроизводим тестовую фразу с выбранным голосом
        sample_text = "Здравствуйте, если выберите меня, то я буду звучать так"  # Пример текста
        try:
            speaker_silero(sample_text, selected_voice)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось воспроизвести голос: {str(e)}")

    def get_button_style(self):
        return """
        QPushButton {
            background-color: #6969B3;  /* Синий цвет */
            color: white;
            padding: 10px;
            font-size: 18px;
            text-align: center;
            border: none;
            width: 200px;
            height: 50px;
            border-radius: 25px;
        }
        QPushButton:hover {
            background-color: #7A7AC1;  /* Более светлый синий при наведении */
        }
        """

    def get_combo_box_style(self):
        return """
        QComboBox {
            background-color: #333333;
            color: white;
            padding: 5px;
            font-size: 18px;
            border-radius: 10px;
        }
        QComboBox:hover {
            background-color: #555555;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #333333;
            color: white;
            selection-background-color: #555555;
            selection-color: white;
        }
        """
    
# Основное окно настроек
class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Настройки")
        self.setGeometry(100, 100, 500, 300)
        self.setStyleSheet("background-color: #25171A;")  # Основной фон окна

        layout = QVBoxLayout()

        # Кнопка для создания команды запуска файла
        self.create_command_button = QPushButton("Создать команду запуска файла", self)
        self.create_command_button.setStyleSheet(self.get_button_style())
        self.create_command_button.clicked.connect(self.open_create_command_window)
        layout.addWidget(self.create_command_button)

        # Кнопка для выбора голоса ассистента
        self.choose_voice_button = QPushButton("Выбрать голос", self)
        self.choose_voice_button.setStyleSheet(self.get_button_style())
        self.choose_voice_button.clicked.connect(self.open_choose_voice_window)
        layout.addWidget(self.choose_voice_button)

        self.amplitude_button = QPushButton("Шум микрофона", self)
        self.amplitude_button.setStyleSheet(self.get_button_style())
        self.amplitude_button.clicked.connect(self.open_amplitude_window)
        layout.addWidget(self.amplitude_button)

        self.setLayout(layout)

    def open_amplitude_window(self):
        self.amplitude_window = AmplitudeWindow()  # Создаем окно с настройкой амплитуды
        self.amplitude_window.show()  # Отображаем окно

    def get_amplitude_threshold(self):
        return load_amplitude_threshold()

    def update_amplitude_threshold(self, value):
        save_amplitude_threshold(value)

    def open_create_command_window(self):
        self.create_command_window = CreateCommandWindow()
        self.create_command_window.show()

    def open_choose_voice_window(self):
        self.choose_voice_window = ChooseVoiceWindow()
        self.choose_voice_window.show()

    def get_button_style(self):
        return """
        QPushButton {
            background-color: #6969B3;  /* Синий цвет */
            color: white;
            padding: 10px;
            font-size: 18px;
            text-align: center;
            border: none;
            width: 200px;
            height: 50px;
            border-radius: 25px;
        }
        QPushButton:hover {
            background-color: #7A7AC1;  /* Более светлый синий при наведении */
        }
        """

class AmplitudeWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Настройка амплитуды звука")
        self.setGeometry(100, 100, 400, 200)
        self.setStyleSheet("background-color: #25171A;")  # Основной фон окна

        layout = QVBoxLayout()

        # Лейбл для отображения текущего значения амплитуды
        self.amplitude_label = QLabel("Порог шума микрофона")
        self.amplitude_label.setStyleSheet("color: white; font-size: 16px;")
        layout.addWidget(self.amplitude_label)

        # Слайдер для настройки амплитуды
        self.amplitude_slider = QSlider(Qt.Orientation.Horizontal)
        self.amplitude_slider.setRange(0, 1000)  # Установите нужный диапазон
        self.amplitude_slider.setValue(self.get_amplitude_threshold())
        self.amplitude_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #444444;
                height: 10px;
            }
            QSlider::handle:horizontal {
                background: #6969B3;
                border: 2px solid white;
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
        """)
        self.amplitude_slider.valueChanged.connect(self.update_amplitude_threshold)
        layout.addWidget(self.amplitude_slider)

        # Лейбл для отображения текущего значения слайдера
        self.amplitude_value_label = QLabel(str(self.get_amplitude_threshold()))
        self.amplitude_value_label.setStyleSheet("color: white; font-size: 14px;")
        self.amplitude_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.amplitude_value_label)

        # Подключаем изменение значения слайдера к отображению
        self.amplitude_slider.valueChanged.connect(lambda value: self.amplitude_value_label.setText(str(value)))

        # Поле для ручного ввода значения амплитуды
        self.amplitude_input = QLineEdit(self)
        self.amplitude_input.setText(str(self.get_amplitude_threshold()))
        self.amplitude_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                padding: 5px;
                font-size: 16px;
                border-radius: 10px;
            }
        """)
        self.amplitude_input.setValidator(QIntValidator(0, 1000))  # Ввод только чисел
        layout.addWidget(self.amplitude_input)

        # Обновляем значение слайдера при ручном вводе
        self.amplitude_input.textChanged.connect(self.update_slider_from_input)

        # Кнопка для сохранения амплитуды
        self.save_button = QPushButton("Сохранить", self)
        self.save_button.setStyleSheet(self.get_button_style())
        self.save_button.clicked.connect(self.save_amplitude_threshold)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def update_slider_from_input(self):
        """Обновляет положение слайдера в зависимости от введенного значения"""
        try:
            value = int(self.amplitude_input.text())
            self.amplitude_slider.setValue(value)
        except ValueError:
            pass  # Игнорируем некорректный ввод

    def get_amplitude_threshold(self):
        return load_amplitude_threshold()

    def update_amplitude_threshold(self, value):
        """Обновляет значение амплитуды при изменении слайдера"""
        self.amplitude_value_label.setText(str(value))
        self.amplitude_input.setText(str(value))

    def save_amplitude_threshold(self):
        """Сохраняет текущее значение амплитуды"""
        value = self.amplitude_slider.value()
        save_amplitude_threshold(value)
        show_custom_message("Успех", f"Значение амплитуды сохранено: {value}")
        self.close()

    def get_button_style(self):
        return """
        QPushButton {
            background-color: #6969B3;  /* Синий цвет */
            color: white;
            padding: 10px;
            font-size: 18px;
            text-align: center;
            border: none;
            width: 200px;
            height: 50px;
            border-radius: 25px;
        }
        QPushButton:hover {
            background-color: #7A7AC1;  /* Более светлый синий при наведении */
        }
        """
