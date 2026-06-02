from fastapi import FastAPI, HTTPException, Query
from requests import RequestException

from app.database import get_book, get_relevant_books_for_book, get_relevant_books_for_history, search_books
from app.embedding import embed_query
from app.schemas import BookDetail, BookListResponse, RelevantRequest

app = FastAPI(title="SemanticShelf API")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/books/search", response_model=BookListResponse)
def search(
        q: str = Query(..., min_length=1),
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=50),
):
    try:
        model_name, query_vector = embed_query(q)
    except RequestException as error:
        raise HTTPException(status_code=503, detail="Embedding API is unavailable") from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    books, total = search_books(query_vector, model_name, offset, limit)
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
    return book


@app.get("/api/books/{book_id}/relevant", response_model=BookListResponse)
def relevant_for_book(
        book_id: int,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=50),
):

    books = get_relevant_books_for_book(book_id, offset, limit)
    return {
        "items": books,
        "total": None,
        "offset": offset,
        "limit": limit,
    }
