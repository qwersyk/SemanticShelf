# Pflichtenheft

## Projekt: SemanticShelf

## 1. Ausgangslage

Die HTL-Bibliothek besitzt eine bestehende Website zur Buchsuche. Die aktuelle Oberfläche ist jedoch veraltet und wenig
benutzerfreundlich. Die Suche nach Büchern ist teilweise umständlich und liefert nicht immer passende Ergebnisse.

Das Projekt wird durchgeführt, um die Bedienung der Website zu verbessern und eine moderne Suchfunktion bereitzustellen.

---

## 2. Ist-Zustand

Derzeit gibt es eine einfache Website für die HTL-Bibliothek. Die Suche funktioniert hauptsächlich über direkte
Begriffe. Ähnliche oder inhaltlich verwandte Suchbegriffe werden nicht ausreichend berücksichtigt.

Schwächen des aktuellen Systems:

* veraltete Benutzeroberfläche
* unübersichtliche Darstellung
* einfache, nicht-semantische Suche
* längere Suchzeit für passende Bücher
* keine modernen Empfehlungen oder ähnlichen Bücher

---

## 3. Zielsetzung

Ziel ist die Entwicklung einer modernen Webanwendung für die HTL-Bibliothek. Benutzerinnen und Benutzer sollen Bücher
einfacher, schneller und genauer finden können.

### Ziele

* moderne und übersichtliche Benutzeroberfläche
* semantische Suche mithilfe von Embeddings
* Anzeige relevanter oder ähnlicher Bücher

### Nicht-Ziele

Nicht umgesetzt werden:

* Benutzerprofile
* Login-System
* Ausleihverwaltung
* Marketingfunktionen
* manuelles Eintragen aller Bücher durch das Projektteam

---

## 4. Anforderungen

### Funktionale Anforderungen

| Nr.  | Anforderung                                                                                | Priorität |
|------|--------------------------------------------------------------------------------------------|-----------|
| FA01 | Das System muss die importierten Buchdaten aus der Datenbank abrufen können.               | Muss      |
| FA02 | Das System muss eine semantische Suche über die vorhandenen Buchdaten ermöglichen.         | Muss      |
| FA03 | Das System muss Suchergebnisse als Liste anzeigen können.                                  | Muss      |
| FA04 | Das System muss zu jedem Buch eine Detailseite anzeigen können.                            | Muss      |
| FA05 | Das System muss relevante bzw. ähnliche Bücher zu einem ausgewählten Buch anzeigen können. | Muss      |
| FA06 | Das Backend muss einen API-Endpunkt für die Buchsuche bereitstellen.                       | Muss      |
| FA07 | Das Backend muss einen API-Endpunkt für Buchdetails bereitstellen.                         | Muss      |
| FA08 | Das Backend muss einen API-Endpunkt für relevante Bücher bereitstellen.                    | Muss      |
| FA09 | Das Frontend muss die Daten über das Backend abrufen und darstellen können.                | Muss      |
| FA10 | Das System soll einen Bereich „For you“ mit Buchempfehlungen anzeigen können.              | Soll      |
| FA11 | Das System kann Bücher nach Genre anzeigen.                                                | Kann      |

### Nicht-funktionale Anforderungen

| Nr.  | Anforderung                                                                          | Priorität |
|------|--------------------------------------------------------------------------------------|-----------|
| NF01 | Die Website muss übersichtlich und benutzerfreundlich sein.                          | Muss      |
| NF02 | Die Suchergebnisse sollen innerhalb kurzer Zeit angezeigt werden.                    | Soll      |
| NF03 | Die Anwendung soll auf Desktop-Geräten gut nutzbar sein.                             | Muss      |
| NF04 | Die Datenbankstruktur soll klar und nachvollziehbar sein.                            | Muss      |
| NF06 | Das System soll so aufgebaut sein, dass weitere Bücher später ergänzt werden können. | Soll      |

---

## 5. UI-Konzept

Die Webanwendung besteht aus mehreren einfachen Seiten.

| Seite / Komponente | Beschreibung                                                     |
|--------------------|------------------------------------------------------------------|
| Startseite         | Einstieg in die Anwendung mit Suchmöglichkeit und Empfehlungen   |
| Suchseite          | Eingabe eines Suchbegriffs und Anzeige der Suchergebnisse        |
| Buch-Komponente    | Darstellung eines einzelnen Buches in einer Liste oder Übersicht |
| BuchdSeite         | Anzeige genauer Informationen zu einem Buch                      |
| For-you-Komponente | Anzeige relevanter oder empfohlener Bücher                       |
| Verlauf Komponente | Anzeige zuletzt angesehener Bücher                               |

Das Design soll modern, schlicht und übersichtlich sein. Die Benutzerinnen und Benutzer sollen ohne Erklärung nach
Büchern suchen und Ergebnisse öffnen können.

