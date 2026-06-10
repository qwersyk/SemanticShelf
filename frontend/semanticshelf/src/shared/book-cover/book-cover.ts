import { Component, computed, input } from '@angular/core';
import { PreviewBook } from '../../core/models/preview-book';

const COVER_PALETTES = [
  { bg: '#D15B47', fg: '#FFFDF9', accent: '#F2D388' },
  { bg: '#123C55', fg: '#F7F4E8', accent: '#E5B769' },
  { bg: '#295C4E', fg: '#FFF8EC', accent: '#DFAE72' },
  { bg: '#5A334A', fg: '#FFF7F1', accent: '#E8A0A8' },
  { bg: '#2E2A24', fg: '#FAF1DD', accent: '#C9A66B' },
  { bg: '#6E3F2B', fg: '#FFF8EA', accent: '#E7C16F' },
];

@Component({
  selector: 'app-book-cover',
  templateUrl: './book-cover.html',
  styleUrl: './book-cover.scss',
})
export class BookCover {
  readonly book = input.required<PreviewBook>()

  readonly palette = computed(() => {
    const hash = Array.from(this.book().title).reduce((sum, char) => sum + char.charCodeAt(0), 0);
    return COVER_PALETTES[hash % COVER_PALETTES.length];
  });
}
