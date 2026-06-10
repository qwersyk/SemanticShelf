import csv
from pathlib import Path

import requests
from sqlalchemy import text

from db import engine
from settings import EMBEDDING_API_KEY, EMBEDDING_API_URL

EXPECTED_DIMENSIONS = 384

CSV_PATH = Path(__file__).resolve().parent / "genres.csv"


def load_genres():
    genres = []

    with open(CSV_PATH, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            genres.append((row["name"].strip(), row["description"].strip()))

    return genres


def embed_texts(texts):
    response = requests.post(
        f"{EMBEDDING_API_URL}/embed",
        headers={"x-api-key": EMBEDDING_API_KEY},
        json={"texts": texts},
        timeout=60
    )
    response.raise_for_status()

    data = response.json()
    if data["dimensions"] != EXPECTED_DIMENSIONS:
        raise RuntimeError(f"Expected {EXPECTED_DIMENSIONS} dimensions, got {data['dimensions']}")

    return data["model"], data["vectors"]


def seed_genres():
    genres = load_genres()
    texts = [f"passage: {name}. {description}" for name, description in genres]
    model_name, vectors = embed_texts(texts)

    with engine.begin() as connection:
        for (name, description), vector in zip(genres, vectors):
            connection.execute(
                text("""
                     INSERT INTO genre(name, description, model_name, embedding_vector)
                     VALUES (:name, :description, :model_name,
                             CAST(:embedding_vector AS public.vector)) ON CONFLICT (name) DO
                     UPDATE
                         SET description = EXCLUDED.description,
                         model_name = EXCLUDED.model_name,
                         embedding_vector = EXCLUDED.embedding_vector
                     """),
                {
                    "name": name,
                    "description": description,
                    "model_name": model_name,
                    "embedding_vector": str(vector),
                }
            )

    print(f"Saved genres: {len(genres)}")


def main():
    seed_genres()


if __name__ == "__main__":
    main()
