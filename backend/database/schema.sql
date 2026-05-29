CREATE SCHEMA IF NOT EXISTS semanticshelf;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS semanticshelf.author
(
    id   BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS semanticshelf.book
(
    id          BIGSERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT,
    isbn13      VARCHAR(13) UNIQUE,
    year        INTEGER,
    language    VARCHAR(10),
    publisher   TEXT,
    pages       INTEGER,
    cover_url   TEXT
);

CREATE TABLE IF NOT EXISTS semanticshelf.book_author
(
    book_id   BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    PRIMARY KEY (book_id, author_id),
    CONSTRAINT fk_book_author_book
        FOREIGN KEY (book_id)
            REFERENCES semanticshelf.book (id)
            ON DELETE CASCADE,
    CONSTRAINT fk_book_author_author
        FOREIGN KEY (author_id)
            REFERENCES semanticshelf.author (id)
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS semanticshelf.embedding
(
    id               BIGSERIAL PRIMARY KEY,
    book_id          BIGINT       NOT NULL,
    embedding_type   VARCHAR(50)  NOT NULL,
    model_name       VARCHAR(100) NOT NULL,
    embedding_vector public.vector(384) NOT NULL,
    created_at       TIMESTAMP WITH TIME ZONE
        DEFAULT NOW(),
    UNIQUE (book_id, embedding_type, model_name),
    CONSTRAINT fk_embedding_book
        FOREIGN KEY (book_id)
            REFERENCES semanticshelf.book (id)
            ON DELETE CASCADE
);
