import assert from 'node:assert/strict';
import test from 'node:test';
import { MathUtils, Quaternion, Vector3 } from 'three';
import { applyOrbitSettings, DEFAULT_ORBIT_SETTINGS } from '../src/orbit-editor-state.js';
import { getOrbitPose, letterAngle } from '../src/orbit-flight.js';

const STORAGE_KEY = 'snn-world-intro:orbit-settings:v1';
let moduleId = 0;
async function withStorage(storage, run) {
  const original = Object.getOwnPropertyDescriptor(globalThis, 'localStorage');
  Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: storage });
  try {
    const state = await import(`../src/orbit-editor-state.js?test=${moduleId++}`);
    await run(state);
  } finally {
    if (original) Object.defineProperty(globalThis, 'localStorage', original);
    else delete globalThis.localStorage;
  }
}

test('orbit settings persist normalized snapshots, notify changes, and reset', async () => {
  const stored = new Map();
  const storage = { getItem: (key) => stored.get(key) ?? null, setItem: (key, value) => stored.set(key, value) };
  await withStorage(storage, async (state) => {
    assert.ok(Object.isFrozen(DEFAULT_ORBIT_SETTINGS));
    assert.deepEqual(state.getOrbitSettings(), DEFAULT_ORBIT_SETTINGS);
    let notifications = 0;
    const unsubscribe = state.subscribeOrbitSettings((snapshot) => { notifications += 1; snapshot.radius = 0; });
    assert.deepEqual(state.setOrbitSettings({ radius: 999, tilt: -200, phase: NaN, heading: Infinity, speed: -9 }),
      { radius: 360, tilt: -90, phase: 0, heading: 0, speed: -0.5 });
    assert.equal(notifications, 1);
    state.setOrbitSettings({ radius: 360, ignored: true });
    assert.equal(notifications, 1, 'unchanged settings do not trigger feedback loops');
    state.getOrbitSettings().tilt = 40;
    assert.equal(state.getOrbitSettings().tilt, -90, 'callers receive copies');
    state.setOrbitSettings({ radius: 234, phase: 45, heading: 30, speed: 1.25 });
    const saved = JSON.parse(stored.get(STORAGE_KEY));
    assert.equal(saved.version, 1);
    assert.deepEqual(saved.settings, state.getOrbitSettings());
    assert.deepEqual(JSON.parse(state.exportOrbitSettingsJSON()), saved);
    await withStorage(storage, (reloaded) => assert.deepEqual(reloaded.getOrbitSettings(), saved.settings));
    unsubscribe();
    const previousNotifications = notifications;
    assert.deepEqual(state.resetOrbitSettings(), DEFAULT_ORBIT_SETTINGS);
    assert.equal(notifications, previousNotifications);
    assert.deepEqual(JSON.parse(stored.get(STORAGE_KEY)).settings, DEFAULT_ORBIT_SETTINGS);
  });
});

test('missing, blocked, malformed, and unknown-version storage remain editable', async () => {
  const blocked = { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } };
  for (const storage of [undefined, blocked,
    { getItem: () => '{invalid' },
    { getItem: () => JSON.stringify({ version: 2, settings: { radius: 300 } }) }]) {
    await withStorage(storage, (state) => {
      assert.deepEqual(state.getOrbitSettings(), DEFAULT_ORBIT_SETTINGS);
      assert.equal(state.setOrbitSettings({ radius: 240 }).radius, 240);
      assert.deepEqual(state.setOrbitSettings({ radius: Infinity, speed: '2', tilt: null }),
        { ...DEFAULT_ORBIT_SETTINGS, radius: 240 });
    });
  }
});

test('default orbit settings reproduce every baseline pose exactly without mutation', () => {
  for (const aspect of [0.6, 1, 1.8]) {
    for (const time of [0, 1.8, 5.8, 7.2, 8.6, 11, 12, 14, 18]) {
      const pose = getOrbitPose(time, 1, aspect);
      const snapshot = structuredClone(pose);
      const adjusted = applyOrbitSettings(pose, time);
      assert.deepEqual(adjusted, pose);
      assert.notEqual(adjusted, pose);
      assert.notEqual(adjusted.center, pose.center);
      assert.notEqual(adjusted.frame, pose.frame);
      assert.notEqual(adjusted.letterQuaternion, pose.letterQuaternion);
      assert.equal(adjusted.position, pose.position, 'editing the orbit never changes the camera');
      assert.deepEqual(structuredClone(pose), snapshot);
    }
  }
});

