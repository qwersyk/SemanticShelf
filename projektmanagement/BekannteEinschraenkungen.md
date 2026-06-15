## Bekannte Einschränkungen

### Embedding API

- Sehr große Texte können langsam verarbeitet werden
- Modell lädt beim ersten Start relativ lange

### SemanticShelf API

- Die Suche funktioniert nur für Bücher, für die bereits Embeddings gespeichert wurden
- Für die semantische Suche muss das Embedding API erreichbar sein
- Empfehlungen basieren aktuell nur auf Titel und Autor, nicht auf der Beschreibung
- Filter nach Jahr oder Sprache sind noch nicht implementiert
