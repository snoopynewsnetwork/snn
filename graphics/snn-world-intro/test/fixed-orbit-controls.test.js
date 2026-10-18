import assert from 'node:assert/strict';
import test from 'node:test';
import * as THREE from 'three';
import { orbitPose } from '../src/camera-arc.js';
import { createFixedOrbitControls, syncManualOrbit } from '../src/fixed-orbit-controls.js';

const RADIUS = 650;

function near(actual, expected, tolerance = 1e-9) {
  assert.ok(Math.abs(actual - expected) < tolerance, `${actual} differs from ${expected}`);
}

function applyShot(camera, target, angle) {
  const pose = orbitPose(angle, target, RADIUS);
  camera.position.copy(pose.position);
  camera.up.copy(pose.up);
  camera.lookAt(target);
}

function assertLookingAt(camera, target) {
  const direction = camera.getWorldDirection(new THREE.Vector3());
  const expected = target.clone().sub(camera.position).normalize();
  near(direction.distanceTo(expected), 0);
}

function setup(target = new THREE.Vector3()) {
  const camera = new THREE.OrthographicCamera(-215, 215, 215, -215, 0.1, 2000);
  applyShot(camera, target, 0);
  const controls = createFixedOrbitControls(camera, null, target, RADIUS);
  return { camera, controls, target };
}

test('manual rotation stays on a fixed sphere without moving target or changing zoom', () => {
  const { camera, controls, target } = setup(new THREE.Vector3(12, -8, 25));
  const initialPosition = camera.position.clone();
  const initialTarget = target.clone();
  const initialZoom = camera.zoom;

  for (let index = 0; index < 100; index += 1) {
    controls.rotateLeft(0.15);
    controls.rotateUp(Math.sin(index * 0.3) * 0.2);
    near(camera.position.distanceTo(target), RADIUS);
    near(controls.target.distanceTo(initialTarget), 0);
    assert.deepEqual(target, initialTarget);
    assert.equal(camera.zoom, initialZoom);
    assertLookingAt(camera, target);
  }
  assert.ok(camera.position.distanceTo(initialPosition) > 100);

  // No residual damping may keep moving the view after the drag ends.
  const settledPosition = camera.position.clone();
  for (let index = 0; index < 10; index += 1) controls.update();
  near(camera.position.distanceTo(settledPosition), 0);
});

test('manual orbit can start from the exact scripted overhead pose', () => {
  const { camera, controls, target } = setup();
  applyShot(camera, target, Math.PI / 2);
  const overheadPosition = camera.position.clone();
  const overheadOrientation = camera.quaternion.clone();

  syncManualOrbit(controls);
  assert.ok([...camera.position, ...camera.quaternion].every(Number.isFinite));
  near(camera.position.distanceTo(target), RADIUS);
  assert.ok(camera.position.distanceTo(overheadPosition) < 0.001);
  assert.ok(camera.quaternion.angleTo(overheadOrientation) < 0.00001);
  assertLookingAt(camera, target);

  controls.rotateUp(-Math.PI / 4);
  controls.rotateLeft(Math.PI / 3);
  assert.ok(camera.position.distanceTo(overheadPosition) > 100);
  near(camera.position.distanceTo(target), RADIUS);
  assertLookingAt(camera, target);
});

test('scripted poses take over after manual orbit and a subsequent drag uses the new pose', () => {
  const { camera, controls, target } = setup();
  controls.rotateLeft(1.2);
  controls.rotateUp(-0.6);

  // Script playback owns the transform and intentionally does not update controls.
  for (const angle of [0, Math.PI / 4, Math.PI / 2]) {
    applyShot(camera, target, angle);
    const expected = orbitPose(angle, target, RADIUS);
    near(camera.position.distanceTo(new THREE.Vector3().copy(expected.position)), 0);
    near(camera.up.distanceTo(new THREE.Vector3().copy(expected.up)), 0);
    assertLookingAt(camera, target);
  }

  applyShot(camera, target, 0);
  syncManualOrbit(controls);
  controls.rotateLeft(Math.PI / 2);
  near(camera.position.x, -RADIUS);
  near(camera.position.y, 0);
  near(camera.position.z, 0);
  near(camera.position.distanceTo(target), RADIUS);
  assertLookingAt(camera, target);
});
