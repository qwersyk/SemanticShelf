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