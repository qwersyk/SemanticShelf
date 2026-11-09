from os import getenv

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DATABASE_URL = getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://','postgresql+psycopg2://',1)
DATABASE_SCHEMA = getenv("DATABASE_SCHEMA", "semanticshelf")
EMBEDDING_API_URL = getenv("EMBEDDING_API_URL", "http://localhost:8000")
EMBEDDING_API_KEY = getenv("EMBEDDING_API_KEY", "secret")
CORS_ALLOW_ALL = getenv("CORS_ALLOW_ALL", "false").lower() == "true"
SEARCH_PROVIDER = getenv("SEARCH_PROVIDER", "legacy")
OPENAI_API_KEY = getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
OPENAI_EMBEDDING_DIMENSIONS = 1536

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")
