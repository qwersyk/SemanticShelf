import { Isbn13Pipe } from './isbn13-pipe';

describe('Isbn13Pipe', () => {
  it('create an instance', () => {
    const pipe = new Isbn13Pipe();
    expect(pipe).toBeTruthy();
  });
});
