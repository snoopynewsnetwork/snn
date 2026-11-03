const formatTime = (time) => Number.isInteger(time) ? String(time).padStart(2, '0') : String(time);

// Full-film seconds, shared by the storyboard players and every phase label.
export const FILM_SHOTS = Object.freeze([
  {
    id: 'opening', title: 'Through the ink', start: 0, end: 6,
    description: 'A flat Snoopy profile opens through the ink into the globe.',
  },
  {
    id: 'pacific', title: 'Across the Pacific', start: 6, end: 11.9,
    description: 'Descend near Baja, then follow the broad arc past Alaska and Russia toward Japan.',
  },
  {
    id: 'approach', title: 'Behind the N', start: 11.9, end: 14,
    description: 'Rise from Earth toward the back of the trailing N and settle into the direction of travel.',
  },
  {
    id: 'weave', title: 'Between the letters', start: 14, end: 17.4,
    description: 'Fly outside the trailing N, inside the middle N, then past the S while looking along the track.',
  },
  {
    id: 'reveal', title: 'Back to Earth', start: 17.4, end: 20,
    description: 'Curve back toward Earth, then pull away as the separate forms resolve into SNN.',
  },
  {
    id: 'crossing', title: 'Across the world', start: 20, end: 24,
    description: 'Let the readable initials travel right to left across the globe into the closing view.',
  },
].map((shot, index) => Object.freeze({
  ...shot,
  number: String(index + 1).padStart(2, '0'),
  range: `${formatTime(shot.start)}–${formatTime(shot.end)}s`,
  phase: `${String(index + 1).padStart(2, '0')} · ${shot.title.toUpperCase()}`,
})));

export const FILM_DURATION = FILM_SHOTS.at(-1).end;

export function getFilmShot(seconds) {
  const time = Number.isFinite(seconds) ? Math.max(0, Math.min(FILM_DURATION, seconds)) : 0;
  // The editor converts between full-film and globe-only clocks. Treat a
  // boundary reached through floating-point round trips as the new shot.
  return FILM_SHOTS.find((shot) => time < shot.end - 1e-9) ?? FILM_SHOTS.at(-1);
}

export const getFilmPhase = (seconds) => getFilmShot(seconds).phase;
