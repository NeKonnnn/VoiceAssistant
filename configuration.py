import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SETTINGS = {
    'LANG': 'ru',
    'OPENAI_API_KEY': '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',
    'CHATGPT': '0',
    'MIC': '0',
    'NEW_DIALOGUE': '1',
    'PICOVOICE_TOKEN': 'EZ/Qd05mqqfC0Vfc+4fyRZfweMDpIgfqaNgwOEB4eJR96oij7gPKag==',
    'KEYWORD_PATH': [os.path.join(BASE_DIR, "voices", "Crystal.ppn")]
    }