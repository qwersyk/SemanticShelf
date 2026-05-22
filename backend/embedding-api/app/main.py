import os

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

API_KEY = os.getenv("API_KEY", "secret")
MODEL_NAME = os.getenv("MODEL_NAME", "intfloat/multilingual-e5-small")

model = SentenceTransformer(MODEL_NAME)

app = FastAPI()


class EmbedRequest(BaseModel):
    texts: list[str]


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


@app.get("/model")
async def model_info(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return {
        "model": MODEL_NAME,
        "dimensions": model.get_embedding_dimension()
    }


@app.post("/embed")
async def embed(request: EmbedRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    if not request.texts:
        raise HTTPException(
            status_code=400,
            detail="texts list cannot be empty"
        )

    vectors = model.encode(request.texts, normalize_embeddings=True).tolist()

    return {
        "model": MODEL_NAME,
        "dimensions": model.get_embedding_dimension(),
        "vectors": vectors
    }
