from fastapi import FastAPI, UploadFile, File
from parser.splitter import split_scenes
from parser.logic import analyze_scene
from pydantic import BaseModel
import uvicorn
from docx import Document  # библиотека для работы с .docx
import io

app = FastAPI(title="Scenario Parser API")

# -----------------------------
# POST /parse_text
# -----------------------------
class ScenarioRequest(BaseModel):
    text: str

@app.post("/parse_text")
def parse_text(request: ScenarioRequest):
    scenes = split_scenes(request.text)
    result = []
    for scene in scenes:
        lines = scene.strip().split("\n")
        header = lines[0].strip()
        scene_text = "\n".join(lines[1:]).strip()
        analysis = analyze_scene(scene_text)
        result.append({
            "scene_header": header,
            "analysis": analysis
        })
    return {"scenes": result}

# -----------------------------
# POST /parse_file
# -----------------------------
@app.post("/parse_file")
async def parse_file(file: UploadFile = File(...)):
    content = await file.read()
    text = ""

    if file.filename.endswith(".docx"):
        # читаем Word-документ
        doc = Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs)
    else:
        # читаем обычный текст
        text = content.decode("utf-8")

    scenes = split_scenes(text)
    result = []
    for scene in scenes:
        lines = scene.strip().split("\n")
        header = lines[0].strip()
        scene_text = "\n".join(lines[1:]).strip()
        analysis = analyze_scene(scene_text)
        result.append({
            "scene_header": header,
            "analysis": analysis
        })
    return {"scenes": result}

# -----------------------------
# Запуск через uvicorn
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)