---

## 6. Lieferobjekte

| Lieferobjekt      | Beschreibung                                                   | Abnahmekriterium                                         |
|-------------------|----------------------------------------------------------------|----------------------------------------------------------|
| Frontend          | Angular-Webanwendung mit Startseite, Suche und Buchdetailseite | Die wichtigsten Seiten sind aufrufbar und bedienbar      |
| Backend           | FastAPI-Anwendung mit API-Endpunkten                           | Such- und Buchdaten können über die API abgefragt werden |
| Datenbank         | PostgreSQL-Datenbank mit Buchdaten und Vektoren                | Bücher und Vektoren sind gespeichert                     |
| Semantische Suche | Suche mithilfe von Embeddings                                  | Die Suche liefert passende Bücher                        |
| Dokumentation     | Kurze technische Dokumentation                                 | Architektur, API, Datenbank und Setup sind beschrieben   |

---

# Technische Dokumentation

## 7. Architektur

Das System besteht aus drei Hauptteilen:

```text
Angular Frontend  →  FastAPI Backend  →  PostgreSQL Datenbank
```

### Beschreibung

* Das **Frontend** wird mit Angular umgesetzt.
* Das **Backend** wird mit FastAPI umgesetzt.
* Die **Datenbank** wird mit PostgreSQL umgesetzt.
* Für die semantische Suche werden Embeddings verwendet.
* Die Embeddings werden über ein Embedding-Modell erzeugt und als Vektoren gespeichert.

---

## 8. Datenkatalog

| Tabelle    | Zweck                                                  |
|------------|--------------------------------------------------------|
| books      | Speicherung der Buchinformationen                      |
| embeddings | Speicherung der Buchvektoren für die semantische Suche |

### Felder

| Tabelle    | Felder                                                                                                                                                                 |
|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| books      | id, title, author, year, description, language, cover_image_url, isbn, publisher, classification, pages, annotation, signature_line1, signature_line2, signature_color |
| embeddings | id, book_id, vector                                                                                                                                                    |

---

## 9. ERD

Das Entity-Relationship-Diagramm beschreibt die Beziehungen zwischen den wichtigsten Daten.

```text
books 1 ─── 1 embeddings
```

### Beschreibung

Ein Buch besitzt einen zugehörigen Vektor für die semantische Suche.

---

## 10. API-Dokumentation

| Methode | Pfad                     | Beschreibung                              |
|---------|--------------------------|-------------------------------------------|
| GET     | /api/books/search        | Sucht Bücher anhand eines Suchbegriffs    |
| GET     | /api/books/{id}          | Gibt die Details zu einem Buch zurück     |
| GET     | /api/books/{id}/relevant | Gibt ähnliche Bücher zu einem Buch zurück |
| POST    | /api/books/relevant      | Gibt allgemein relevante Bücher zurück    |

### Beispiel: Suche

```http
GET /api/books/search?q=1984
```

### Beispielhafte Antwort

```json
[
  {
    "id": 1,
    "title": "1984 : Roman",
    "author": "Orwell, George",
    "cover_image_url": "https://images.littera.eu/image/KeYAtqESLROpw0UM/9783548234106/m"
  }
]
```

---

## 11. Setup

Für die Ausführung des Systems werden benötigt:

* Node.js
* Angular CLI
* Python
* FastAPI
* PostgreSQL
* benötigte Python- und npm-Pakete

### Start des Frontends

```bash
npm install
ng serve
```

### Start des Backends

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 12. Testkonzept

Die wichtigsten Muss-Anforderungen werden durch einfache Testfälle überprüft.

| Testfall | Beschreibung                    | Erwartetes Ergebnis                        |
|----------|---------------------------------|--------------------------------------------|
| TC01     | Startseite öffnen               | Die Startseite wird korrekt angezeigt      |
| TC02     | Suchbegriff eingeben            | Suchergebnisse werden angezeigt            |
| TC03     | Buch öffnen                     | Die Detailseite des Buches wird angezeigt  |
| TC04     | Semantische Suche testen        | Inhaltlich passende Bücher werden gefunden |
| TC05     | API-Endpunkt für Suche aufrufen | Das Backend liefert gültige JSON-Daten     |
| TC06     | Datenbank prüfen                | Buchdaten und Vektoren sind gespeichert    |
| TC07     | Relevante Bücher anzeigen       | Ähnliche Bücher werden angezeigt           |

---

## 13. Abnahme

Das Projekt gilt als abgenommen, wenn:

* die Website gestartet werden kann
* Bücher über die Suche gefunden werden können
* eine Buchdetailseite funktioniert
* die semantische Suche grundsätzlich passende Ergebnisse liefert
* Frontend, Backend und Datenbank zusammenarbeiten
* die wichtigsten Muss-Anforderungen erfüllt sind
