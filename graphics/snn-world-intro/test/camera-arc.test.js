import assert from 'node:assert/strict';
import test from 'node:test';
import {
  PROFILE_HOLD_SECONDS,
  ORBIT_SECONDS,
  OVERHEAD_HOLD_SECONDS,
  TOTAL_SECONDS,
  sampleCameraArc,
  orbitPose,
} from '../src/camera-arc.js';

function near(actual, expected, tolerance = 1e-10) {
  assert.ok(
    Math.abs(actual - expected) < tolerance,
    `Expected ${actual} to be within ${tolerance} of ${expected}`,
  );
}

function subtract(a, b) {
  return { x: a.x - b.x, y: a.y - b.y, z: a.z - b.z };
}

function dot(a, b) {
  return a.x * b.x + a.y * b.y + a.z * b.z;
}

function length(vector) {
  return Math.hypot(vector.x, vector.y, vector.z);
}

test('shot timing is a half-second hold, one-second turn, half-second hold', () => {
  assert.equal(PROFILE_HOLD_SECONDS, 0.5);
  assert.equal(ORBIT_SECONDS, 1);
  assert.equal(OVERHEAD_HOLD_SECONDS, 0.5);
  assert.equal(TOTAL_SECONDS, 2);

  for (const time of [-10, 0, 0.25, 0.499999]) {
    assert.deepEqual(sampleCameraArc(time), {
      angleRadians: 0,
      progress: 0,
      phase: 'profile',
      finished: false,
    });
  }

  assert.deepEqual(sampleCameraArc(0.5), {
    angleRadians: 0,
    progress: 0,
    phase: 'orbit',
    finished: false,
  });
  assert.deepEqual(sampleCameraArc(1), {
    angleRadians: Math.PI / 4,
    progress: 0.5,
    phase: 'orbit',
    finished: false,
  });

  for (const time of [1.5, 1.75, 1.999999]) {
    assert.deepEqual(sampleCameraArc(time), {
      angleRadians: Math.PI / 2,
      progress: 1,
      phase: 'overhead',
      finished: false,
    });
  }

  for (const time of [2, 2.1, 100]) {
    assert.deepEqual(sampleCameraArc(time), {
      angleRadians: Math.PI / 2,
      progress: 1,
      phase: 'overhead',
      finished: true,
    });
  }
});

test('angular velocity is constant throughout the one-second turn', () => {
  for (let index = 0; index < 10; index += 1) {
    const start = sampleCameraArc(0.5 + index / 10);
    const end = sampleCameraArc(0.5 + (index + 1) / 10);
    near(end.angleRadians - start.angleRadians, Math.PI / 20);
  }
});

test('camera starts in profile and ends directly above the same target', () => {
  const target = { x: -2, y: 3, z: 4 };
  const radius = 8;
  const profile = orbitPose(0, target, radius);
  const overhead = orbitPose(Math.PI / 2, target, radius);

  assert.deepEqual(profile.position, { x: -2, y: 3, z: 12 });
  near(overhead.position.x, target.x);
  near(overhead.position.y, target.y + radius);
  near(overhead.position.z, target.z);
  near(overhead.up.x, 0);
  near(overhead.up.y, 0);
  near(overhead.up.z, -1);
  assert.deepEqual(target, { x: -2, y: 3, z: 4 });
});

test('radius stays fixed and the up vector stays unit length and perpendicular to view', () => {
  const target = { x: 2.5, y: -1.25, z: 6 };
  const radius = 7;

  for (let index = 0; index <= 100; index += 1) {
    const pose = orbitPose(index / 100 * Math.PI / 2, target, radius);
    const radial = subtract(pose.position, target);
    near(length(radial), radius);
    near(length(pose.up), 1);
    near(dot(radial, pose.up), 0);
  }
});

test('camera velocity is tangent to the radius and points along camera-up', () => {
  const target = { x: 1, y: 2, z: -3 };
  const radius = 6;
  const epsilon = 1e-5;

  for (const time of [0.6, 0.75, 1, 1.25, 1.4]) {
    const before = orbitPose(sampleCameraArc(time - epsilon).angleRadians, target, radius);
    const current = orbitPose(sampleCameraArc(time).angleRadians, target, radius);
    const after = orbitPose(sampleCameraArc(time + epsilon).angleRadians, target, radius);
    const difference = subtract(after.position, before.position);
    const velocity = {
      x: difference.x / (2 * epsilon),
      y: difference.y / (2 * epsilon),
      z: difference.z / (2 * epsilon),
    };
    const radial = subtract(current.position, target);
    const expectedSpeed = radius * Math.PI / 2;

    near(dot(velocity, radial), 0, 1e-8);
    near(length(velocity), expectedSpeed, 1e-8);
    near(dot(velocity, current.up), expectedSpeed, 1e-8);
  }
});
