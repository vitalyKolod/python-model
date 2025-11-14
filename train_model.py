import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import json
import random
from pathlib import Path
from tqdm import tqdm

# -----------------------------
# Пути
# -----------------------------
DATA_DIR = Path("data")                          # Папка с файлами .txt (JSON)
OUTPUT_MODEL_DIR = Path("parser/ner_model")      # Папка для сохранения модели

# -----------------------------
# Загружаем предобученную модель
# -----------------------------
# Перед запуском: python -m spacy download ru_core_news_md
nlp = spacy.load("ru_core_news_md")

# -----------------------------
# Создаём / получаем NER
# -----------------------------
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

# -----------------------------
# Загружаем тренировочные данные
# -----------------------------
train_data = []
for file_path in sorted(DATA_DIR.glob("*.txt")):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_data = json.load(f)
    except json.JSONDecodeError:
        print(f"⚠️ Пропущен файл (не JSON): {file_path}")
        continue

    for item in file_data:
        text = item.get("text")
        entities = item.get("entities", [])
        if not text or not entities:
            continue
        # Проверяем корректность диапазонов
        valid_entities = []
        for start, end, label in entities:
            if 0 <= start < end <= len(text):
                valid_entities.append((start, end, label))
        if valid_entities:
            train_data.append((text, {"entities": valid_entities}))

print(f"✅ Загружено {len(train_data)} примеров из {len(list(DATA_DIR.glob('*.txt')))} файлов")

if not train_data:
    raise ValueError("❌ Нет данных для обучения. Проверь содержимое папки data/")

# -----------------------------
# Регистрируем все лейблы
# -----------------------------
for _, annotations in train_data:
    for ent in annotations.get("entities", []):
        ner.add_label(ent[2])

# -----------------------------
# Обучение модели
# -----------------------------
n_iterations = 10
dropout_rate = 0.3

# Отключаем остальные пайпы (только NER)
other_pipes = [p for p in nlp.pipe_names if p != "ner"]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()

    for itn in range(1, n_iterations + 1):
        random.shuffle(train_data)
        losses = {}
        batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

        with tqdm(total=len(train_data), desc=f"Эпоха {itn}/{n_iterations}", ncols=100) as pbar:
            for batch in batches:
                examples = []
                for text, annots in batch:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annots)
                    examples.append(example)
                nlp.update(
                    examples,
                    sgd=optimizer,
                    drop=dropout_rate,
                    losses=losses,
                )
                pbar.update(len(batch))

        print(f"  🔹 Потери (loss): {losses.get('ner', 0):.4f}")

# -----------------------------
# Сохраняем модель
# -----------------------------
OUTPUT_MODEL_DIR.mkdir(parents=True, exist_ok=True)
nlp.to_disk(OUTPUT_MODEL_DIR)
print(f"\n✅ Модель обучена и сохранена в: {OUTPUT_MODEL_DIR}")
