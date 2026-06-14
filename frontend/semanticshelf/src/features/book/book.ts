import { Component, inject, input, signal } from '@angular/core';
import {LucideAngularModule} from 'lucide-angular';
import {Book} from '../../core/models/book.model';
import { PreviewBook } from '../../core/models/preview-book';
import { BookCover } from '../../shared/book-cover/book-cover';
import { Router } from '@angular/router';

@Component({
  selector: 'app-book',
  imports: [LucideAngularModule, BookCover],
  templateUrl: './book.html',
  styleUrl: './book.scss',
})
export class BookComponent {
  readonly book = input.required<Book>();



}
