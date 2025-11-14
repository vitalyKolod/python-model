import re
from typing import List, Tuple, Optional

# Регулярки для заголовков и разбиения сцен
SCENE_HEADER_RE = re.compile(
    r"^(СЦЕНА\s*\d+)\s*[-—]?\s*(?:\(?\s*(ИНТ\.|ЭКСТ\.)\s*\)?)?\s*[-—]?\s*(.*?)(?:—\s*(ДЕНЬ|НОЧЬ|УТРО|ВЕЧЕР))?",
    flags=re.IGNORECASE | re.MULTILINE
)

SPLIT_SCENES_RE = re.compile(
    r"(СЦЕНА\s*\d+[^\n]*?(?:\n(?:\s|.)*?))(?=(?:\nСЦЕНА\s*\d+)|\Z)",
    flags=re.IGNORECASE
)

def split_scenes(text: str) -> List[str]:
    """
    Разбивает полный сценарий на блоки по заголовку 'СЦЕНА <номер>'.
    Возвращает список подстрок (каждая — текст сцены).
    """
    scenes = re.split(r'(СЦЕНА \d+.*)', text)
    scenes = [scenes[i] + scenes[i+1] for i in range(1, len(scenes), 2)]
    return scenes

def parse_header(scene_text: str) -> str:
    """
    Пытается извлечь читабельный заголовок сцены,
    например: 'СЦЕНА 7 — ЭКСТ. ГОРОДСКАЯ УЛИЦА — ДЕНЬ'
    Если не найден, возвращает начало сцены (до первой строки).
    """
    first_line = scene_text.splitlines()[0].strip()
    m = SCENE_HEADER_RE.match(first_line)
    if m:
        scene_num = m.group(1).strip()
        int_ext = (m.group(2) or "").upper().strip()
        loc = (m.group(3) or "").strip()
        time = (m.group(4) or "").upper().strip()

        parts = [scene_num]
        if int_ext:
            parts.append(int_ext)
        if loc:
            parts.append(loc)
        if time:
            parts.append(time)
        return " — ".join([p for p in parts if p])
    else:
        # fallback: вернуть первую непустую строку
        for line in scene_text.splitlines():
            if line.strip():
                return line.strip()
        return "Неизвестно"

def demo_on_text(text: str) -> List[Tuple[str, str]]:
    """
    Утилита: разбить текст на сцены и вернуть список (header, scene_text)
    """
    scenes = split_scenes(text)
    out = []
    for s in scenes:
        header = parse_header(s)
        out.append((header, s))
    return out
