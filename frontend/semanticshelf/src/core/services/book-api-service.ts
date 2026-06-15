import {inject, Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {PreviewBook} from '../models/preview-book';
import {Book} from '../models/book.model';
import {Relevant_return} from '../models/relevant_return';


@Injectable({
  providedIn: 'root',
})
export class BookApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'https://semanticshelfapidev.qsk.me/';

  searchBook(query: string , offset = 0 ,limit = 12) {
    const params = new HttpParams().set('q', query).set('offset', offset).set('limit', limit);
    return this.http.get<Relevant_return>(`${this.baseUrl}/api/books/search`, {params: params});
  }
  getBookById(id: number) {
    return this.http.get<Book>(`${this.baseUrl}/api/books/${id}`);
  }
  getBookByIdRelevant(id: number) {
    return this.http.get<PreviewBook[]>(`${this.baseUrl}/api/books/${id}/relevant`);
  }
  postBooksRelevant(bookIds:number[] ,offset = 0 ,limit = 12 ) {
    return this.http.post<Relevant_return>(`${this.baseUrl}/api/books/relevant`, {book_ids: bookIds , offset: offset , limit: limit});
  }





}
