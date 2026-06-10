import re

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from requests import RequestException

from app.database import get_book, get_genres_for_book, get_relevant_books_for_book, get_relevant_books_for_history, search_books
from app.embedding import embed_query
from app.schemas import BookDetail, BookListResponse, GenreScore, RelevantRequest
from app.settings import CORS_ALLOW_ALL

app = FastAPI(title="SemanticShelf API")

if CORS_ALLOW_ALL:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

AUTHOR_FILTER_PATTERN = re.compile(r"\bauthor:`([^`]+)`", re.IGNORECASE)


def parse_search_query(query):
    author_match = AUTHOR_FILTER_PATTERN.search(query)
    author_filter = author_match.group(1).strip() if author_match else None
    author_filter = author_filter or None
    clean_query = AUTHOR_FILTER_PATTERN.sub("", query)
    clean_query = " ".join(clean_query.split())
    return clean_query, author_filter


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/books/search", response_model=BookListResponse)
def search(
        q: str = Query(..., min_length=1),
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=50),
):
    clean_query, author_filter = parse_search_query(q)

    if not clean_query:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    try:
        model_name, query_vector = embed_query(clean_query)
    except RequestException as error:
        raise HTTPException(status_code=503, detail="Embedding API is unavailable") from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    books, total = search_books(query_vector, model_name, offset, limit, author_filter)
    return {
        "items": books,
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@app.post("/api/books/relevant", response_model=BookListResponse)
def relevant_for_history(request: RelevantRequest):
    books = get_relevant_books_for_history(request.book_ids, request.offset, request.limit)
    return {
        "items": books,
        "total": None,
        "offset": request.offset,
        "limit": request.limit,
    }


@app.get("/api/books/{book_id}", response_model=BookDetail)
def book_detail(book_id: int):
    book = get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get("/api/books/{book_id}/genres", response_model=list[GenreScore])
def book_genres(
        book_id: int,
        limit: int = Query(default=5, ge=1, le=30),
):
    if get_book(book_id) is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return get_genres_for_book(book_id, limit)


@app.get("/api/books/{book_id}/relevant", response_model=BookListResponse)
def relevant_for_book(
        book_id: int,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=50),
):
    if get_book(book_id) is None:
        raise HTTPException(status_code=404, detail="Book not found")

    books = get_relevant_books_for_book(book_id, offset, limit)
    return {
        "items": books,
        "total": None,
        "offset": offset,
        "limit": limit,
    }
