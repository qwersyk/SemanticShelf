# Testkonzept

## Backend – Embedding API

| Testfall                         | Beschreibung                  | Erwartetes Ergebnis                         |
|----------------------------------|-------------------------------|---------------------------------------------|
| GET /health                      | Prüfung des Health-Endpunkts  | Status 200 und gültige Statusmeldung        |
| GET /model mit falschem API-Key  | Zugriff mit falschem API-Key  | Status 401 Unauthorized                     |
| GET /model mit gültigem API-Key  | Abruf der Modellinformationen | Modelldaten werden zurückgegeben            |
| POST /embed mit gültigen Daten   | Erstellung von Embeddings     | Embeddings werden erfolgreich zurückgegeben |
| POST /embed mit falschem API-Key | Anfrage mit falschem API-Key  | Status 401 Unauthorized                     |
| POST /embed mit leerer Textliste | Ungültige Eingabedaten        | Status 400 Bad Request                      |

## Backend – SemanticShelf API

| Testfall                                    | Beschreibung                                  | Erwartetes Ergebnis                             |
|---------------------------------------------|-----------------------------------------------|-------------------------------------------------|
| GET /api/health                             | Prüfung des Health-Endpunkts                  | Status 200 und gültige Statusmeldung            |
| GET /api/books/search                       | Semantische Suche mit Suchbegriff             | Bücher werden nach Vektor-Ähnlichkeit geliefert |
| GET /api/books/search nur mit author-Filter | Suche ohne Suchtext, nur mit Autor-Filter     | Bücher des angegebenen Autors werden geliefert  |
| GET /api/books/search leer                  | Suche mit leerem Suchbegriff                  | Status 400 Bad Request                          |
| GET /api/books/{id}                         | Abruf von Buchdetails                         | Buchdetails werden zurückgegeben                |
| GET /api/books/{id} unbekannt               | Abruf eines nicht existierenden Buchs         | Status 404 Not Found                            |
| GET /api/books/{id}/genres                  | Abruf passender Genres zu einem Buch          | Genres mit Wahrscheinlichkeit werden geliefert  |
| GET /api/books/{id}/genres unbekannt        | Genres für ein nicht existierendes Buch       | Status 404 Not Found                            |
| GET /api/books/{id}/relevant                | Abruf ähnlicher Bücher zu einem Buch          | Ähnliche Bücher werden zurückgegeben            |
| GET /api/books/{id}/relevant unbekannt      | Ähnliche Bücher für nicht existierendes Buch  | Status 404 Not Found                            |
| POST /api/books/relevant                    | Empfehlungen anhand mehrerer gelesener Bücher | Relevante Bücher werden zurückgegeben           |

Die Unit-Tests des SemanticShelf API verwenden gemockte Datenbank- und Embedding-Funktionen. Dadurch werden die
API-Endpunkte getestet, ohne dass eine echte PostgreSQL-Datenbank oder ein laufendes Embedding API notwendig ist.

## TODO

- [ ] Frontend-Tests ergaenzen, sobald das Frontend implementiert ist.
