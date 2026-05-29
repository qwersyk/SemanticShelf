from sqlalchemy import create_engine, text

from settings import DATABASE_SCHEMA, DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"options": f"-csearch_path={DATABASE_SCHEMA}"}
)


def find_author_by_name(name):
    with engine.connect() as connection:
        result = connection.execute(text("""SELECT *
                                            FROM author
                                            WHERE name = :name"""), {"name": name})
        return result.scalar()


def delete_authors_by_name(name):
    with engine.begin() as connection:
        result = connection.execute(
            text("""
                 DELETE
                 FROM author
                 WHERE name = :name
                 """),
            {"name": name}
        )
        return result.rowcount


def add_author(name):
    with engine.begin() as connection:
        result = connection.execute(
            text("""
                 INSERT INTO author(name)
                 VALUES (:name)
                 ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                 RETURNING id
                 """),
            {"name": name}
        )
        return result.scalar()


def link_authors(book_id, authors_names):
    if authors_names is None:
        return None

    author_ids = []
    for name in authors_names:
        author_ids.append(add_author(name))

    if not author_ids:
        return None

    with engine.begin() as connection:
        result = None
        for author_id in author_ids:
            result = connection.execute(text("""INSERT INTO book_author(author_id, book_id)
                                                VALUES (:author_id, :book_id)
                                                    ON CONFLICT (book_id, author_id) DO NOTHING
                                             RETURNING *"""), {"author_id": author_id, "book_id": book_id})
        return result.fetchone()


def find_books_by_id(book_id):
    with engine.connect() as connection:
        result = connection.execute(text("""SELECT *
                                            FROM book
                                            WHERE id = :id"""), {"id": book_id})
        return result.scalar()


def add_book(id, title, isbn13, year, language, pages, publisher, description, coverurl):
    book_id = id
    params = {
        "id": book_id,
        "title": title,
        "isbn13": isbn13,
        "year": year,
        "language": language,
        "pages": pages,
        "publisher": publisher,
        "description": description,
        "coverurl": coverurl
    }

    if find_books_by_id(book_id):
        with engine.begin() as connection:
            result = connection.execute(
                text("""
                    UPDATE book
                    SET
                        title = COALESCE(:title, title),
                        isbn13 = COALESCE(:isbn13, isbn13),
                        year = COALESCE(:year, year),
                        language = COALESCE(:language, language),
                        pages = COALESCE(:pages, pages),
                        publisher = COALESCE(:publisher, publisher),
                        description = COALESCE(:description, description),
                        cover_url = COALESCE(:coverurl, cover_url)
                    WHERE id = :id
                    RETURNING *
                """),
                params
            )

            return result.fetchone()

    with engine.begin() as connection:
        result = connection.execute(
            text("""
                INSERT INTO book(id, title, isbn13, year, language, pages, publisher, description, cover_url)
                VALUES (:id, :title, :isbn13, :year, :language, :pages, :publisher, :description, :coverurl)
                RETURNING *
            """),
            params
        )

        return result.fetchone()


def find_books_without_embedding(embedding_type, start_id, end_id):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                 SELECT id, title
                 FROM book
                 WHERE id BETWEEN :start_id AND :end_id
                   AND NOT EXISTS (
                     SELECT 1
                     FROM embedding
                     WHERE embedding.book_id = book.id
                       AND embedding.embedding_type = :embedding_type
                 )
                 ORDER BY id
                 """),
            {"embedding_type": embedding_type, "start_id": start_id, "end_id": end_id}
        )
        return result.mappings().all()


def find_author_names_by_book_id(book_id):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                 SELECT author.name
                 FROM author
                 JOIN book_author ON book_author.author_id = author.id
                 WHERE book_author.book_id = :book_id
                 ORDER BY author.name
                 """),
            {"book_id": book_id}
        )
        return [row[0] for row in result]


def add_embeddings(rows, embedding_type, model_name, vectors):
    with engine.begin() as connection:
        for row, vector in zip(rows, vectors):
            connection.execute(
                text("""
                     INSERT INTO embedding(book_id, embedding_type, model_name, embedding_vector)
                     VALUES (:book_id, :embedding_type, :model_name, CAST(:embedding_vector AS public.vector))
                     ON CONFLICT (book_id, embedding_type, model_name) DO NOTHING
                     """),
                {
                    "book_id": row["id"],
                    "embedding_type": embedding_type,
                    "model_name": model_name,
                    "embedding_vector": str(vector),
                }
            )
