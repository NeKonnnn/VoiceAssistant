import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def load_local_model():
    # Локальный путь к загруженной модели
    model_path = "./local_model_cache"

    # Загрузка токенизатора и модели из локальной директории
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16)

    print("Модель и токенизатор успешно загружены локально.")

    return tokenizer, model

if __name__ == "__main__":
    tokenizer, model = load_local_model()

