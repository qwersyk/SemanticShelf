import json
import re
import webcolors
import requests
from bs4 import BeautifulSoup
books = []

def find_row(string , soup):
    try:
        return soup.find("td" , class_="label" ,string= string).find_parent("tr").find("td" , class_="data").get_text().strip()
    except:
        return None

def wiki_row(soup):
    try:
        return soup.find("td", class_="label", string="Verfasser").find_parent("tr").find("td", class_="data").find_all("a")[
            1].get("href")
    except:
        return None




def scrape():
    for i in range(1 ,8000):
        url = f'https://htl-stp.bibbs.cc/search?mode=stb&q=&critCount=3&crit_0=&op_0=&crit_1=&op_1=AND&ma=0&exAnz=0&flt=Alle&gradeFlt=&sort_0=Systematik&sort_1=Haupteintrag&sort_2=Haupttitel&page=1&view=detail&page_size=10&id=0.{i}'
        response = requests.get(url)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'html.parser')

        div = soup.select_one("div.detailData")
        title = div.select_one("h3").text
        if not title:
            continue
        div_2 = soup.select_one("div.signaturetikett").find_all("div")
        ort = find_row("Ort", soup)
        abkuerzung = div_2[0].text
        if div_2[1].get("style")[18:25]:
            try:
                color = webcolors.hex_to_name(div_2[1].get("style")[18:25])
            except:
                color = None
        else:
            color = None
        medienart = find_row("Medienart", soup)
        isbn = find_row("ISBN", soup)
        verfasser = find_row("Verfasser", soup)
        verfasserWiki = wiki_row(soup)
        verlag = find_row("Verlag", soup)
        jahr = find_row("Jahr", soup)
        umfang = find_row("Umfang", soup)
        sprache = find_row("Sprache", soup)
        verfasserangabe = find_row("Verfasserangabe", soup)
        annotation = find_row("Annotation", soup)
        book = {
            "id" :f"0.{i}",
            "title": title,
            "medienart": medienart,
            "isbn": isbn,
            "author": verfasser,
            "ort": ort,
            "abkuerzung": abkuerzung,
            "color": color,
            "verfasserWiki": verfasserWiki,
            "verlag": verlag,
            "jahr": jahr,
            "umfang": umfang,
            "sprache": sprache,
            "verfasserangabe": verfasserangabe,
            "annotation": annotation,

        }


        books.append(book)
        print(f"Book {book['title']} was scraped")
    print(books)
    with open("books.json", "w", encoding="utf-8") as file:

        json.dump(books, file, ensure_ascii=False, indent=4)




def clean_str(string):
    return re.sub(r'\d+', '', string)


if __name__ == '__main__':
    scrape()