from datetime import datetime
from num2words import num2words
import voice

def tell_time():
    now = datetime.now()
    current_hour, current_minute, current_second = now.hour, now.minute, now.second
    current_hour_word = num2words(current_hour, lang='ru')
    current_minute_word = num2words(current_minute, lang='ru')
    current_second_word = num2words(current_second, lang='ru')
    voice.speaker_silero(f"Текущее время: {current_hour_word} часов, {current_minute_word} минут, {current_second_word} секунд.")