import re
from typing import Dict, List
import spacy

# -----------------------------
# Настройка spaCy
# -----------------------------
try:
    nlp = spacy.load("parser/ner_model")  # путь к обученной модели
except:
    print("ML-модель spaCy не найдена. Используйте train_model.py для обучения.")
    nlp = None

# -----------------------------
# Эвристические словари
# -----------------------------
MASS_SCENE_KEYWORDS = ["толпа", "прохож", "пешеход", "люд", "массовка", "музыкант"]
PROP_KEYWORDS = ["автомобиль", "машин", "папк", "телефон", "чашк", "книга", "саксофон", "чемодан"]
EFFECT_KEYWORDS = ["ветер", "дождь", "снег", "дым", "огонь", "пыль", "листь"]
COSTUME_HINTS = ["повседневн", "делов", "форм", "военн", "нарядн", "рабоч"]
MAKEUP_HINTS = ["гр", "макияж", "грима", "кровь", "пыль", "пот"]

# -----------------------------
# Регулярка для эвристики имён
# -----------------------------
NAME_RE = re.compile(r"\b[А-ЯЁ][а-яё]{2,}\b")

# -----------------------------
# Фильтры для очистки персонажей
# -----------------------------
RAW_IGNORE = {
    "и", "но", "то", "кто", "уже", "как", "что", "где", "улыбаясь",
    "руках", "стоит", "держит", "комнате", "с", "по", "а", "в"
}

def clean_character(name: str) -> str | None:
    name = name.strip()

    if len(name) < 2:
        return None

    if name.lower() in RAW_IGNORE:
        return None

    if any(name.lower().endswith(suffix) for suffix in ["ясь", "вши", "ши", "ами", "ыми"]):
        return None

    if not re.match(r"^[А-ЯЁа-яё\-]+$", name):
        return None

    return name.capitalize()


def extract_characters_ml(doc):
    chars = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            cleaned = clean_character(ent.text)
            if cleaned:
                chars.append(cleaned)

    return list(set(chars))  # уникальные


# -----------------------------
# Эвристические fallback-функции
# -----------------------------
def extract_characters_heuristic(scene_text: str) -> List[str]:
    candidates = NAME_RE.findall(scene_text)
    exclude = ["СЦЕНА", "ИНТ", "ЭКСТ", "ДЕНЬ", "НОЧЬ", "УТРО", "ВЕЧЕР"]
    cleaned = []

    for c in candidates:
        if c.upper() not in exclude:
            fixed = clean_character(c)
            if fixed:
                cleaned.append(fixed)

    return sorted(set(cleaned))


def extract_mass_scene(scene_text: str) -> List[str]:
    found = []
    for kw in MASS_SCENE_KEYWORDS:
        m = re.findall(rf"\b{kw}\w*", scene_text.lower())
        found.extend(m)
    return sorted(set(found))


def extract_props(scene_text: str) -> List[str]:
    found = []
    for kw in PROP_KEYWORDS:
        m = re.findall(rf"\b{kw}\w*", scene_text.lower())
        found.extend(m)
    return sorted(set(found))


def extract_effects(scene_text: str) -> List[str]:
    found = []
    for kw in EFFECT_KEYWORDS:
        m = re.findall(rf"\b{kw}\w*", scene_text.lower())
        found.extend(m)
    return sorted(set(found))


def guess_costume(scene_text: str) -> str:
    for kw in COSTUME_HINTS:
        if kw in scene_text.lower():
            return "специфические"
    return "повседневные"


def guess_makeup(scene_text: str) -> str:
    for kw in MAKEUP_HINTS:
        if kw in scene_text.lower():
            return "особый"
    return "стандартный"


# -----------------------------
# Основная функция анализа сцены
# -----------------------------
def analyze_scene(scene_text: str) -> Dict[str, List[str] | str]:
    result = {
        "Персонажи": [],
        "Массовка": [],
        "Реквизит": [],
        "Грим": guess_makeup(scene_text),
        "Костюмы": guess_costume(scene_text),
        "Эффекты": [],
    }

    if nlp:
        doc = nlp(scene_text)

        # Улучшенное выделение персонажей
        result["Персонажи"] = extract_characters_ml(doc)

        # Остальные категории
        for ent in doc.ents:
            if ent.label_ == "MASSOVKA":
                result["Массовка"].append(ent.text)
            elif ent.label_ == "PROP":
                result["Реквизит"].append(ent.text)
            elif ent.label_ == "EFFECT":
                result["Эффекты"].append(ent.text)

        for key in ["Массовка", "Реквизит", "Эффекты"]:
            result[key] = list(set(result[key]))  # Уникальные
    else:
        # Fallback — если модель spaCy не загружена
        result["Персонажи"] = extract_characters_heuristic(scene_text)
        result["Массовка"] = extract_mass_scene(scene_text)
        result["Реквизит"] = extract_props(scene_text)
        result["Эффекты"] = extract_effects(scene_text)

    return result
