from configurations.listen_to_task import listen_to_task
import voice

def add_to_backlog():
    voice.speaker_silero("Пожалуйста, назовите задачу, которую вы хотите занести в бэклог.")
    task = listen_to_task()
    if task is not None:
        with open("C:/Users/Nekon/project_GS/myapp/back_log/backlog.txt", "a", encoding='utf-8') as backlog_file:
            backlog_file.write("❗️ " + task + "\n")  # Добавляем символ ❗️ перед задачей
        voice.speaker_silero("Задача успешно добавлена в бэклог.")
    else:
        voice.speaker_silero("Не удалось распознать задачу. Попробуйте еще раз.")