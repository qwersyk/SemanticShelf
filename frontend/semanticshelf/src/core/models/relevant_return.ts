import {Book} from './book.model';
import {PreviewBook} from './preview-book';

export interface Relevant_return {
  items: PreviewBook[];
  limit: number;
  offset: number;
  total: number;
}
