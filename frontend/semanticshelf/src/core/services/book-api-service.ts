import {inject, Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {PreviewBook} from '../models/preview-book';
import {Book} from '../models/book.model';


@Injectable({
  providedIn: 'root',
})
export class BookApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'https://semanticshelf.qsk.me';

  searchBook(query: string , offset = 0 ,limit = 10) {
    const params = new HttpParams();
    params.set('q', query);
    params.set('offset', offset);
    params.set('limit', limit);
    return this.http.get<PreviewBook[]>(`${this.baseUrl}/api/books/search`, {params: params});
  }
  getBookById(id: number) {
    return this.http.get<Book>(`${this.baseUrl}/api/books/${id}`);
  }
  getBookByIdRelevant(id: number) {
    return this.http.get<PreviewBook[]>(`${this.baseUrl}/api/books/${id}/relevant`);
  }
  postBooksRelevant(bookIds:number[] ,offset = 0 ,limit = 10 ) {
    return this.http.post(`${this.baseUrl}/api/books/relevant`, {book_ids: bookIds , offset: offset , limit: limit});
  }





}
