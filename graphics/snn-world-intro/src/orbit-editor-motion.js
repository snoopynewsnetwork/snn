import { getOrbitPose } from './orbit-flight.js';
import { applyOrbitSettings } from './orbit-editor-state.js';

export const PATH_START = 7.1;
export const PATH_END = 24;
export const FILM_ASPECT = 16 / 9;

const FILM_START = 6;
const DIFFERENCE_STEP = 0.005;
// Keep the editor line dense enough to show the rounded letter turns.
const TRACK_INTERVALS = Math.round((PATH_END - PATH_START) / 0.02);

function filmTime(value) {
  const time = typeof value === 'number' && !Number.isNaN(value) ? value : FILM_START;
  return Math.min(PATH_END, Math.max(FILM_START, time));
}

function cameraPose(time, weave) {
  return getOrbitPose(time - FILM_START, Number.isFinite(weave) ? weave : 1, FILM_ASPECT);
}

function differenceWindow(time) {
  return [Math.max(FILM_START, time - DIFFERENCE_STEP), Math.min(PATH_END, time + DIFFERENCE_STEP)];
}

function cameraSpeedAt(time, weave) {
  const [before, after] = differenceWindow(time);
  return cameraPose(after, weave).position.distanceTo(cameraPose(before, weave).position) / (after - before);
}

function orbitSpeedAt(time, weave, settings) {
  const [before, after] = differenceWindow(time);
  const start = applyOrbitSettings(cameraPose(before, weave), before - FILM_START, settings);
  const end = applyOrbitSettings(cameraPose(after, weave), after - FILM_START, settings);
  return end.center.distanceTo(start.center) / (after - before);
}

/**
 * Actual camera positions and world-units-per-second speeds. The path starts
 * after the opening's distant near-orthographic lens blend, without remapping
 * or compressing any positions. Both endpoints are included at uniform times.
 */
export function sampleCameraTrack(weave = 1) {
  return Array.from({ length: TRACK_INTERVALS + 1 }, (_, index) => {
    const time = PATH_START + (PATH_END - PATH_START) * index / TRACK_INTERVALS;
    return { time, position: cameraPose(time, weave).position, speed: cameraSpeedAt(time, weave) };
  });
}

/** Sample the live shot and physical speeds on the full-film 6–24s clock. */
export function getEditorMotion(time, weave = 1, settings) {
  const at = filmTime(time);
  return {
    pose: applyOrbitSettings(cameraPose(at, weave), at - FILM_START, settings),
    cameraSpeed: cameraSpeedAt(at, weave),
    orbitSpeed: orbitSpeedAt(at, weave, settings),
  };
}

/** The letter-center speed at each supplied camera-track time, in world units/s. */
export function sampleOrbitSpeeds(track, weave = 1, settings) {
  return track.map(({ time }) => orbitSpeedAt(filmTime(time), weave, settings));
}
