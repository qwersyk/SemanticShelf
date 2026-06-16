# SemanticShelf

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/search-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="docs/screenshots/search-light.png">
  <img alt="Search" src="docs/screenshots/search-light.png">
</picture>

SemanticShelf ist eine Webanwendung für die HTL-Bibliothek. Bücher können gesucht, geöffnet und über Embeddings passende ähnliche Bücher gefunden werden.

## Projektstruktur

- `backend/database` - SQL-Schema
- `backend/embedding-api` - FastAPI-Service für Embeddings
- `backend/semanticshelf-api` - FastAPI-Backend für Bücher, Suche und Empfehlungen
- `backend/scripts` - Scraper, Embedding- und Cover-Skripte
- `frontend/semanticshelf` - Angular-Frontend
- `projektmanagement` - Projektdokumentation

## Screenshots

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/book-detail-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="docs/screenshots/book-detail-light.png">
  <img alt="Buchdetail" src="docs/screenshots/book-detail-light.png">
</picture>

## Voraussetzungen

- PostgreSQL mit pgvector
- Python 3
- Node.js und npm
- Optional: Docker

## Datenbank vorbereiten

```bash
psql "postgresql://user:password@host:5432/database" -f backend/database/schema.sql
```

Für die Python-Services wird danach `DATABASE_URL` als SQLAlchemy-URL gesetzt.

## Daten importieren

```bash
cd backend/scripts
pip install -r requirements.txt
```

Beispiel für `backend/scripts/.env`:

```env
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/database
DATABASE_SCHEMA=semanticshelf
EMBEDDING_API_URL=http://localhost:8000
EMBEDDING_API_KEY=secret
```

Bibliotheksdaten laden:

```bash
python3 scraper.py --start 1 --end 8000
```

## Embedding API starten

```bash
cd backend/embedding-api
pip install -r requirements.txt
API_KEY=secret uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Optional mit Docker:

```bash
cd backend/embedding-api
docker build -t semanticshelf-embedding .
docker run --rm -p 8000:8000 -e API_KEY=secret semanticshelf-embedding
```

## Embeddings und Zusatzdaten erstellen

```bash
cd backend/scripts
python3 embed_books.py --start 1 --end 8000
python3 seed_genres.py
python3 update_cover_urls.py --start 1 --end 8000
```

`update_cover_urls.py` ist optional. Es verbessert fehlende oder unpassende Cover-URLs.

## Backend API starten

Beispiel für `backend/semanticshelf-api/.env`:

```env
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/database
DATABASE_SCHEMA=semanticshelf
EMBEDDING_API_URL=http://localhost:8000
EMBEDDING_API_KEY=secret
CORS_ALLOW_ALL=true
```

Start:

```bash
cd backend/semanticshelf-api
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Optional mit Docker:

```bash
cd backend/semanticshelf-api
docker build -t semanticshelf-api .
docker run --rm -p 8001:8000 --env-file .env semanticshelf-api
```

## Frontend starten

Die Backend-URL wird in `frontend/semanticshelf/src/environments/environment.ts` gesetzt:

```ts
export const environment = {
  apiUrl: 'http://localhost:8001',
};
```

Start:

```bash
cd frontend/semanticshelf
npm install
npm start
```

Optional mit Docker:

```bash
cd frontend/semanticshelf
docker build -t semanticshelf-frontend .
docker run --rm -p 3000:3000 semanticshelf-frontend
```

## Tests

```bash
cd backend/embedding-api
python3 -m pytest -q
```

```bash
cd backend/semanticshelf-api
python3 -m pytest -q
```

## Dokumentation

Die Projektdokumentation liegt in `projektmanagement/`.
