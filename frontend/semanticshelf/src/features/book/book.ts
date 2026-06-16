import { Component, input } from '@angular/core';
import {LucideAngularModule} from 'lucide-angular';
import {Book} from '../../core/models/book.model';
import { BookCover } from '../../shared/book-cover/book-cover';
import { Isbn13Pipe } from '../../isbn13-pipe';
import { ReversePipe } from '../../reverse-pipe';

@Component({
  selector: 'app-book',
  imports: [LucideAngularModule, BookCover, Isbn13Pipe, ReversePipe],
  templateUrl: './book.html',
  styleUrl: './book.scss',
})
export class BookComponent {
  readonly book = input.required<Book>();


  openWebsite(): void {
    window.location.href = `https://htl-stp.bibbs.cc/search?view=detail&id=0.${this.book().id}`;
  }

}
