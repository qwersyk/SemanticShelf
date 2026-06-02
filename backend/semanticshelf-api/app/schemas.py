from pydantic import BaseModel, Field


class BookSummary(BaseModel):
    id: int
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    language: str | None = None
    cover_url: str | None = None
    score: float | None = None


class BookDetail(BookSummary):
    description: str | None = None
    isbn13: str | None = None
    publisher: str | None = None
    pages: int | None = None


class BookListResponse(BaseModel):
    items: list[BookSummary]
    total: int | None = None
    offset: int
    limit: int


class RelevantRequest(BaseModel):
    book_ids: list[int] = Field(min_length=0)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=50)
