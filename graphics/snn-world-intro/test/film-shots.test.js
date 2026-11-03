import assert from 'node:assert/strict';
import test from 'node:test';
import { FILM_DURATION, FILM_SHOTS, getFilmPhase, getFilmShot } from '../src/film-shots.js';

test('six storyboard clips cover the complete film once, including the opening and S exit', () => {
  assert.equal(FILM_SHOTS.length, 6);
  assert.equal(FILM_SHOTS[0].start, 0);
  assert.equal(FILM_DURATION, 24);
  assert.equal(new Set(FILM_SHOTS.map(shot => shot.id)).size, FILM_SHOTS.length);
  let total = 0;
  for (const [index, shot] of FILM_SHOTS.entries()) {
    assert.ok(shot.end > shot.start);
    if (index > 0) assert.equal(shot.start, FILM_SHOTS[index - 1].end, 'clips have no gaps or overlaps');
    assert.equal(shot.number, String(index + 1).padStart(2, '0'));
    assert.ok(shot.description && shot.range && shot.title);
    assert.equal(getFilmShot((shot.start + shot.end) / 2), shot);
    total += shot.end - shot.start;
  }
  assert.equal(total, FILM_DURATION);
  assert.deepEqual(FILM_SHOTS.map(({ id, start, end }) => [id, start, end]), [
    ['opening', 0, 6], ['pacific', 6, 11.9], ['approach', 11.9, 14],
    ['weave', 14, 17.4], ['reveal', 17.4, 20], ['crossing', 20, 24],
  ]);
});

test('phase labels change at the clip boundaries and survive globe-clock round trips', () => {
  for (const [index, shot] of FILM_SHOTS.entries()) {
    assert.equal(getFilmPhase(shot.start), shot.phase);
    assert.equal(getFilmShot((shot.start - 6) + 6), shot);
    if (index > 0) assert.equal(getFilmShot(shot.start - 1e-6), FILM_SHOTS[index - 1]);
  }
  assert.equal(getFilmPhase(0), '01 · THROUGH THE INK');
  assert.equal(getFilmPhase(24), '06 · ACROSS THE WORLD');
  assert.equal(getFilmShot(-1), FILM_SHOTS[0]);
  assert.equal(getFilmShot(25), FILM_SHOTS.at(-1));
});
