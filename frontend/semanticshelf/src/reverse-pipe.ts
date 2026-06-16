import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'reverseAuthor',

  standalone: true,
})
export class ReversePipe implements PipeTransform {
  transform(value: string[] | null | undefined): string {
    if (!value) {
      return '';
    }

    return value

      .map((v) => v.split(',').reverse().join(' '))

      .join(', ');
  }
}
