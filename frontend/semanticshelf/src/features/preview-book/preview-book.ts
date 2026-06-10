import {Component, input, Input} from '@angular/core';
import {PreviewBook} from '../../core/models/preview-book';

@Component({
  selector: 'app-preview-book',
  imports: [],
  templateUrl: './preview-book.html',
  styleUrl: './preview-book.scss',
})
export class PreviewBookComponent {
  readonly book = input.required<PreviewBook>();



}
