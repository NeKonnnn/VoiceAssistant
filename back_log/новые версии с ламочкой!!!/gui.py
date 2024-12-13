import os
import sys
import tkinter as tk
from tkinter import ttk
from threading import Thread

from PIL import Image, ImageTk

from microphone import recognize_wheel
from chatGPT import write_history, new_dialogue


class Application(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        self.title("Голосовой помощник")
        self.resizable(True, True)

        # Устанавливаем окно в максимизированное состояние
        self.state('zoomed')

        self.icon_size = (128, 128)  # Размер иконок

        self.prepare_img()
        self.create_widgets()

        self.check_env_vars()

    def create_widgets(self):
        # Создаем Frame для обработки изменения размера фона и размещения виджетов
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)

        # Создаем Canvas для фонового изображения
        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, side='left')

        # Загрузка и установка фонового изображения
        self.background_image = Image.open('icons/background.jpg')
        self.bg_image_tk = ImageTk.PhotoImage(self.background_image)
        self.bg_image_id = self.canvas.create_image(0, 0, anchor='nw', image=self.bg_image_tk)

        # Создание фрейма для кнопок на Canvas
        self.button_frame = tk.Frame(self.canvas, bg='', highlightthickness=0)  # Убираем белый фон
        self.canvas.create_window(30, 30, anchor='nw', window=self.button_frame)

        # Кнопка ассистента
        self.assistant_label = ttk.Label(self.button_frame, image=self.assistant_img_frames[0], background="")  # прозрачный фон
        self.assistant_label.pack(pady=0)  # Убираем отступы
        self.assistant_label.bind("<Button-1>", self.run_assistant)
        self.assistant_label.bind("<Enter>", lambda e: self.assistant_label.configure(cursor="hand2"))

        # Кнопка ChatGPT
        self.gpt_label = ttk.Label(self.button_frame, image=self.gpt_img_frames[0], background="")  # прозрачный фон
        self.gpt_label.pack(pady=0)  # Убираем отступы
        self.gpt_label.bind("<Button-1>", self.run_gpt)
        self.gpt_label.bind("<Enter>", lambda e: self.gpt_label.configure(cursor="hand2"))

        # Кнопка обновления диалога
        self.gpt_clear_label = ttk.Label(self.button_frame, image=self.refresh_img_frames[0], background="")  # прозрачный фон
        self.gpt_clear_label.pack(pady=0)  # Убираем отступы
        self.gpt_clear_label.bind("<Button-1>", self.clear_gpt)
        self.gpt_clear_label.bind("<Enter>", lambda e: self.gpt_clear_label.configure(cursor="hand2"))

        # Кнопка выхода
        self.exit_label = ttk.Label(self.button_frame, image=self.exit_img_frames[0], background="")  # прозрачный фон
        self.exit_label.pack(pady=0)  # Убираем отступы
        self.exit_label.bind("<Button-1>", self.exit)
        self.exit_label.bind("<Enter>", lambda e: self.exit_label.configure(cursor="hand2"))

        # Привязываем событие изменения размера окна
        self.bind('<Configure>', self.on_resize)


    def on_resize(self, event):
        # Изменяем размер фонового изображения под размер окна
        self.update_idletasks()
        new_width = self.canvas.winfo_width()
        new_height = self.canvas.winfo_height()

        resized_bg = self.background_image.resize((new_width, new_height), Image.LANCZOS)
        self.bg_image_tk = ImageTk.PhotoImage(resized_bg)
        self.canvas.itemconfig(self.bg_image_id, image=self.bg_image_tk)

        # Обновляем размер Canvas
        self.canvas.config(width=new_width, height=new_height)

    def read_gif_frames(self, gif, size=None):
        frames = []
        for frame in range(0, getattr(gif, 'n_frames', 1)):
            gif.seek(frame)
            frame_image = gif.copy()
            if size is not None:
                frame_image = frame_image.resize(size, Image.LANCZOS)
            frames.append(ImageTk.PhotoImage(frame_image))
        return frames

    def prepare_img(self):
        # Загрузка иконок с изменением размера
        image = Image.open("icons/microphone.gif")
        self.assistant_img_frames = self.read_gif_frames(image, self.icon_size)

        image = Image.open("icons/chatgpt.gif")
        self.gpt_img_frames = self.read_gif_frames(image, self.icon_size)

        image = Image.open("icons/exit.gif")
        self.exit_img_frames = self.read_gif_frames(image, self.icon_size)

        image = Image.open("icons/refresh.gif")
        self.refresh_img_frames = self.read_gif_frames(image, self.icon_size)

    def animate_mic(self, frame_index=0):
        self.assistant_label.configure(image=self.assistant_img_frames[frame_index])
        self.wheel_mic_animation = self.after(100, self.animate_mic,
                                              (frame_index + 1) % len(self.assistant_img_frames))

    def animate_gpt(self, frame_index=0):
        self.gpt_label.configure(image=self.gpt_img_frames[frame_index])
        self.wheel_gpt_animation = self.after(100, self.animate_gpt,
                                              (frame_index + 1) % len(self.gpt_img_frames))

    def animate_exit(self, frame_index=0):
        self.exit_label.configure(image=self.exit_img_frames[frame_index])
        self.wheel_exit_animation = self.after(100, self.animate_exit,
                                               (frame_index + 1) % len(self.exit_img_frames))

    def animate_refresh(self, frame_index=0):
        self.gpt_clear_label.configure(image=self.refresh_img_frames[frame_index])
        self.wheel_refresh_animation = self.after(100, self.animate_refresh,
                                                  (frame_index + 1) % len(self.refresh_img_frames))

    def stop_mic_animation(self):
        if hasattr(self, 'wheel_mic_animation') and self.wheel_mic_animation is not None:
            self.after_cancel(self.wheel_mic_animation)
            self.wheel_mic_animation = None

    def stop_gpt_animation(self):
        if hasattr(self, 'wheel_gpt_animation') and self.wheel_gpt_animation is not None:
            self.after_cancel(self.wheel_gpt_animation)
            self.wheel_gpt_animation = None

    def stop_exit_animation(self):
        if hasattr(self, 'wheel_exit_animation') and self.wheel_exit_animation is not None:
            self.after_cancel(self.wheel_exit_animation)
            self.wheel_exit_animation = None

    def stop_refresh_animation(self):
        if hasattr(self, 'wheel_refresh_animation') and self.wheel_refresh_animation is not None:
            self.after_cancel(self.wheel_refresh_animation)
            self.wheel_refresh_animation = None

    def run_assistant(self, event=None):
        if int(os.getenv('MIC', '0')):

            os.environ.update(MIC='0')
            self.stop_mic_animation()
            self.assistant_label['image'] = self.assistant_img_frames[0]

            if int(os.getenv('CHATGPT', '0')):
                os.environ.update(CHATGPT='0')
                self.stop_gpt_animation()
                self.gpt_label['image'] = self.gpt_img_frames[0]

                self.stop_exit_animation()
                self.exit_label['image'] = self.exit_img_frames[0]

                self.stop_refresh_animation()
                self.gpt_clear_label['image'] = self.refresh_img_frames[0]

        else:
            os.environ.update(MIC='1')
            self.animate_mic()
            p1 = Thread(target=recognize_wheel, daemon=True)
            p1.start()

    def check_env_vars(self):
        '''
        Каждые 5 секунд проверяем, если появился диалог с GPT,
        то обновляем состояние интерфейса.
        '''
        dialogue_status = os.environ.get('NEW_DIALOGUE', '0')
        if not int(dialogue_status):
            self.gpt_clear_label['image'] = self.refresh_img_frames[0]

        self.after(5000, self.check_env_vars)

    def run_gpt(self, event):
        if int(os.getenv('CHATGPT', '0')):

            os.environ.update(CHATGPT='0')
            self.stop_gpt_animation()
            self.gpt_label['image'] = self.gpt_img_frames[0]

            self.stop_exit_animation()
            self.exit_label['image'] = self.exit_img_frames[0]

            self.stop_refresh_animation()
            self.gpt_clear_label['image'] = self.refresh_img_frames[0]

        elif not int(os.getenv('MIC', '0')):
            return

        else:
            os.environ.update(CHATGPT='1')
            self.animate_gpt()

    def clear_gpt(self, event):
        new_dialogue()
        os.environ.update(NEW_DIALOGUE='1')
        self.gpt_clear_label['image'] = self.refresh_img_frames[0]

    def exit(self, event):
        write_history()
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
