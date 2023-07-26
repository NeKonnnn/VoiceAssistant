import subprocess


import voice
    
def steam():
    #Указываем путь до стим
    try:
        subprocess.Popen(r'E:\Programms\steam\steam.exe')
    except:
        voice.speaker('Путь к файлу не найден, проверьте, правильный ли он')
        
        
steam()