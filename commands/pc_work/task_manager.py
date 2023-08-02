import subprocess
import voice

def task_manager():
    subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\task_manager.exe'])
    voice.speaker_silero("Открыла диспетчер задач, сэр")