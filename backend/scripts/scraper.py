import argparse
import time
from threading import Thread

import requests
from bs4 import BeautifulSoup

from db import add_book, link_authors

DETAIL_URL_TEMPLATE = "https://htl-stp.bibbs.cc/search?mode=stb&q=&critCount=3&crit_0=&op_0=&crit_1=&op_1=AND&ma=0&exAnz=0&flt=Alle&gradeFlt=&sort_0=Systematik&sort_1=Haupteintrag&sort_2=Haupttitel&page=1&view=detail&page_size=10&id=0.{book_id}"
REQUEST_TIMEOUT_SECONDS = 10
THREAD_START_DELAY_SECONDS = 5
DEFAULT_START_ID = 1
DEFAULT_END_ID = 8000
DEFAULT_THREADS = 8


def find_row(label, soup):
    try:
        return (
            soup.find("td", class_="label", string=label)
            .find_parent("tr")
            .find("td", class_="data")
            .get_text()
            .strip()
        )
    except AttributeError:
        return None


def scrape(start_id, end_id):
    for book_id in range(start_id, end_id + 1):
        try:
            url = DETAIL_URL_TEMPLATE.format(book_id=book_id)

            response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)

            print(f"request done {book_id}")
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, 'html.parser')

            div = soup.select_one("div.detailData")
            if not div:
                continue
            div_cover_image = soup.select_one("div.coverimage")
            title = div.select_one("h3").text
            if not title:
                continue
            isbn_raw = find_row("ISBN", soup)
            isbn = "".join(d for d in isbn_raw if d.isdigit()) if isbn_raw else None
            verfasser_row = find_row("Verfasser", soup)
            verfasser = verfasser_row.split(";") if verfasser_row else None
            verlag = find_row("Verlag", soup)
            jahr = find_row("Jahr", soup)
            umfang_row = find_row("Umfang", soup)
            umfang = "".join(d for d in umfang_row if d.isdigit()) if umfang_row else None
            sprache = find_row("Sprache", soup)
            cover_url = div_cover_image.select_one("img").attrs["src"]
            book = {
                "id": book_id,
                "title": title,
                "isbn13": isbn,
                "description": None,
                "author": verfasser,
                "publisher": verlag,
                "year": jahr,
                "pages": umfang,
                "language": sprache,
                "coverurl": cover_url,
            }

            book_data = book.copy()

            book_data.pop("author")
            add_book(**book_data)
            link_authors(book["id"], book["author"])
            print(f"Book {book['title']} was scraped")
        except Exception as e:
            print(f"Error on id {book_id}: {e}")

            continue


def worker(start_id, end_id, threads):
    if start_id > end_id:
        raise ValueError("start id cannot be greater than end id")
    if threads < 1:
        raise ValueError("threads must be greater than 0")

    total_items = end_id - start_id + 1
    threads = min(threads, total_items)
    part = total_items // threads
    first = start_id
    threads_array = []

    for thread_number in range(1, threads + 1):
        if thread_number == threads:
            end = end_id
        else:
            end = first + part - 1

        t = Thread(target=scrape, args=(first, end))
        t.start()
        threads_array.append(t)

        first = end + 1
        time.sleep(THREAD_START_DELAY_SECONDS)

    for t in threads_array:
        t.join()


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape books by id range.")
    parser.add_argument("--start", type=int, default=DEFAULT_START_ID, help="First book id to scrape.")
    parser.add_argument("--end", type=int, default=DEFAULT_END_ID, help="Last book id to scrape.")
    parser.add_argument("--threads", type=int, default=DEFAULT_THREADS, help="Number of worker threads.")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    worker(args.start, args.end, args.threads)
