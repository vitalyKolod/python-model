import re

def normalize(text: str) -> str:
    text = text.replace("\r", "\n")
    text = text.replace("\u2028", "\n")
    text = text.replace("\u00A0", " ")
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()

# 🔥 Ловим заголовки вида:
# 21. НАТ. горы. ЛАГЕРЬ. ВЕЧЕР.
# 24. ФЛЕШБЕК кати-4. ...
SCENE_REGEX = re.compile(
    r"(?:^|\n)(\d{1,3}\.\s*[^\n]+)",
    re.IGNORECASE
)

def split_scenes(text: str):
    text = normalize(text) + "\n"

    matches = list(SCENE_REGEX.finditer(text))

    if not matches:
        return [("СЦЕНА 1", text.strip())]

    scenes = []

    for i, m in enumerate(matches):
        start = m.start(1)
        end = matches[i+1].start(1) if i+1 < len(matches) else len(text)

        header = m.group(1).strip()
        body = text[start:end].replace(header, "", 1).strip()

        scenes.append((header, body))

    return scenes
