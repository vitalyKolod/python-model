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
EFFECT_KEYWORDS = ["ветер", "дожд", "снег", "дым", "огонь", "пыль", "листь"]
COSTUME_HINTS = ["повседневн", "делов", "форм", "военн", "нарядн", "рабоч"]
MAKEUP_HINTS = ["гр", "макияж", "грима", "кровь", "пыль", "пот"]

# Распознавание имён (для эвристики)
NAME_RE = re.compile(r"\b[А-ЯЁ][а-яё]{2,}\b")


# -----------------------------
# Эвристические функции
# -----------------------------
def extract_characters_heuristic(scene_text: str) -> List[str]:
    candidates = NAME_RE.findall(scene_text)
    exclude = ["СЦЕНА", "ИНТ", "ЭКСТ", "ДЕНЬ", "НОЧЬ", "УТРО", "ВЕЧЕР"]
    names = sorted(set([c.title() for c in candidates if c.upper() not in exclude]))
    return names


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
    """
    Анализ одной сцены. Использует spaCy, если модель доступна, иначе эвристику.
    Возвращает словарь с категориями:
    Персонажи, Массовка, Реквизит, Грим, Костюмы, Эффекты
    """
    result = {
        "Персонажи": [],
        "Массовка": [],
        "Реквизит": [],
        "Грим": guess_makeup(scene_text),
        "Костюмы": guess_costume(scene_text),
        "Эффекты": [],
    }

    if nlp:
        # ML-анализ через spaCy
        doc = nlp(scene_text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                result["Персонажи"].append(ent.text)
            elif ent.label_ == "MASSOVKA":
                result["Массовка"].append(ent.text)
            elif ent.label_ == "PROP":
                result["Реквизит"].append(ent.text)
            elif ent.label_ == "EFFECT":
                result["Эффекты"].append(ent.text)

        # убираем дубликаты
        for key in ["Персонажи", "Массовка", "Реквизит", "Эффекты"]:
            result[key] = list(set(result[key]))
    else:
        # Эвристический fallback
        result["Персонажи"] = extract_characters_heuristic(scene_text)
        result["Массовка"] = extract_mass_scene(scene_text)
        result["Реквизит"] = extract_props(scene_text)
        result["Эффекты"] = extract_effects(scene_text)

    return result

