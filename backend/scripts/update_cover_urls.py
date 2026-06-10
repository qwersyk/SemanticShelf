import argparse
from struct import unpack

import requests
from sqlalchemy import text

from db import engine

REQUEST_TIMEOUT_SECONDS = 10


def image_size(content):
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return unpack(">II", content[16:24])

    if content.startswith(b"\xff\xd8"):
        index = 2
        while index < len(content):
            while index < len(content) and content[index] == 0xff:
                index += 1
            marker = content[index]
            index += 1
            length = unpack(">H", content[index:index + 2])[0]
            if marker in (0xc0, 0xc2):
                height, width = unpack(">HH", content[index + 3:index + 7])
                return width, height
            index += length

    return None, None


def image_exists(url, min_width=200, allow_png=True):
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException:
        return False

    if response.status_code != 200:
        return False

    content_type = response.headers.get("content-type", "")
    if "image/" not in content_type:
        return False
    if not allow_png and "image/png" in content_type:
        return False

    width, _ = image_size(response.content)
    return width is not None and width >= min_width


def find_cover_url(isbn):
    urls = [
        (f"https://images.littera.eu/image/KeYAtqESLROpw0UM/{isbn}/m", False),
        (f"https://books.google.com/books/content?vid=ISBN:{isbn}&printsec=frontcover&img=1&zoom=1&fife=w320", False),
        (f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false", True),
    ]

    for url, allow_png in urls:
        if image_exists(url, allow_png=allow_png):
            return url

    return None


def update_cover_urls(start_id, end_id):
    if start_id is not None and end_id is not None and start_id > end_id:
        raise ValueError("start id cannot be greater than end id")

    where_parts = []
    params = {}

    if start_id is not None:
        where_parts.append("id >= :start_id")
        params["start_id"] = start_id
    if end_id is not None:
        where_parts.append("id <= :end_id")
        params["end_id"] = end_id

    where_sql = "WHERE " + " AND ".join(where_parts) if where_parts else ""

    with engine.connect() as connection:
        books = connection.execute(
            text(f"""
                 SELECT id, isbn13
                 FROM book
                 {where_sql}
                 ORDER BY id
                 """),
            params
        ).mappings().all()

    updates = []
    for index, book in enumerate(books, start=1):
        isbn = book["isbn13"]
        print(isbn)
        cover_url = find_cover_url(isbn) if isbn else None
        updates.append({"id": book["id"], "cover_url": cover_url})
        print(f"{index}/{len(books)} book {book['id']}: {cover_url}")

    if not updates:
        print("Updated books: 0")
        return

    with engine.begin() as connection:
        connection.execute(
            text("""
                 UPDATE book
                 SET cover_url = :cover_url
                 WHERE id = :id
                 """),
            updates
        )

    print(f"Updated books: {len(updates)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Update book cover URLs.")
    parser.add_argument("--start", type=int, help="First book id.")
    parser.add_argument("--end", type=int, help="Last book id.")
    return parser.parse_args()


def main():
    args = parse_args()
    update_cover_urls(args.start, args.end)


if __name__ == "__main__":
    main()
