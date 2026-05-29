from dotenv import load_dotenv
from os import getenv

load_dotenv()

DATABASE_URL = getenv("DATABASE_URL")
DATABASE_SCHEMA = getenv("DATABASE_SCHEMA", "semanticshelf")
EMBEDDING_API_URL = getenv("EMBEDDING_API_URL", "http://localhost:8000")
EMBEDDING_API_KEY = getenv("EMBEDDING_API_KEY", "secret")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")