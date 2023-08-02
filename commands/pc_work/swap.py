import subprocess
import voice

def swap_language():
    subprocess.run([r'C:\Users\Nekon\project_GS\myapp\commands\exe\swap.exe'])
    voice.speaker_silero("Язык поменяла")