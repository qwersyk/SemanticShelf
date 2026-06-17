import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { PreviewBook } from '../../core/models/preview-book';
import { Book } from '../../core/models/book.model';
import { BookComponent } from '../book/book';
import { BookApiService } from '../../core/services/book-api-service';
import { PreviewBookComponent } from '../preview-book/preview-book';

@Component({
  selector: 'app-book-site',
  imports: [BookComponent, PreviewBookComponent],
  templateUrl: './book-site.html',
  styleUrl: './book-site.scss',
})
export class BookSite {
  readonly isLoading = signal<boolean>(false);
  readonly error = signal('');
  protected router = inject(Router);
  readonly book_id = signal(decodeURIComponent(this.router.url.valueOf().slice(6) ?? ''));
  book = signal<Book | null>(null);
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(BookApiService);

  recommendedBooks= signal<PreviewBook[] | null>(null);

  ngOnInit() {
    this.route.paramMap.subscribe(param => {
      const id = param.get("id")
      if(id){
        this.book.set(null)
        this.recommendedBooks.set(null)
        window.scrollTo(0, 0);
        this.book_id.set(id);
        this.getBook();
        this.getRecommendedBooks();
      }
    })
  }
  getBook() {
    this.isLoading.set(true);
      if (this.book_id()) {
        this.api.getBookById(Number(this.book_id())).subscribe({
          next: (book) => {
            this.book.set(book);
            this.isLoading.set(false);
          },
          error: (err) => {
            this.router.navigate(['/404']);
          },
        });
      }
  }
  getRecommendedBooks() {
    this.isLoading.set(true);
      if (this.book_id()) {
        this.api.postBooksRelevant([Number(this.book_id())]).subscribe({next: (books_return) => {
            this.recommendedBooks.set(books_return.items);
            this.isLoading.set(false);
          } , error: (err) => {
            this.error.set('Failure during loading recommended books');
          }})
      }

  }

  back(): void {
    this.router.navigate(['/']);
  }
}
