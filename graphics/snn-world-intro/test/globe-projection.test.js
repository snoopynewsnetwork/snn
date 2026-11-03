import assert from 'node:assert/strict';
import test from 'node:test';
import { geoEquirectangular, geoPath } from 'd3-geo';
import { SphereGeometry, Vector3 } from 'three';
import {
  FLAT_VIEW,
  SPHERE_VIEW,
  geoVector,
  createFlatProjection,
  coastlineGeometry,
} from '../src/globe-projection.js';

function near(actual, expected, tolerance = 1e-10) {
  assert.ok(
    Math.abs(actual - expected) < tolerance,
    `Expected ${actual} to be within ${tolerance} of ${expected}`,
  );
}

test('geographic vectors preserve radius and use north-up sphere coordinates', () => {
  for (const radius of [1, 2.5, 12]) {
    for (const longitude of [-180, -115, -90, 0, 45, 180]) {
      for (const latitude of [-90, -45, 0, 12, 90]) {
        const position = geoVector(longitude, latitude, radius);
        assert.ok(position instanceof Vector3);
        near(position.length(), radius);
      }
    }
  }

  near(geoVector(0, 90).y, 1);
  near(geoVector(0, -90).y, -1);
  near(geoVector(0, 0).x, 1);
  near(geoVector(90, 0).z, -1);
  near(geoVector(-90, 0).z, 1);
});

test('geographic vectors match the actual default SphereGeometry texture mapping', () => {
  const sphere = new SphereGeometry(2, 16, 8);
  const positions = sphere.getAttribute('position');
  const coordinates = sphere.getAttribute('uv');

  for (let index = 0; index < positions.count; index += 1) {
    const u = coordinates.getX(index);
    const v = coordinates.getY(index);
    const expected = geoVector(u * 360 - 180, v * 180 - 90, 2);
    near(positions.getX(index), expected.x, 1e-6);
    near(positions.getY(index), expected.y, 1e-6);
    near(positions.getZ(index), expected.z, 1e-6);
  }

  sphere.dispose();
});

test('flat projection centers the Americas and keeps east right and north up', () => {
  const projection = createFlatProjection(240, [320, 280]);
  const center = projection([FLAT_VIEW.longitude, FLAT_VIEW.latitude]);
  const north = projection([FLAT_VIEW.longitude, FLAT_VIEW.latitude + 5]);
  const east = projection([FLAT_VIEW.longitude + 5, FLAT_VIEW.latitude]);

  near(center[0], 320);
  near(center[1], 280);
  near(north[0], center[0]);
  assert.ok(north[1] < center[1]);
  assert.ok(east[0] > center[0]);

  const rim = projection([FLAT_VIEW.longitude + 90, 0]);
  near(Math.hypot(rim[0] - center[0], rim[1] - center[1]), 240);
});

test('flat path rendering clips the far hemisphere while keeping both Americas', () => {
  const path = geoPath(createFlatProjection(100));
  const visible = [
    [FLAT_VIEW.longitude, FLAT_VIEW.latitude],
    [-120, 37], // California.
    [-71, -30], // Chile.
    [-36, -10], // Eastern Brazil.
  ];
  const hidden = [
    [FLAT_VIEW.longitude + 180, -FLAT_VIEW.latitude],
    [140, 36], // Japan.
  ];

  for (const coordinates of visible) {
    assert.ok(path({ type: 'Point', coordinates }), `${coordinates} should be visible`);
  }
  for (const coordinates of hidden) {
    assert.equal(path({ type: 'Point', coordinates }), null, `${coordinates} should be clipped`);
  }
});

test('3D view faces the eastern Pacific with the Americas visible and Europe and Japan hidden', () => {
  const cameraDirection = geoVector(SPHERE_VIEW.longitude, SPHERE_VIEW.latitude);
  assert.ok(cameraDirection.y > 0);
  assert.ok(cameraDirection.y < Math.sin(20 * Math.PI / 180));

  for (const [name, coordinates] of [
    ['California', [-120, 37]],
    ['Chile', [-71, -30]],
    ['Brazil', [-36, -10]],
  ]) {
    assert.ok(cameraDirection.dot(geoVector(...coordinates)) > 0, `${name} should face the camera`);
  }
  for (const [name, coordinates] of [
    ['London', [0, 51.5]],
    ['Japan', [140, 36]],
    ['Western Africa', [-17, 15]],
  ]) {
    assert.ok(cameraDirection.dot(geoVector(...coordinates)) < 0, `${name} should be behind the globe`);
  }
});

test('coastlines preserve polygon rings through feature and multipolygon wrappers', () => {
  const coast = [[-100, 10], [-90, 10], [-95, 20], [-100, 10]];
  const island = [[-80, 10], [-75, 10], [-77, 15], [-80, 10]];
  const land = {
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', geometry: { type: 'Polygon', coordinates: [coast] } },
      { type: 'Feature', geometry: { type: 'MultiPolygon', coordinates: [[island]] } },
    ],
  };
  const original = structuredClone(land);

  assert.deepEqual(coastlineGeometry(land), {
    type: 'MultiLineString', coordinates: [coast, island],
  });
  assert.deepEqual(land, original);
});

test('texture coastlines do not gain artificial vertical edges at the antimeridian', () => {
  const projection = geoEquirectangular()
    .scale(180 / Math.PI)
    .translate([180, 90]);

  function seamSegments(geometry) {
    let previous;
    let start;
    let count = 0;
    const context = {
      moveTo(x, y) { previous = start = [x, y]; },
      lineTo(x, y) {
        const onEdge = (value) => Math.abs(value) < 1e-6 || Math.abs(value - 360) < 1e-6;
        if (onEdge(x) && onEdge(previous[0]) && Math.abs(x - previous[0]) < 1e-6
          && Math.abs(y - previous[1]) > 1e-6) count += 1;
        previous = [x, y];
      },
      closePath() { this.lineTo(...start); },
    };
    geoPath(projection, context)(geometry);
    return count;
  }

  const crossingPolygon = {
    type: 'Polygon',
    coordinates: [[[170, 60], [170, 70], [-170, 70], [-170, 60], [170, 60]]],
  };
  // Reproduce both projection-generated seams and seams already present in
  // land data whose polygons were split at the antimeridian beforehand.
  const splitPolygon = {
    type: 'Polygon',
    coordinates: [[[180, 60], [170, 60], [170, 70], [180, 70], [180, 60]]],
  };
  for (const polygon of [crossingPolygon, splitPolygon]) {
    assert.ok(seamSegments(polygon) > 0, 'filled polygon should reproduce the original seam');
    assert.equal(seamSegments(coastlineGeometry(polygon)), 0);
  }
});
