from fastapi.testclient import TestClient
from app.main import app
from app.main import app, API_KEY

client = TestClient(app)


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
            "x-api-key": "not_" + API_KEY
        }
    )

    assert response.status_code == 401


def test_model_authorized():
    response = client.get(
        "/model",
        headers={
            "x-api-key": API_KEY
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "model" in data
    assert "dimensions" in data


def test_embed():
    response = client.post(
        "/embed",
        headers={
            "x-api-key": API_KEY
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
            "x-api-key": "not_" + API_KEY
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
            "x-api-key": API_KEY
        },
        json={
            "texts": []
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "texts list cannot be empty"
