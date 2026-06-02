from sqlalchemy import create_engine, text

from app.settings import DATABASE_SCHEMA, DATABASE_URL

DEFAULT_EMBEDDING_TYPE = "title_author"

engine = create_engine(
    DATABASE_URL,
    connect_args={"options": f"-csearch_path={DATABASE_SCHEMA}"}
)


def get_authors(connection, book_id):
    return [row[0] for row in connection.execute(
        text("""
             SELECT author.name
             FROM author
                      JOIN book_author ON book_author.author_id = author.id
             WHERE book_author.book_id = :book_id
             ORDER BY author.name
             """),
        {"book_id": book_id}
    )]


def book_from_row(connection, row):
    data = dict(row)
    data["authors"] = get_authors(connection, data["id"])
    return data


def search_books(query_vector, model_name, offset, limit):
    params = {
        "query_vector": query_vector,
        "model_name": model_name,
        "embedding_type": DEFAULT_EMBEDDING_TYPE,
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
                   AND embedding.model_name = :model_name
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
                        embedding.embedding_vector OPERATOR(public.<=>) CAST(:query_vector AS public.vector) AS score
                 FROM book
                     JOIN embedding
                 ON embedding.book_id = book.id
                 WHERE embedding.embedding_type = :embedding_type
                   AND embedding.model_name = :model_name
                 ORDER BY score
                 OFFSET :offset LIMIT :limit
                 """),
            params
        )
        books = [book_from_row(connection, row) for row in result.mappings()]

    return books, total
