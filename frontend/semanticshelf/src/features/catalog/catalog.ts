import {Component, inject, signal} from '@angular/core';
import {BookApiService} from '../../core/services/book-api-service';
import {HttpClient} from '@angular/common/http';
import {PreviewBook} from '../../core/models/preview-book';
import {PreviewBookComponent} from '../preview-book/preview-book';
import { LucideAngularModule } from 'lucide-angular';
;

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [PreviewBookComponent, LucideAngularModule],
  templateUrl: './catalog.html',
  styleUrl: './catalog.scss',
})
export class Catalog {
  private readonly api = inject(BookApiService);
  readonly books = signal<PreviewBook[]>([]);
  readonly isLoading = signal<boolean>(false);
  readonly query = signal('');
  readonly error = signal('');

  searchBooks(): void {
    const query = this.query().trim();
    if (!query) {
      this.books.set([]);
      return;
    }
    this.isLoading.set(true);
    this.api.searchBook(this.query()).subscribe({
      next: (results) => {
        this.books.set(results.items);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.error.set('Error occurred while searching books');
        this.isLoading.set(false);
      },
    });
  }
  startPage(): void {
    this.error.set('');
    this.isLoading.set(true);
    this.api.postBooksRelevant([]).subscribe({
      next: (results) => {
        this.books.set(results.items ?? []);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.error.set('Error occurred while loading books');
        this.books.set([]);
        this.isLoading.set(false);
      },
    });
  }
  ngOnInit() {
    this.startPage();
  }
}
