# Testprotokoll

## Backend - Embedding API

| Testfall                         | Erwartetes Ergebnis               | Ergebnis                     | Status    | Datum      |
|----------------------------------|-----------------------------------|------------------------------|-----------|------------|
| GET /health                      | 200 OK und Statusmeldung          | Funktioniert korrekt         | Bestanden | 22.05.2026 |
| GET /model ohne API-Key          | 401 Unauthorized                  | Fehler korrekt zurückgegeben | Bestanden | 22.05.2026 |
| GET /model mit gültigem API-Key  | Modelldaten werden geliefert      | Erfolgreich                  | Bestanden | 22.05.2026 |
| POST /embed mit gültigen Daten   | Embeddings werden zurückgegeben   | Erfolgreich                  | Bestanden | 22.05.2026 |
| POST /embed ohne API-Key         | 401 Unauthorized                  | Fehler korrekt zurückgegeben | Bestanden | 22.05.2026 |
| POST /embed mit leerer Textliste | 400 Bad Request mit Fehlermeldung | Fehler korrekt zurückgegeben | Bestanden | 22.05.2026 |

## Testumgebung

- Betriebssystem: macOS
- Python-Version: 3.14.3
- Testframework: pytest
- API-Framework: FastAPI

## Testausführung

Die Tests wurden mit folgendem Befehl ausgeführt:

```bash
cd backend/embedding-api
python3 -m pytest
```

`Ergebnis: 6 passed in 10.66s`

## Backend - SemanticShelf API

| Testfall                               | Erwartetes Ergebnis              | Ergebnis                     | Status    | Datum      |
|----------------------------------------|----------------------------------|------------------------------|-----------|------------|
| GET /api/health                        | 200 OK und Statusmeldung         | Funktioniert korrekt         | Bestanden | 29.05.2026 |
| GET /api/books/search                  | Bücher werden zurückgegeben      | Erfolgreich                  | Bestanden | 02.06.2026 |
| GET /api/books/search leer             | 400 Bad Request                  | Fehler korrekt zurückgegeben | Bestanden | 02.06.2026 |
| GET /api/books/{id}                    | Buchdetails werden geliefert     | Erfolgreich                  | Bestanden | 02.06.2026 |
| GET /api/books/{id} unbekannt          | 404 Not Found                    | Fehler korrekt zurückgegeben | Bestanden | 02.06.2026 |
| GET /api/books/{id}/relevant           | Ähnliche Bücher werden geliefert | Erfolgreich                  | Bestanden | 02.06.2026 |
| GET /api/books/{id}/relevant unbekannt | 404 Not Found                    | Fehler korrekt zurückgegeben | Bestanden | 02.06.2026 |
| POST /api/books/relevant               | Empfehlungen werden geliefert    | Erfolgreich                  | Bestanden | 02.06.2026 |

## Testausführung SemanticShelf API

Die Unit-Tests wurden mit folgendem Befehl ausgeführt:

```bash
cd semanticshelf-api
python3 -m pytest -q
```

`Ergebnis: 8 passed, 1 skipped in 0.39s`