import { Component, inject, input } from '@angular/core';
import {PreviewBook} from '../../core/models/preview-book';
import { BookCover } from '../../shared/book-cover/book-cover';
import { Router } from '@angular/router';
import { HistoryService } from '../../core/services/history';

@Component({
  selector: 'app-preview-book',
  imports: [BookCover],
  templateUrl: './preview-book.html',
  styleUrl: './preview-book.scss',
})
export class PreviewBookComponent {
  readonly book = input.required<PreviewBook>();
  historyService = inject(HistoryService);
  router = inject(Router);

  clickBook(){
    this.historyService.addBook(this.book().id)
    this.router.navigate(['book' , this.book().id])


  }
}