test('edited type and rings share a fixed physical orbit, including reverse and stopped motion', () => {
  for (const speed of [-0.5, 0, 0.75, 2]) {
    const settings = { radius: 270, tilt: 24, heading: -38, phase: 55, speed };
    let previous;
    for (let time = 0; time <= 11; time += 0.5) {
      const pose = getOrbitPose(time);
      const snapshot = structuredClone(pose);
      const adjusted = applyOrbitSettings(pose, time, settings);
      const localCenter = adjusted.center.clone().applyQuaternion(adjusted.frame.clone().invert());
      assert.ok(Math.abs(Math.hypot(localCenter.x, localCenter.z) - settings.radius) < 1e-8);
      assert.ok(Math.abs(localCenter.y - 18) < 1e-8, 'radius edits preserve the orbital plane height');
      const front = new Vector3(0, 0, 1).applyQuaternion(adjusted.letterQuaternion);
      const radial = localCenter.clone().setY(0).normalize().applyQuaternion(adjusted.frame);
      assert.ok(front.distanceTo(radial) < 1e-8, 'the word faces radially in the same frame as the rings');
      const heading = new Quaternion().setFromAxisAngle(new Vector3(0, 1, 0), MathUtils.degToRad(settings.heading));
      const expectedFrame = new Quaternion().setFromAxisAngle(new Vector3(1, 0, 0), MathUtils.degToRad(settings.tilt))
        .multiply(heading).multiply(pose.frame);
      assert.ok(expectedFrame.angleTo(adjusted.frame) < 1e-7, 'heading precedes tilt in world coordinates');
      if (previous) {
        assert.ok(previous.frame.angleTo(adjusted.frame) < 1e-7);
        assert.ok(Math.abs(adjusted.angle - previous.angle - (-0.16 * speed * 0.5)) < 1e-10,
          'negative speed reverses the same constant physical orbit, and zero stops it');
      }
      for (const key of ['position', 'target', 'up', 'fov', 'roll']) assert.equal(adjusted[key], pose[key]);
      assert.deepEqual(structuredClone(pose), snapshot);
      previous = adjusted;
    }
  }
});

test('speed scales authored angular travel through the reveal without introducing a velocity jump', () => {
  const settings = { radius: 240, phase: -80, speed: -0.5 };
  const initialAngle = letterAngle(0);
  for (const speed of [-0.5, 0, 0.75, 2]) {
    for (const time of [0, 5, 11, 11.01, 12, 14, 17, 18]) {
      const pose = getOrbitPose(time);
      const adjusted = applyOrbitSettings(pose, time, { ...settings, speed });
      const expectedAngle = initialAngle + MathUtils.degToRad(settings.phase)
        + speed * (pose.angle - initialAngle);
      assert.ok(Math.abs(adjusted.angle - expectedAngle) < 1e-10,
        `the speed multiplier follows authored angular travel at ${time}s`);
      assert.ok(pose.frame.angleTo(adjusted.frame) < 1e-7,
        'speed edits preserve the fixed orbital plane');
      const undoExtraPhase = new Quaternion().setFromAxisAngle(new Vector3(0, 1, 0), pose.angle - adjusted.angle);
      const restoredFacing = pose.frame.clone().multiply(undoExtraPhase)
        .multiply(adjusted.frame.clone().invert()).multiply(adjusted.letterQuaternion);
      assert.ok(restoredFacing.angleTo(pose.letterQuaternion) < 1e-7,
        'speed edits preserve the authored facing transition');
    }
  }

  const step = 1e-4;
  const atJoin = applyOrbitSettings(getOrbitPose(11), 11, settings);
  const preceding = applyOrbitSettings(getOrbitPose(11 - step), 11 - step, settings);
  const following = applyOrbitSettings(getOrbitPose(11 + step), 11 + step, settings);
  const incomingAngularSpeed = (atJoin.angle - preceding.angle) / step;
  const outgoingAngularSpeed = (following.angle - atJoin.angle) / step;
  assert.ok(Math.abs(incomingAngularSpeed - outgoingAngularSpeed) < 1e-3,
    'the speed multiplier does not switch off when the reveal begins');
  const incomingVelocity = atJoin.center.clone().sub(preceding.center).divideScalar(step);
  const outgoingVelocity = following.center.clone().sub(atJoin.center).divideScalar(step);
  assert.ok(incomingVelocity.distanceTo(outgoingVelocity) < 0.1,
    'the letter center has continuous physical velocity through the reveal boundary');

  const before = applyOrbitSettings(getOrbitPose(11 - 1e-7), 11 - 1e-7, settings);
  const after = applyOrbitSettings(getOrbitPose(11 + 1e-7), 11 + 1e-7, settings);
  assert.ok(before.center.distanceTo(after.center) < 1e-4, 'the reveal begins without a position jump');
  assert.ok(before.letterQuaternion.angleTo(after.letterQuaternion) < 1e-6);
});

test('invalid orbit modifiers normalize to finite settings', () => {
  const invalid = applyOrbitSettings(getOrbitPose(4), NaN,
    { radius: Infinity, phase: NaN, speed: 'fast', heading: null, tilt: undefined });
  assert.deepEqual(invalid, getOrbitPose(4));
  const clamped = applyOrbitSettings(getOrbitPose(4), Infinity,
    { radius: -100, phase: 900, speed: 90, heading: -900, tilt: 900 });
  for (const value of [...clamped.center.toArray(), ...clamped.frame.toArray(), ...clamped.letterQuaternion.toArray(), clamped.angle]) {
    assert.ok(Number.isFinite(value));
  }
});
