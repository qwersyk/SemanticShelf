import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BookSite } from './book-site';

describe('BookSite', () => {
  let component: BookSite;
  let fixture: ComponentFixture<BookSite>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BookSite],
    }).compileComponents();

    fixture = TestBed.createComponent(BookSite);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
