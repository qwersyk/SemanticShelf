import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { PreviewBook } from '../../core/models/preview-book';
import { Book } from '../../core/models/book.model';
import { BookComponent } from '../book/book';
import { BookApiService } from '../../core/services/book-api-service';
import { comment } from 'postcss';

@Component({
  selector: 'app-book-site',
  imports: [BookComponent],
  templateUrl: './book-site.html',
  styleUrl: './book-site.scss',
})
export class BookSite {
  readonly isLoading = signal<boolean>(false);
  readonly error = signal('');
  private router = inject(Router);
  readonly book_id = signal(decodeURIComponent(this.router.url.valueOf().slice(6) ?? ''));
  book = signal<Book | null>(null);
  private readonly api = inject(BookApiService);

  ngOnInit() {
    this.getBook();


  }
  getBook(){
    if(this.book_id()){
      this.api.getBookById(Number(this.book_id())).subscribe({ next: (book) => { this.book.set(book);console.log(book); } ,
        error: err => {this.error.set("Failure during loading the book")}
      });
    }
  }



}
