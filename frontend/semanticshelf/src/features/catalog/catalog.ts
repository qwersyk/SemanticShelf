import { Component, computed, inject, signal } from '@angular/core';
import {BookApiService} from '../../core/services/book-api-service';
import {PreviewBook} from '../../core/models/preview-book';
import {PreviewBookComponent} from '../preview-book/preview-book';
import { LucideAngularModule,} from 'lucide-angular';
import {Router} from '@angular/router';
import {HistoryService } from '../../core/services/history';


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
  readonly error = signal('');
  private router = inject(Router);
  readonly query = signal(decodeURIComponent(this.router.url.valueOf().slice(8) ?? ""));
  readonly isSearchPage = computed(() => this.router.url.startsWith('/search'));
  private offset = 12;
  historyService = inject(HistoryService);


  searchBooks(): void {
    this.offset = 12;
    const query = this.query().trim();
    this.isLoading.set(true);
    if (!query) {
      this.books.set([]);
      return;
    }
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
    if(this.query()){
      this.searchBooks()

    }else {
      this.error.set('');
      this.isLoading.set(true);
      setTimeout(() => {
        this.api.postBooksRelevant(this.historyService.getBooks()).subscribe({
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
      }, 1000);
    }


  }


  goToSearch(): void {
    const query = this.query().trim();
    if (!query) {
      return;
    }
    this.searchBooks();
    this.router.navigate([`/search/${query}`]);
  }
  loadMoreBooks(): void {
    let newBooks: PreviewBook[] = []
      this.api.searchBook(this.query() , this.offset).subscribe({
        next: (results) => {
          newBooks = results.items;
          this.offset += newBooks.length;
          this.books.update(currentBooks => [...currentBooks, ...newBooks]);
        } , error: (err) => {
          this.error.set('Error occurred while loading books');
        }
      })


  }
  back(): void {
    this.offset = 12;
    this.router.navigate(['/']);
  }
  ngOnInit() {
    this.startPage();
  }
}
