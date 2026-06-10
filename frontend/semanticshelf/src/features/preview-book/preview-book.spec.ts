import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PreviewBook } from './preview-book';

describe('PreviewBook', () => {
  let component: PreviewBook;
  let fixture: ComponentFixture<PreviewBook>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PreviewBook],
    }).compileComponents();

    fixture = TestBed.createComponent(PreviewBook);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
