import os
import json
import torch
from app.ml.model import BookGenreLMHead

ML_DIR = os.path.dirname(__file__)
GENRES_PATH = os.path.join(ML_DIR, "genres.json")
MODEL_PATH = os.path.join(ML_DIR, "model.pt")

if os.path.exists(GENRES_PATH):
    with open(GENRES_PATH, "r", encoding="utf-8") as f:
        GENRES = json.load(f)
else:
    GENRES = []

MODEL = BookGenreLMHead(input_dim=384, num_classes=len(GENRES), hidden_dim=128) if GENRES else None
if MODEL and os.path.exists(MODEL_PATH):
    MODEL.load_state_dict(torch.load(MODEL_PATH))
    MODEL.eval()

def predict_book_genres(vec_input, limit=5):
    if not MODEL or not vec_input:
        return []

    if isinstance(vec_input, str):
        vec = [float(x) for x in vec_input.strip("[]").split(",") if x.strip()]
    else:
        vec = vec_input

    probs = MODEL.predict_probabilities(vec)

    results = []
    for idx, (genre_name, prob) in enumerate(zip(GENRES, probs)):
        results.append({
            "id": idx + 1,
            "name": genre_name,
            "probability": round(prob, 4)
        })

    results.sort(key=lambda x: x["probability"], reverse=True)
    return results[:limit]
