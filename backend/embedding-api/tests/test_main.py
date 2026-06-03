from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


class FakeVectors:
    def __init__(self, vectors):
        self.vectors = vectors

    def tolist(self):
        return self.vectors


class FakeModel:
    def get_embedding_dimension(self):
        return 3

    def encode(self, texts, normalize_embeddings=True):
        return FakeVectors([[0.1, 0.2, 0.3] for _ in texts])


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_model_invalid_api_key():
    response = client.get(
        "/model",
        headers={
            "x-api-key": "not_" + main.API_KEY
        }
    )

    assert response.status_code == 401


def test_model_authorized(monkeypatch):
    monkeypatch.setattr(main, "get_model", lambda: FakeModel())

    response = client.get(
        "/model",
        headers={
            "x-api-key": main.API_KEY
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "model" in data
    assert "dimensions" in data


def test_embed(monkeypatch):
    monkeypatch.setattr(main, "get_model", lambda: FakeModel())

    response = client.post(
        "/embed",
        headers={
            "x-api-key": main.API_KEY
        },
        json={
            "texts": [
                "hello world",
                "test"
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "vectors" in data
    assert len(data["vectors"]) == 2


def test_embed_invalid_api_key():
    response = client.post(
        "/embed",
        headers={
            "x-api-key": "not_" + main.API_KEY
        },
        json={
            "texts": ["hello"]
        }
    )

    assert response.status_code == 401


def test_embed_empty_list():
    response = client.post(
        "/embed",
        headers={
            "x-api-key": main.API_KEY
        },
        json={
            "texts": []
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "texts list cannot be empty"
