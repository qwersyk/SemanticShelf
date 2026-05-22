# Testkonzept

## Backend – Embedding API

| Testfall                         | Beschreibung                   | Erwartetes Ergebnis                         |
|----------------------------------|--------------------------------|---------------------------------------------|
| GET /health                      | Prüfung des Health-Endpunkts   | Status 200 und gültige Statusmeldung        |
| GET /model ohne API-Key          | Zugriff ohne Authentifizierung | Status 401 Unauthorized                     |
| GET /model mit gültigem API-Key  | Abruf der Modellinformationen  | Modelldaten werden zurückgegeben            |
| POST /embed mit gültigen Daten   | Erstellung von Embeddings      | Embeddings werden erfolgreich zurückgegeben |
| POST /embed ohne API-Key         | Anfrage ohne Authentifizierung | Status 401 Unauthorized                     |
| POST /embed mit leerer Textliste | Ungültige Eingabedaten         | Status 400 Bad Request                      |