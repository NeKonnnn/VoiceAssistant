import sys
import os
import subprocess
import voice

def call_llama_via_subprocess(prompt):
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        result = subprocess.run(
            [sys.executable, "llama_worker.py", prompt],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            env=env,
            check=True
        )
        output = result.stdout.strip()
        # Фильтруем вывод: выбираем текст после последнего появления префикса "Ответ от LLaMA:"
        if "Ответ от LLaMA:" in output:
            final_answer = output.split("Ответ от LLaMA:")[-1].strip()
        else:
            final_answer = output
        print(f"[ASYNC] Ответ нейронки: {final_answer}")
        # Вместо вызова speaker_silero, вызываем функцию для частичной озвучки:
        voice.speaker_silero_chunks(final_answer)
    except subprocess.CalledProcessError as e:
        print(f"[ASYNC] Ошибка при вызове llama_worker.py: {e.stderr}")
        voice.speaker_silero("Произошла ошибка при получении ответа от нейронки.")