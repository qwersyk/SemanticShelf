import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BookCover } from './book-cover';

describe('BookCover', () => {
  let component: BookCover;
  let fixture: ComponentFixture<BookCover>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BookCover],
    }).compileComponents();

    fixture = TestBed.createComponent(BookCover);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
