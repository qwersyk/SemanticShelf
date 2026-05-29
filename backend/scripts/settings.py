from dotenv import load_dotenv
from os import getenv

load_dotenv()

DATABASE_URL = getenv("DATABASE_URL")
DATABASE_SCHEMA = getenv("DATABASE_SCHEMA", "semanticshelf")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")