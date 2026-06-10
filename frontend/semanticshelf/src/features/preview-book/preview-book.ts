import {Component, input} from '@angular/core';
import {PreviewBook} from '../../core/models/preview-book';
import { BookCover } from '../../shared/book-cover/book-cover';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-preview-book',
  imports: [BookCover, RouterLink],
  templateUrl: './preview-book.html',
  styleUrl: './preview-book.scss',
})
export class PreviewBookComponent {
  readonly book = input.required<PreviewBook>();
}
