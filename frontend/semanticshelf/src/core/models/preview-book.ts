export interface PreviewBook {
  id: number;
  title: string;
  authors: string[];
  year: number | null;
  language: string | null;
  cover_url: string | null;
  score: number | null;
}
