import subprocess
import voice

def sleep_mode():
    voice.speaker_silero("Активирую спящий режим")
    subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\sleep_mode.exe'])
    
def lock_mode():
    voice.speaker_silero("Включаю безопасный режим")
    subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\lock.exe'])