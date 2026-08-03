from sqlalchemy import create_engine, text

from app.ml.predictor import predict_book_genres
from app.settings import DATABASE_SCHEMA, DATABASE_URL

DEFAULT_EMBEDDING_TYPE = "title_author"

engine = create_engine(
    DATABASE_URL,
    connect_args={"options": f"-csearch_path={DATABASE_SCHEMA}"}
)


def books_from_rows(connection, rows):
    books = [dict(row) for row in rows]
    book_ids = [book["id"] for book in books]
    if book_ids:
        authors = connection.execute(
            text("""
                 SELECT book_author.book_id, author.name
                 FROM author
                          JOIN book_author ON book_author.author_id = author.id
                 WHERE book_author.book_id = ANY(:book_ids)
                 ORDER BY author.name
                 """),
            {"book_ids": book_ids}
        )
        authors_map = {}
        for book_id, name in authors:
            authors_map.setdefault(book_id, []).append(name)
    else:
        authors_map = {}
    for book in books:
        book["authors"] = authors_map.get(book["id"], [])
    return books


def search_books(query_vector, model_name, offset, limit, author_filter=None):
    params = {
        "query_vector": query_vector,
        "model_name": model_name,
        "embedding_type": DEFAULT_EMBEDDING_TYPE,
        "author_filter": author_filter,
        "offset": offset,
        "limit": limit,
    }

    with engine.connect() as connection:
        total = connection.execute(
            text("""
                 SELECT COUNT(*)
                 FROM book
                          JOIN embedding ON embedding.book_id = book.id
                 WHERE embedding.embedding_type = :embedding_type
                   AND (:model_name IS NULL OR embedding.model_name = :model_name)
                   AND (
                     :author_filter IS NULL
                         OR EXISTS (
                         SELECT 1
                         FROM book_author
                                  JOIN author ON author.id = book_author.author_id
                         WHERE book_author.book_id = book.id
                           AND author.name ILIKE '%' || :author_filter || '%'
                     )
                     )
                 """),
            params
        ).scalar()

        result = connection.execute(
            text("""
                 SELECT book.id,
                        book.title,
                        book.year,
                        book.language,
                        book.cover_url,
                        CASE WHEN :query_vector IS NULL THEN NULL
                             ELSE embedding.embedding_vector OPERATOR(public.<=>) CAST(:query_vector AS public.vector)
                        END AS score
                 FROM book
                     JOIN embedding
                 ON embedding.book_id = book.id
                 WHERE embedding.embedding_type = :embedding_type
                   AND (:model_name IS NULL OR embedding.model_name = :model_name)
                   AND (
                     :author_filter IS NULL
                         OR EXISTS (
                         SELECT 1
                         FROM book_author
                                  JOIN author ON author.id = book_author.author_id
                         WHERE book_author.book_id = book.id
                           AND author.name ILIKE '%' || :author_filter || '%'
                     )
                     )
                 ORDER BY score NULLS LAST, book.title
                 OFFSET :offset LIMIT :limit
                 """),
            params
        )
        books = books_from_rows(connection, result.mappings())

    return books, total


def get_book(book_id):
    with engine.connect() as connection:
        row = connection.execute(
            text("""
                 SELECT id,
                        title,
                        description,
                        isbn13, year, language, publisher, pages, cover_url
                 FROM book
                 WHERE id = :book_id
                 """),
            {"book_id": book_id}
        ).mappings().first()

        if row is None:
            return None

        return books_from_rows(connection, [row])[0]


def get_genres_for_book(book_id, limit):
    with engine.connect() as connection:
        row = connection.execute(
            text("""
                 SELECT embedding_vector::text AS vec
                 FROM embedding
                 WHERE book_id = :book_id
                   AND embedding_type = :embedding_type
                 ORDER BY created_at DESC
                 LIMIT 1
                 """),
            {"book_id": book_id, "embedding_type": DEFAULT_EMBEDDING_TYPE}
        ).mappings().first()

    if not row or not row["vec"]:
        return []

    return predict_book_genres(row["vec"], limit)


def get_relevant_books_for_book(book_id, offset, limit):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                 WITH source AS (SELECT embedding_vector, model_name
                                 FROM embedding
                                 WHERE book_id = :book_id
                                   AND embedding_type = :embedding_type
                                 ORDER BY created_at DESC
                                 LIMIT 1
                                 )
                 SELECT book.id,
                        book.title,
                        book.year,
                        book.language,
                        book.cover_url,
                        embedding.embedding_vector OPERATOR(public.<=>) source.embedding_vector AS score
                 FROM source
                          JOIN embedding ON embedding.embedding_type = :embedding_type
                      AND embedding.model_name = source.model_name
                          JOIN book ON book.id = embedding.book_id
                 WHERE book.id != :book_id
                 ORDER BY score
                 OFFSET :offset LIMIT :limit
                 """),
            {
                "book_id": book_id,
                "embedding_type": DEFAULT_EMBEDDING_TYPE,
                "offset": offset,
                "limit": limit,
            }
        )
        return books_from_rows(connection, result.mappings())


def get_random_books(offset, limit):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                 SELECT id, title, year, language, cover_url, NULL AS score
                 FROM book
                 ORDER BY random()
                 OFFSET :offset LIMIT :limit
                 """),
            {
                "offset": offset,
                "limit": limit,
            }
        )
        return books_from_rows(connection, result.mappings())


def get_relevant_books_for_history(book_ids, offset, limit):
    if not book_ids:
        return get_random_books(offset, limit)
    with engine.connect() as connection:
        embedding_rows = connection.execute(
            text("""
                 SELECT model_name, embedding_vector::text AS embedding_vector
                 FROM embedding
                 WHERE book_id = ANY (:book_ids)
                   AND embedding_type = :embedding_type
                 ORDER BY created_at DESC
                 """),
            {"book_ids": book_ids, "embedding_type": DEFAULT_EMBEDDING_TYPE}
        ).mappings().all()

        if not embedding_rows:
            return []

        model_name = embedding_rows[0]["model_name"]
        vectors = [
            [float(item) for item in row["embedding_vector"].strip("[]").split(",")]
            for row in embedding_rows
            if row["model_name"] == model_name
        ]
        average_vector = "[" + ",".join(str(value) for value in [
            sum(vector[i] for vector in vectors) / len(vectors)
            for i in range(len(vectors[0]))
        ]) + "]"

        result = connection.execute(
            text("""
                 SELECT book.id,
                        book.title,
                        book.year,
                        book.language,
                        book.cover_url,
                        embedding.embedding_vector OPERATOR(public.<=>) CAST(:average_vector AS public.vector) AS score
                 FROM embedding
                     JOIN book
                 ON book.id = embedding.book_id
                 WHERE embedding.embedding_type = :embedding_type
                   AND embedding.model_name = :model_name
                   AND NOT (embedding.book_id = ANY (:book_ids))
                 ORDER BY score
                 OFFSET :offset LIMIT :limit
                 """),
            {
                "book_ids": book_ids,
                "embedding_type": DEFAULT_EMBEDDING_TYPE,
                "model_name": model_name,
                "average_vector": average_vector,
                "offset": offset,
                "limit": limit,
            }
        )
        return books_from_rows(connection, result.mappings())
