import requests
from bs4 import BeautifulSoup
from threading import Thread
from db import add_book, link_authors
import time

DETAIL_URL_TEMPLATE = "https://htl-stp.bibbs.cc/search?mode=stb&q=&critCount=3&crit_0=&op_0=&crit_1=&op_1=AND&ma=0&exAnz=0&flt=Alle&gradeFlt=&sort_0=Systematik&sort_1=Haupteintrag&sort_2=Haupttitel&page=1&view=detail&page_size=10&id=0.{book_id}"
REQUEST_TIMEOUT_SECONDS = 10
THREAD_START_DELAY_SECONDS = 5
SCRAPE_AMOUNT = 8000
SCRAPE_THREADS = 8

books = []

def find_row(string , soup):
    try:
        return soup.find("td" , class_="label" ,string= string).find_parent("tr").find("td" , class_="data").get_text().strip()
    except:
        return None

def scrape(a , b):

    for i in range(a ,b+1):
        try:
            url = DETAIL_URL_TEMPLATE.format(book_id=i)

            response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)

            print(f"request done {i}")
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
            coverUrl = div_cover_image.select_one("img").attrs["src"]
            book = {
                "id" : i,
                "title": title,
                "isbn13": isbn,
                "description": None,
                "author": verfasser,
                "publisher": verlag,
                "year": jahr,
                "pages": umfang,
                "language": sprache,
                "coverurl": coverUrl,

            }

            book_data = book.copy()

            book_data.pop("author")
            add_book(**book_data)
            link_authors(book['id'] , book['author'])
            print(f"Book {book['title']} was scraped")
        except Exception as e:
            print(f"Error on id {i}: {e}")

            continue



def worker(amount, threads):
    part = amount // threads
    first = 1
    threads_array = []

    for i in range(1, threads + 1):
        if i == threads:
            end = amount
        else:
            end = first + part - 1

        t = Thread(target=scrape, args=(first, end))
        t.start()
        threads_array.append(t)

        first = end + 1
        time.sleep(THREAD_START_DELAY_SECONDS)

    for t in threads_array:
        t.join()



if __name__ == '__main__':
    worker(SCRAPE_AMOUNT , SCRAPE_THREADS)
