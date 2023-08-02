import subprocess
import voice

def screenshot():
    subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\screenshot.exe'])
    voice.speaker_silero("Скриншот готов, сэр")