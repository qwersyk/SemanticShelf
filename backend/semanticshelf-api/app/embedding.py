import requests

from app.settings import EMBEDDING_API_KEY, EMBEDDING_API_URL

EXPECTED_DIMENSIONS = 384


def embed_query(query):
    response = requests.post(
        f"{EMBEDDING_API_URL}/embed",
        headers={"x-api-key": EMBEDDING_API_KEY},
        json={"texts": [f"query: {query.strip()}"]},
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    if data["dimensions"] != EXPECTED_DIMENSIONS:
        raise RuntimeError(f"Expected {EXPECTED_DIMENSIONS} dimensions, got {data['dimensions']}")

    return data["model"], "[" + ",".join(str(value) for value in data["vectors"][0]) + "]"
