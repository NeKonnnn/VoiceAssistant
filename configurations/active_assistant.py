import time
import threading

# Глобальная переменная, показывающая активность ассистента
assistant_active = False

# Время последней активности
last_activity_time = None

# Lock для синхронизации доступа к assistant_active
assistant_active_lock = threading.Lock()

# Время ожидания (в секундах)
timeout = 30

def track_activity():
    global assistant_active, last_activity_time
    while True:
        with assistant_active_lock:
            if assistant_active and time.time() - last_activity_time > timeout:
                assistant_active = False
                print("Ассистент заснул")
        time.sleep(5)

def activate_assistant():
    print("Activating assistant")
    global assistant_active, last_activity_time
    assistant_active = True
    last_activity_time = time.time()
    print("Ассистент активирован")

# Запуск потока, отслеживающего активность
tracking_thread = threading.Thread(target=track_activity)
tracking_thread.start()