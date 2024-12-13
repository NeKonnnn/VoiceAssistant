import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import subprocess
import string

# Настройка начального диалога
base_dialogue = [
    {'role': 'system', 'content': 'Ты дружелюбный и полезный ассистент.'},
    {'role': 'user', 'content': 'Привет, можем поговорить?'},
    {'role': 'assistant', 'content': 'Конечно, о чем бы ты хотел поговорить?'}
]

# История диалога
messages = base_dialogue.copy()

# Локальный путь к загруженной модели
model_path = "./local_model_cache"

# Загрузка модели и токенизатора из локальной директории
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map="auto")

def preprocess_text(text):
    """Предварительная обработка текста перед отправкой в модель."""
    return text.lower()

def start_llama_dialogue(text):
    """Функция для начала диалога с LLaMA."""
    try:
        # Добавляем новый запрос в историю
        messages.append({'role': 'user', 'content': text})
        
        # Форматирование истории для подачи в модель
        input_text = " ".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        inputs = tokenizer(preprocess_text(input_text), return_tensors="pt").to("cuda")

        # Генерация ответа модели
        outputs = model.generate(**inputs, max_length=200, temperature=0.7)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Добавляем ответ в историю
        messages.append({'role': 'assistant', 'content': response})

        # Проверяем и очищаем текст ответа перед озвучкой
        response = clear_text(response)

        return response

    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

def write_history():
    """Сохраняет историю диалога в файл перед его очисткой."""
    len_base_dialogue = len(base_dialogue)

    if len(messages) == len_base_dialogue:
        return
    
    file_name = messages[len_base_dialogue]['content']
    file_name = remove_punctuation(file_name)

    if len(file_name) > 50:
        file_name = file_name[:51]

    with open(f'temporary_files/{file_name}.txt', 'w', encoding='utf-8') as r:
        for i in messages[len_base_dialogue:]:
            r.writelines(i['content'] + '\n')

def new_dialogue():
    """Очищает историю текущего диалога."""
    write_history()
    messages.clear()
    messages.extend(base_dialogue)

def clear_text(response):
    """Очищает текст ответа от ненужных символов перед озвучкой."""
    table = str.maketrans({'`': '', '(': '', ')': ' ', '@': 'at ', '_': ' '})
    response = response.translate(table)
    return response

def remove_punctuation(file_name):
    """Удаляет всю пунктуацию из строки."""
    translator = str.maketrans('', '', string.punctuation)
    return file_name.translate(translator)

def check_response(response):
    """Отделяет код от текста в ответе LLaMA, если есть код."""
    if '```' in response:
        parts = response.split('```')
        text = ''
        code = ''

        count = 1
        for i in parts:
            if count % 2 == 0:
                code += f'{i} \n'
            else:
                text += f'{i} \n'
            count += 1

        save_code(code)
        response = clear_text(text)
        return response
    else:
        response = clear_text(response)
        return response

def save_code(code):
    """Сохраняет код в файл для последующего просмотра."""
    with open('temporary_files/code.py', 'w', encoding='utf-8') as r:
        r.write(code)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    code_path = os.path.join(dir_path, 'temporary_files', 'code.py')

    subprocess.Popen(['python', '-m', 'idlelib', '-e', code_path])
