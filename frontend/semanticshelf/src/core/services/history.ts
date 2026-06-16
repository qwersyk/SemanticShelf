import { Injectable } from '@angular/core';
import { Book } from '../models/book.model';
import { filter } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class HistoryService {
  private readonly storageKey = 'visitedBooks';

  addBook(id: number) {
    const history = this.getBooks()

    const updatedHistory = [id , ...history.filter(book=> book !== id).slice(0, 10)];
    localStorage.setItem(this.storageKey , JSON.stringify(updatedHistory));


  }
  getBooks():number[]{
    const historyString =  localStorage.getItem(this.storageKey);
    if (!historyString) {

      return [];

    }
    return JSON.parse(historyString) as number[];
  }
  clearBooks():void{
    localStorage.setItem(this.storageKey , JSON.stringify([]));
  }
}
