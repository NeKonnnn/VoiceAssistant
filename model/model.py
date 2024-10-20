import re
import pickle
import numpy as np
import torch
from collections import Counter
from imblearn.over_sampling import SMOTE
from transformers import AutoTokenizer, AutoModel, pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
import os
import sys

# Добавляем путь к корневой директории проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import words  # Импортируем ваш словарь команд

# Функция для проверки баланса классов
def check_class_balance(labels, title="Распределение классов"):
    class_counts = Counter(labels)
    print(f"\n{title}:")
    for label, count in class_counts.items():
        print(f"Класс '{label}': {count} примеров")

# Предобработка текста: нижний регистр и удаление лишних символов
def preprocess_text(text):
    text = text.lower()  # Приведение к нижнему регистру
    text = re.sub(r'[^а-яё\s]', '', text)  # Удаление всех символов, кроме русских букв и пробелов
    text = re.sub(r'\s+', ' ', text).strip()  # Удаление лишних пробелов
    return text

# Загрузка предобученного токенизатора и модели RuBERT
tokenizer = AutoTokenizer.from_pretrained('cointegrated/rubert-tiny')
model = AutoModel.from_pretrained('cointegrated/rubert-tiny')

# Загрузка модели для перефразирования
paraphraser = pipeline('text2text-generation', model='cointegrated/rut5-base-paraphraser')

# Функция для аугментации команд
def augment_command(command, num_variants=3):
    variants = paraphraser(command, num_return_sequences=num_variants, do_sample=True)
    return [variant['generated_text'] for variant in variants]

# Функция для получения вектора текста с помощью RuBERT
def encode_text(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        # Используем pooler_output для более репрезентативного вектора предложения
        sentence_embedding = outputs.pooler_output.squeeze().numpy()
    return sentence_embedding

# Предобработка команд, аугментация и получение эмбеддингов
def prepare_data():
    commands = list(words.data_set.keys())
    labels = list(words.data_set.values())
    
    augmented_commands = []
    augmented_labels = []
    
    # Аугментация данных
    for command, label in zip(commands, labels):
        preprocessed_command = preprocess_text(command)
        augmented_commands.append(preprocessed_command)
        augmented_labels.append(label)
        
        # Генерируем синонимичные команды
        augmented_variants = augment_command(preprocessed_command)
        augmented_commands.extend(augmented_variants)
        augmented_labels.extend([label] * len(augmented_variants))

    vectors = np.array([encode_text(cmd) for cmd in augmented_commands])
    return vectors, augmented_labels

# Обучение модели и сохранение в .pkl
def train_and_save_model():
    vectors, labels = prepare_data()
    # Проверка баланса классов в исходных данных
    check_class_balance(labels, "Баланс классов в исходных данных")
    X_train, X_test, y_train, y_test = train_test_split(vectors, labels, test_size=0.2, random_state=42)

    # Проверка баланса классов в тренировочном наборе до применения SMOTE
    check_class_balance(y_train, "Баланс классов до применения SMOTE")
    
    # Применение SMOTE для балансировки классов в обучающем наборе
    smote = SMOTE(random_state=42, k_neighbors=1)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    # Проверка баланса классов после применения SMOTE
    check_class_balance(y_train_resampled, "Баланс классов после применения SMOTE")
    
    # Настройка параметров для GridSearchCV
    param_grid = {
        'C': [0.1, 1.0, 10.0],  # Регуляризация для логистической регрессии
        'penalty': ['l2', 'l1'],
        'solver': ['liblinear', 'saga'],
        'max_iter': [100, 200, 500]
    }
    
    grid_search = GridSearchCV(
        LogisticRegression(class_weight='balanced', random_state=42),
        param_grid,
        cv=10,
        scoring='accuracy',
        n_jobs=-1
    )
    # ----- если зхочу использовать SGDCClassifier ------
    # param_grid = {
    #     'loss': ['log_loss', 'hinge', 'modified_huber'],
    #     'learning_rate': ['constant', 'optimal', 'adaptive'],
    #     'alpha':  [0.0001, 0.001, 0.01],
    #     'penalty': ['l2', 'l1'],
    #     'max_iter': [1000, 2000]
    # }
    
    # grid_search = GridSearchCV(
    #     SGDClassifier(loss='log_loss', class_weight='balanced', random_state=42),
    #     param_grid,
    #     cv=10,
    #     scoring='accuracy',
    #     n_jobs=-1
    # )
    # ------------------------------------------------------

    # Выполняем GridSearchCV для выбора лучших гиперпараметров
    grid_search.fit(X_train_resampled, y_train_resampled)
    best_clf = grid_search.best_estimator_

    print("Лучшие параметры:", grid_search.best_params_)
    
    # Оценка качества на тренировочном наборе
    train_accuracy = accuracy_score(y_train, best_clf.predict(X_train))
    print("Качество на тренировочном наборе:", train_accuracy)
    
    # Оценка качества на тестовом наборе
    test_accuracy = accuracy_score(y_test, best_clf.predict(X_test))
    print("Качество на тестовом наборе:", test_accuracy)

    # Проверка наличия директории 'model' и создание её, если отсутствует
    model_dir = "model"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    # Сохранение модели, токенизатора и классификатора в модельной папке
    with open(os.path.join(model_dir, "model.pkl"), "wb") as f:
        pickle.dump((tokenizer, model, best_clf), f)
    print(f"Модель сохранена в '{os.path.join(model_dir, 'model.pkl')}'")

if __name__ == "__main__":
    train_and_save_model()
