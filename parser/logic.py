import re
from typing import Dict, List, Tuple
from pymorphy3 import MorphAnalyzer

# ============================================================
#  ИНИЦИАЛИЗАЦИЯ
# ============================================================

morph = MorphAnalyzer()

TOKEN_RE = re.compile(r"[А-Яа-яЁёA-Za-z\-]+")

def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text)


# ============================================================
#  СЛОВАРИ
# ============================================================

STOP_WORDS = {
    "и", "в", "во", "не", "что", "он", "она", "оно", "они", "а", "но", "же",
    "из", "у", "к", "по", "на", "за", "от", "до", "под", "над", "при", "для",
    "без", "или", "ли", "то", "это", "эта", "этот", "эти", "этом", "этих",
    "там", "тут", "здесь", "когда", "мы", "вы", "ты", "я", "его", "её", "ее",
    "их", "нам", "вам", "наш", "ваш", "который", "какая", "какое", "какие",
    "ну", "да", "нет", "ни", "тоже", "ещё", "еще", "бы", "уж", "сам", "сама",
    "каждый", "кто-то", "что-то", "где-то"
}

# Леммы категорий
LOCATION_LEMMAS = {
    "улица", "площадь", "кабинет", "офис", "квартира", "дом", "подъезд",
    "парк", "лес", "берег", "пляж", "комната", "кухня", "зал", "склад",
    "подвал", "коридор", "двор", "театр", "сцена", "площадка", "метро",
    "лифт", "лестница"
}

TIME_OF_DAY_LEMMAS = {"утро", "день", "вечер", "ночь", "рассвет", "закат"}

MASS_LEMMAS = {
    "толпа", "люди", "публика", "прохожий", "официант", "зритель", "гость"
}

TRANSPORT_LEMMAS = {
    "машина", "автомобиль", "автобус", "такси", "поезд", "трамвай",
    "самолет", "самолёт", "вертолет", "вертолёт", "велосипед", "мотоцикл"
}

ANIMAL_LEMMAS = {
    "кот", "кошка", "пес", "пёс", "собака", "лошадь", "птица", "голубь"
}

PROP_LEMMAS = {
    "стол", "стул", "телефон", "пистолет", "документ", "ключ", "книга",
    "бумага", "рюкзак", "портфель", "камера", "микрофон"
}

STUNT_LEMMAS = {
    "взрыв", "выстрел", "стрельба", "драка", "удар", "авария", "падение"
}

EFFECT_LEMMAS = {
    "дым", "огонь", "дождь", "снег", "ветер", "туман", "свет", "гром"
}

MAKEUP_LEMMAS = {
    "кровь", "грязь", "рана", "шрам", "синяк", "порез", "грим", "макияж"
}

COSTUME_LEMMAS = {
    "форма", "мундир", "костюм", "куртка", "платье", "униформа", "шлем"
}

BAD_CHAR_LEMMAS = {"кто", "никто", "люди", "толпа", "человек"}


# ============================================================
#  ФИЛЬТРЫ
# ============================================================

def is_good_case(parsed):
    """Берём только именительный и винительный."""
    return parsed.tag.case in {"nomn", "accs"}


def normalize_word(word: str):
    parsed = morph.parse(word)[0]
    lemma = parsed.normal_form
    pos = parsed.tag.POS or ""

    # Фильтруем падежи у существительных
    if pos == "NOUN" and not is_good_case(parsed):
        return None

    if lemma in STOP_WORDS:
        return None

    return (word, lemma, pos)


# ============================================================
#  ОБЩАЯ ФУНКЦИЯ ИЗВЛЕЧЕНИЯ
# ============================================================

def extract_by_lemmas(items, target):
    out = []
    seen = set()

    for orig, lem, pos in items:
        if lem in target and lem not in seen:
            seen.add(lem)
            out.append(orig)

    return out


# ============================================================
#  ПЕРСОНАЖИ
# ============================================================

def extract_characters(text: str) -> List[str]:
    tokens = tokenize(text)
    result = []
    seen = set()

    for t in tokens:
        parsed = morph.parse(t)[0]

        # Только существительное
        if parsed.tag.POS != "NOUN":
            continue

        # Только одушевлённые
        if parsed.tag.animacy != "anim":
            continue

        # Только имена + фамилии
        if not ("Name" in parsed.tag or "Surn" in parsed.tag):
            continue

        lemma = parsed.normal_form.capitalize()
        if lemma not in seen:
            seen.add(lemma)
            result.append(lemma)

    return result


# ============================================================
#  ГЛАВНАЯ ФУНКЦИЯ АНАЛИЗА
# ============================================================

def analyze_scene(scene_text: str) -> Dict[str, List[str]]:
    tokens = tokenize(scene_text)
    items = []

    for t in tokens:
        norm = normalize_word(t)
        if norm:
            items.append(norm)

    return {
        "Локация": extract_by_lemmas(items, LOCATION_LEMMAS),
        "Время суток": extract_by_lemmas(items, TIME_OF_DAY_LEMMAS),
        "Персонажи": extract_characters(scene_text),
        "Массовка": extract_by_lemmas(items, MASS_LEMMAS),
        "Реквизит": extract_by_lemmas(items, PROP_LEMMAS),
        "Транспорт": extract_by_lemmas(items, TRANSPORT_LEMMAS),
        "Животные": extract_by_lemmas(items, ANIMAL_LEMMAS),
        "Трюки / Каскадёры": extract_by_lemmas(items, STUNT_LEMMAS),
        "Эффекты": extract_by_lemmas(items, EFFECT_LEMMAS),
        "Грим": extract_by_lemmas(items, MAKEUP_LEMMAS),
        "Костюмы": extract_by_lemmas(items, COSTUME_LEMMAS),
    }
