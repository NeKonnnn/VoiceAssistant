# from langchain_ollama import OllamaLLM
# from langchain_core.prompts import ChatPromptTemplate

# template = """
# Answer the question below.

# Here is the conversation history: {context}

# Question: {question}

# Answer:
# """

# model = OllamaLLM(model='llama3')
# prompt = ChatPromptTemplate.from_template(template)
# chain = prompt | model

# def handle_conversation():
#     context = ''
#     print('Welcome to the AI ChatBot! Type "exit" to quit.')
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() == 'exit':
#             break

#         result = chain.invoke({'context': context, 'question': user_input})
#         print('Bot: 'result)
#         context += f"\nUser: {user_input}\nAI: {result}"

# if __name__ == "__main__":
#     handle_conversation()


from huggingface_hub import login

# Замените "your_token_here" на ваш токен
login("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")

import transformers
import torch
import os

def handle_conversation():
    model_id = "mistralai/Ministral-8B-Instruct-2410"
    save_directory = "./saved_mistral_model"  # Путь для сохранения модели

    # Проверяем, существует ли локальная копия модели
    if not os.path.exists(save_directory):
        print("Модель не найдена локально. Загружаю с Hugging Face и сохраняю...")
        
        # Загрузка модели и токенизатора с Hugging Face
        model = transformers.AutoModelForCausalLM.from_pretrained(model_id, torch_dtype="auto", device_map="auto")
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)

        # Сохраняем модель и токенизатор локально
        model.save_pretrained(save_directory)
        tokenizer.save_pretrained(save_directory)
        print(f"Модель сохранена в {save_directory}.")
    else:
        print("Загружаю модель из локального хранилища...")
        
        # Загрузка модели и токенизатора из локального хранилища
        model = transformers.AutoModelForCausalLM.from_pretrained(save_directory, torch_dtype="auto", device_map="auto")
        tokenizer = transformers.AutoTokenizer.from_pretrained(save_directory)

    # Инициализация пайплайна
    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map="auto",
    )

    # Начальная инструкция для системы
    messages = [
        {"role": "system", "content": "You are a helpful assistant who always responds politely."}
    ]
    print('Welcome to the AI ChatBot! Type "exit" to quit.')

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        # Добавляем пользовательское сообщение
        messages.append({"role": "user", "content": user_input})

        # Генерация ответа
        outputs = pipeline(
            messages,
            max_new_tokens=256,  # Количество генерируемых токенов
        )

        # Получаем сгенерированный текст
        response = outputs[0]["generated_text"]

        # Печатаем ответ и обновляем историю сообщений
        print(f"Bot: {response}")
        messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    handle_conversation()




