# llama_worker.py
import sys
import os
import logging

# Добавляем текущую директорию в sys.path
sys.path.insert(0, os.getcwd())

from llama1 import get_model, start_llama_dialogue

# Настройка логирования: отладка в файл, а в stdout – только финальный ответ
logging.basicConfig(level=logging.DEBUG, filename="llama_worker_debug.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")
logging.debug("Используемый интерпретатор: %s", sys.executable)

def main():
    if not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    else:
        if len(sys.argv) < 2:
            print("Usage: python llama_worker.py <prompt>")
            sys.exit(1)
        prompt = sys.argv[1]
    logging.debug("[llama_worker] Получен prompt: '%s'", prompt)
    
    try:
        answer = start_llama_dialogue(prompt)
        # В stdout выводим только финальный ответ
        print(answer)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
