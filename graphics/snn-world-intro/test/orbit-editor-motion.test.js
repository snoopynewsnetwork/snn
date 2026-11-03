import assert from 'node:assert/strict';
import test from 'node:test';
import { getOrbitPose } from '../src/orbit-flight.js';
import {
  FILM_ASPECT, PATH_END, PATH_START,
  getEditorMotion, sampleCameraTrack, sampleOrbitSpeeds,
} from '../src/orbit-editor-motion.js';

test('camera track uses uniform film times and actual finite world positions', () => {
  const track = sampleCameraTrack();
  assert.equal(FILM_ASPECT, 16 / 9);
  assert.equal(track[0].time, PATH_START);
  assert.equal(track.at(-1).time, PATH_END);
  assert.equal(track.length, 846);
  for (let index = 0; index < track.length; index += 1) {
    const sample = track[index];
    assert.ok(sample.position.toArray().every(Number.isFinite));
    assert.ok(Number.isFinite(sample.speed) && sample.speed >= 0);
    assert.deepEqual(sample.position, getOrbitPose(sample.time - 6, 1, FILM_ASPECT).position);
    if (index) assert.ok(Math.abs(sample.time - track[index - 1].time - 0.02) < 1e-12);
  }
});

test('live motion clamps the film range and uses bounded physical finite differences', () => {
  for (const time of [6, 6.1, 7.1, 10, 17, 24]) {
    const motion = getEditorMotion(time);
    const before = Math.max(6, time - 0.005);
    const after = Math.min(24, time + 0.005);
    const distance = getOrbitPose(after - 6, 1, FILM_ASPECT).position
      .distanceTo(getOrbitPose(before - 6, 1, FILM_ASPECT).position);
    assert.equal(motion.cameraSpeed, distance / (after - before));
    assert.ok(Number.isFinite(motion.orbitSpeed) && motion.orbitSpeed >= 0);
    assert.deepEqual(motion.pose.position, getOrbitPose(time - 6, 1, FILM_ASPECT).position);
  }
  assert.deepEqual(getEditorMotion(-100), getEditorMotion(6));
  assert.deepEqual(getEditorMotion(100), getEditorMotion(24));
  assert.deepEqual(getEditorMotion(Number.NaN), getEditorMotion(6));
  assert.ok(getEditorMotion(6.1).cameraSpeed > 100000,
    'the distant opening lens blend retains its real speed rather than chart-clamped speed');
});

test('orbit edits affect letter speed while leaving the physical camera unchanged', () => {
  const settings = { radius: 300, speed: 1.5, tilt: 37, heading: -52, phase: 73 };
  for (const time of [7.1, 10, 15, 16.9]) {
    const original = getEditorMotion(time);
    const edited = getEditorMotion(time, 1, settings);
    assert.equal(edited.cameraSpeed, original.cameraSpeed);
    assert.deepEqual(edited.pose.position, original.pose.position);
    assert.deepEqual(edited.pose.target, original.pose.target);
    assert.ok(Math.abs(original.orbitSpeed - 205 * 0.16) < 1e-4);
    assert.ok(Math.abs(edited.orbitSpeed - 300 * 0.16 * 1.5) < 1e-4);
  }
});

test('zero orbit speed holds the letter center stationary before film 17 seconds', () => {
  const settings = { speed: 0, radius: 250, tilt: 20, heading: 45 };
  const track = [6, 7.1, 10, 13.2, 16.99].map((time) => ({ time }));
  const speeds = sampleOrbitSpeeds(track, 1, settings);
  assert.equal(speeds.length, track.length);
  for (const speed of speeds) assert.ok(speed < 1e-8, `expected stationary center, got ${speed}`);
  assert.deepEqual(speeds, track.map(({ time }) => getEditorMotion(time, 1, settings).orbitSpeed));
});
