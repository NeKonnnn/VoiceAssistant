import subprocess
import voice

def clear_trash():
    subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\trash.exe'])
    voice.speaker_silero("Корзина очищена, сэр")