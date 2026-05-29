import argparse

import requests

from db import add_embeddings, find_author_names_for_books, find_books_without_embedding
from settings import EMBEDDING_API_KEY, EMBEDDING_API_URL

EMBEDDING_TYPE = "title_author"
EXPECTED_DIMENSIONS = 384
DEFAULT_START_ID = 1
DEFAULT_END_ID = 8000
DEFAULT_BATCH_SIZE = 32


def build_embedding_text(title, authors):
    if authors:
        return f"passage: {title}. Authors: {authors}"
    return f"passage: {title}"


def add_authors_to_books(books):
    book_ids = [book["id"] for book in books]
    authors_map = find_author_names_for_books(book_ids)
    books_with_authors = []
    for book in books:
        books_with_authors.append({
            "id": book["id"],
            "title": book["title"],
            "authors": "; ".join(authors_map.get(book["id"], [])),
        })
    return books_with_authors


def iter_batches(items, batch_size):
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


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


def create_embeddings(start_id, end_id, batch_size):
    if start_id > end_id:
        raise ValueError("start id cannot be greater than end id")
    if batch_size < 1:
        raise ValueError("batch size must be greater than 0")

    books = add_authors_to_books(find_books_without_embedding(EMBEDDING_TYPE, start_id, end_id))
    if not books:
        print("No books without embeddings")
        return

    total = 0
    for batch in iter_batches(books, batch_size):
        texts = [build_embedding_text(row["title"], row["authors"]) for row in batch]
        model_name, vectors = embed_texts(texts)
        add_embeddings(batch, EMBEDDING_TYPE, model_name, vectors)
        total += len(batch)
        print(f"Saved embeddings: {total}/{len(books)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Create title-author embeddings for books.")
    parser.add_argument("--start", type=int, default=DEFAULT_START_ID, help="First book id to process.")
    parser.add_argument("--end", type=int, default=DEFAULT_END_ID, help="Last book id to process.")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Embedding API batch size.")
    return parser.parse_args()


def main():
    args = parse_args()
    create_embeddings(args.start, args.end, args.batch_size)


if __name__ == "__main__":
    main()
