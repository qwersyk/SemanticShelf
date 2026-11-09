export interface Book {
  id: number;
  title: string;
  authors: string[];
  year: number | null;
  language: string | null;
  cover_url: string | null;
  score: number | null;
  description: string | null;
  isbn13: string | null;
  publisher: string | null;
  pages: number | null;
  description_needs_review?: boolean | null;
  description_basis?: string | null;
}
