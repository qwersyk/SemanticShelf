import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/books_db")

from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)

BOOK_SUMMARY = {
    "id": 1,
    "title": "Test Book",
    "authors": ["Test Author"],
    "year": 2024,
    "language": "en",
    "cover_url": None,
    "score": 0.12,
}

BOOK_DETAIL = {
    **BOOK_SUMMARY,
    "description": "Test description",
    "isbn13": "1234567890123",
    "publisher": "Test Publisher",
    "pages": 100,
}


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search(monkeypatch):
    monkeypatch.setattr(main, "embed_query", lambda query: ("test-model", "[0.1,0.2]"))
    monkeypatch.setattr(main, "search_books", lambda vector, model, offset, limit, author_filter=None: ([BOOK_SUMMARY], 1))

    response = client.get("/api/books/search?q=python&offset=0&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["title"] == "Test Book"
    assert data["total"] == 1
    assert data["offset"] == 0
    assert data["limit"] == 10


def test_search_with_author_filter(monkeypatch):
    captured = {}

    def fake_embed_query(query):
        captured["query"] = query
        return "test-model", "[0.1,0.2]"

    def fake_search_books(vector, model, offset, limit, author_filter=None):
        captured["author_filter"] = author_filter
        return [BOOK_SUMMARY], 1

    monkeypatch.setattr(main, "embed_query", fake_embed_query)
    monkeypatch.setattr(main, "search_books", fake_search_books)

    response = client.get("/api/books/search?q=python author:`Test Author`")

    assert response.status_code == 200
    assert captured["query"] == "python"
    assert captured["author_filter"] == "Test Author"


def test_search_empty_query():
    response = client.get("/api/books/search?q=   ")

    assert response.status_code == 400
    assert response.json()["detail"] == "Search query cannot be empty"


def test_book_detail(monkeypatch):
    monkeypatch.setattr(main, "get_book", lambda book_id: BOOK_DETAIL)

    response = client.get("/api/books/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["description"] == "Test description"


def test_book_detail_not_found(monkeypatch):
    monkeypatch.setattr(main, "get_book", lambda book_id: None)

    response = client.get("/api/books/404")

    assert response.status_code == 404


def test_relevant_for_book(monkeypatch):
    monkeypatch.setattr(main, "get_book", lambda book_id: BOOK_DETAIL)
    monkeypatch.setattr(main, "get_relevant_books_for_book", lambda book_id, offset, limit: [BOOK_SUMMARY])

    response = client.get("/api/books/1/relevant?offset=0&limit=10")

    assert response.status_code == 200
    assert response.json()["items"][0]["id"] == 1


def test_relevant_for_book_not_found(monkeypatch):
    monkeypatch.setattr(main, "get_book", lambda book_id: None)

    response = client.get("/api/books/404/relevant")

    assert response.status_code == 404


def test_relevant_for_history(monkeypatch):
    monkeypatch.setattr(main, "get_relevant_books_for_history", lambda book_ids, offset, limit: [BOOK_SUMMARY])

    response = client.post(
        "/api/books/relevant",
        json={
            "book_ids": [1, 2],
            "offset": 0,
            "limit": 10,
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["title"] == "Test Book"
