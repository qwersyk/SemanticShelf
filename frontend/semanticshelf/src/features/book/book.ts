import {Component, input} from '@angular/core';

@Component({
  selector: 'app-book',
  imports: [],
  templateUrl: './book.html',
  styleUrl: './book.scss',
})
export class Book {
  readonly book = input.required<Book>();
}
