from sqlalchemy import create_engine, text

from settings import DATABASE_URL

engine = create_engine(DATABASE_URL)


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
    author_id = find_author_by_name(name)
    if author_id:
        return author_id

    with engine.begin() as connection:
        result = connection.execute(text("""INSERT INTO author(name)
                                            VALUES (:name) RETURNING id, name"""), {"name": name})
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
    params = {
        "id": id,
        "title": title,
        "isbn13": isbn13,
        "year": year,
        "language": language,
        "pages": pages,
        "publisher": publisher,
        "description": description,
        "coverurl": coverurl
    }

    if find_books_by_id(id):
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