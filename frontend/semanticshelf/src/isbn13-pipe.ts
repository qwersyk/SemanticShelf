import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'isbn13',
  standalone: true,
})
export class Isbn13Pipe implements PipeTransform {
  transform(value: string | number | null | undefined): string {
    if (value === null || value === undefined) {
      return '';
    }

    const isbn = String(value).replace(/[^0-9]/g, '');

    if (isbn.length !== 13) {
      return String(value);
    }

    return isbn.replace(
      /^(\d{3})(\d)(\d{3})(\d{5})(\d)$/,
      '$1-$2-$3-$4-$5',
    );
  }
}
