import assert from 'node:assert/strict';
import test from 'node:test';
import { createServer } from 'vite';
import { Frustum, Quaternion, Raycaster, Triangle, Vector3 } from 'three';
import {
  APPROACH_DURATION, COAST_START, COAST_END, COAST_RADIUS,
  getOrbitPose, letterAngle, orbitPhase, orbitTimeForRoute,
} from '../src/orbit-flight.js';
import { geoVector } from '../src/globe-projection.js';
import { applyOrbitSettings } from '../src/orbit-editor-state.js';

// Position and viewing direction have independent joins; verify both clocks.
const WEAVE_JOINS = [5.9, 8, 8.35, 8.75, 9.05, 9.15, 9.45, 9.5, 10, 10.25, 10.35, 10.65, 10.7, 11];

test('the camera change preserves the approach and the entire authored letter orbit', () => {
  // Captured independently before the weave was added, with its approved
  // trailing-N bend captured before rounding the later turns.
  const cameraAnchors = [
    { time: 0, position: [0, 0, 206301.68952373404], target: [0, 0, 0], up: [0, 1, 0], fov: 0.1 },
    { time: 1.8, position: [8.794768383076711, 28.2060855856555, 177.55863478024017],
      target: [-17.180676022721553, 90.51679035719164, 103.78430076904257],
      up: [-0.15417788734317148, 0.72740683684995, 0.6686617027752871], fov: 42 },
    { time: 5.9, position: [-140.22987953772363, 108.82960262030007, -29.94912151120485],
      target: [-116.38565826625079, 24.2302025946890325, -75.50667265036442],
      up: [-0.7994061454164827, 0.09421689279801253, -0.5933573895906658], fov: 42 },
    { time: 8.75, weaves: [1], position: [216.13169504460302, 24, -145.57159886855237],
      target: [213.6139052523539, 24, -45.60330022062074],
      up: [0.7258789294486254, 0.6875794876747308, 0.018281901199608746], fov: 42 },
  ];
  for (const expected of cameraAnchors) {
    for (const weave of expected.weaves ?? [0, 1, 1.5]) {
      const pose = getOrbitPose(expected.time, weave, 16 / 9);
      for (const key of ['position', 'target', 'up']) assert.deepEqual(pose[key].toArray(), expected[key],
        `the camera ${key} is unchanged at film ${expected.time + 6}s`);
      assert.equal(pose.fov, expected.fov);
      assert.equal(pose.roll, 0);
    }
  }
  const orbitAnchors = [
    [0, 3.2514946393618147, [-22.48458008643949, 18, -203.76320486863298], [0, 0.9984905740711131, 0, -0.05492334195166123]],
    [5.9, 2.3074946393618148, [151.8416175952828, 18, -137.72843993180166], [0, 0.9142882610117591, 0, 0.40506416254229827]],
    [11, 1.4914946393618145, [204.35574008201618, 18, 16.23981205345178], [0, 0.6785209667421149, 0, 0.7345810354830471]],
    [12, 1.151124268991444, [187.21063567914157, 18, 83.52950310286613], [0, 0.413543317106923, 0, 0.9104844451588412]],
    [14, 0.16149463936181452, [32.96268325783463, 18, 202.3325517865172], [0, 0, 0, 1]],
    [18, -0.9085053606381854, [-161.6600335724364, 18, 126.05964280989667], [0, 0, 0, 1]],
  ];
  for (const [time, angle, center, rotation] of orbitAnchors) {
    const pose = getOrbitPose(time);
    assert.equal(pose.angle, angle);
    assert.deepEqual(pose.center.toArray(), center, `the letter orbit stays unchanged at film ${time + 6}s`);
    assert.ok(pose.letterQuaternion.toArray().every((value, index) => value === rotation[index]),
      'letter orientation stays unchanged, treating equivalent signed zero equally');
    assert.deepEqual(pose.frame.toArray(), [0, 0, 0, 1]);
    assert.equal(pose.lettersVisible, true);
  }
});

test('the letter turns stay broad and the inside of the middle N is one convex bow', () => {
  const step = 0.0002;
  const pointAt = (time, weave) => {
    const pose = getOrbitPose(time, weave);
    return { world: pose.position.clone(),
      local: pose.position.sub(pose.center).applyQuaternion(pose.letterQuaternion.invert()) };
  };
  const curvature = (before, at, after) => {
    const velocity = after.clone().sub(before).divideScalar(2 * step);
    const acceleration = after.clone().add(before).addScaledVector(at, -2).divideScalar(step ** 2);
    const speed = Math.hypot(velocity.x, velocity.z);
    assert.ok(speed > 25, 'the rounded path remains moving instead of hiding a sharp turn with a stop');
    return (velocity.x * acceleration.z - velocity.z * acceleration.x) / speed ** 3;
  };
  for (const weave of [0, 1, 1.5]) {
    let innerSamples = 0;
    let incomingSamples = 0;
    let outgoingSamples = 0;
    for (let sample = 1; sample < 600; sample += 1) {
      const time = 8 + 3 * sample / 600;
      const before = pointAt(time - step, weave);
      const at = pointAt(time, weave);
      const after = pointAt(time + step, weave);
      const localCurvature = curvature(before.local, at.local, after.local);
      const worldCurvature = curvature(before.world, at.world, after.world);
      assert.ok(Math.abs(localCurvature) < 1 / 18,
        `letter-relative turns keep at least an 18-unit radius at film ${time + 6}s`);
      assert.ok(Math.abs(worldCurvature) < 1 / 22,
        `the actual camera path also stays broad in world space at film ${time + 6}s`);
      if (Math.abs(at.local.x) < 36.5 && at.local.z < -21) {
        assert.ok(localCurvature <= 1e-5,
          'the entire inside bow bends one way, without a dip followed by another outward bend');
        if (Math.abs(at.local.x) < 35) assert.ok(worldCurvature < -1e-4,
          'the middle-N bow stays convex in the world-space camera path as the letters orbit');
        innerSamples += 1;
      }
      if (at.local.x > 40 && at.local.x < 75 && at.local.z > 18) {
        assert.ok(localCurvature >= -1e-5, 'the incoming turn rounds directly into the gap without an extra bend');
        incomingSamples += 1;
      }
      if (at.local.x < -40 && at.local.x > -74 && at.local.z > 18) {
        assert.ok(localCurvature >= -1e-5, 'the outgoing turn rounds directly toward S without an extra bend');
        outgoingSamples += 1;
      }
    }
    assert.ok(innerSamples > 100 && incomingSamples > 30 && outgoingSamples > 30,
      'the curvature checks cover the complete visible bends, not just their endpoints');
  }
});

test('orbit flight stays outside Earth and remains continuous at shot boundaries', () => {
  for (const aspect of [0.6, 1, 1.8]) {
    let previousRadius = Infinity;
    for (let sample = 0; sample <= 400; sample += 1) {
      const radius = getOrbitPose(orbitTimeForRoute(COAST_START) * sample / 400, 1, aspect).position.length();
      assert.ok(radius < previousRadius, `the descent approaches Earth without backing away at aspect ${aspect}`);
      previousRadius = radius;
    }
    for (const weave of [0, 0.5, 1, 1.5]) {
      for (let sample = 0; sample <= 360; sample += 1) {
        const pose = getOrbitPose(sample / 20, weave, aspect);
        assert.ok(pose.position.toArray().every(Number.isFinite));
        assert.ok(pose.target.toArray().every(Number.isFinite));
        assert.ok(pose.position.length() > 145, 'camera clears the globe and its ink outline');
        assert.ok(pose.position.distanceTo(pose.target) > 0);
        assert.ok(pose.fov > 0 && pose.fov < 180);
      }
      for (const time of [COAST_START, COAST_END, ...WEAVE_JOINS, 14]) {
        const before = getOrbitPose(time - 1e-7, weave, aspect);
        const after = getOrbitPose(time + 1e-7, weave, aspect);
        assert.ok(before.position.distanceTo(after.position) < 1e-3, `position joins at ${time}`);
        assert.ok(before.target.distanceTo(after.target) < 1e-3, `aim joins at ${time}`);
        assert.ok(before.up.distanceTo(after.up) < 1e-3, `camera up joins at ${time}`);
        assert.ok(Math.abs(before.fov - after.fov) < 1e-3, `lens joins at ${time}`);
        assert.ok(Math.abs(before.roll - after.roll) < 1e-3, `roll joins at ${time}`);
      }
    }
  }
});

test('the close pass is one scene before the renumbered reveal and crossing', () => {
  const phase = orbitPhase(APPROACH_DURATION);
  assert.match(orbitPhase(APPROACH_DURATION - 1e-6), /^01 · /);
  assert.match(phase, /^02 · /);
  assert.equal(orbitPhase((6 + APPROACH_DURATION) - 6), phase,
    'the full-film timestamp round trip preserves the Shot 02 boundary');
  for (const fraction of [0, 0.2, 0.5, 0.8, 0.999]) {
    assert.equal(orbitPhase(APPROACH_DURATION + fraction * (11 - APPROACH_DURATION)), phase);
  }
  assert.match(orbitPhase(11), /^03 · /);
  assert.match(orbitPhase(14), /^04 · /);
});

test('the descent and close pass join smoothly with a longer, steady Pacific cruise', () => {
  const step = 1e-4;
  for (const aspect of [0.6, 1, 1.8]) {
    for (const weave of [0, 1, 1.5]) {
      for (const time of [COAST_START, COAST_END, ...WEAVE_JOINS]) {
        const before = getOrbitPose(time - step, weave, aspect);
        const at = getOrbitPose(time, weave, aspect);
        const after = getOrbitPose(time + step, weave, aspect);
        for (const property of ['position', 'target']) {
          const incoming = at[property].clone().sub(before[property]).divideScalar(step);
          const outgoing = after[property].clone().sub(at[property]).divideScalar(step);
          if (property === 'position') assert.ok(incoming.length() > 10 && outgoing.length() > 10,
            'the camera never pauses at a route join');
          // Use an absolute tolerance when an aim tangent is nearly stationary.
          assert.ok(incoming.distanceTo(outgoing) < Math.max(0.5, 0.02 * Math.max(incoming.length(), outgoing.length())),
            `${property} keeps its velocity across route join ${time}`);
        }
      }
    }
  }
  const speeds = [];
  assert.ok(COAST_START <= 2 && COAST_END - COAST_START >= 4,
    'the descent quickly gives way to a longer orbital arc');
  for (let time = COAST_START + 0.01; time <= COAST_END - 0.01; time += 0.05) {
    speeds.push(getOrbitPose(time + step).position.sub(getOrbitPose(time - step).position).length() / (2 * step));
  }
  const mean = speeds.reduce((sum, value) => sum + value, 0) / speeds.length;
  assert.ok(speeds.every((speed) => Math.abs(speed - mean) / mean < 0.01),
    'the camera maintains one speed throughout the Pacific cruise');
});

function playbackState(film, phase) {
  film.scene.updateMatrixWorld(true);
  film.camera.updateMatrixWorld(true);
  const objects = [];
  film.scene.traverse((object) => {
    objects.push({
      name: object.name, visible: object.visible,
      matrix: object.matrixWorld.elements.slice(),
      opacity: Array.isArray(object.material)
        ? object.material.map((material) => material.opacity) : object.material?.opacity,
    });
  });
  return {
    phase, objects,
    camera: film.camera.matrixWorld.elements.slice(),
    projection: film.camera.projectionMatrix.elements.slice(),
  };
}

function geometryTriangles(geometry) {
  const positions = geometry.attributes.position;
  const indices = geometry.index;
  const triangles = [];
  for (let index = 0; index < (indices?.count ?? positions.count); index += 3) {
    const vertices = [0, 1, 2].map((offset) => new Vector3().fromBufferAttribute(
      positions, indices ? indices.getX(index + offset) : index + offset,
    ));
    triangles.push(new Triangle(...vertices));
  }
  return triangles;
}

function extrusionContains(mesh) {
  const geometry = mesh.geometry;
  geometry.computeBoundingBox();
  const { min, max } = geometry.boundingBox;
  const caps = geometryTriangles(geometry).filter(({ a, b, c }) => (
    [a, b, c].every((point) => Math.abs(point.z - max.z) < 1e-6)
  ));
  assert.ok(caps.length > 0, `${mesh.name} has an actual extruded front cap`);
  return (worldPoint) => {
    const local = mesh.worldToLocal(worldPoint.clone());
    if (local.x < min.x || local.x > max.x || local.y < min.y || local.y > max.y
      || local.z < min.z || local.z > max.z) return false;
    local.z = max.z;
    return caps.some((triangle) => triangle.containsPoint(local));
  };
}

function verifyLetterSurfaceClearance(film, letterGroups) {
  const surfaces = [];
  for (const letter of letterGroups) letter.traverse((mesh) => {
    if (!mesh.isMesh) return;
    mesh.geometry.computeBoundingBox();
    surfaces.push({ mesh, triangles: geometryTriangles(mesh.geometry), bounds: mesh.geometry.boundingBox });
  });
  const nearest = new Vector3();
  const times = new Set(Array.from({ length: 361 }, (_, index) => 6 + index / 20));
  // Inspect the new approach and rounded turns every 10ms, including the ink
  // protruding into the narrow passages, while retaining full-film coverage.
  for (let sample = 0; sample <= 510; sample += 1) times.add(11.9 + sample / 100);
  for (const aspect of [0.6, 1, 1.8]) {
    for (const weave of [0, 1, 1.5]) {
      for (const seconds of times) {
        film.update(seconds, aspect, { weave });
        film.scene.updateMatrixWorld(true);
        let clearance = Infinity;
        for (const { mesh, triangles, bounds } of surfaces) {
          const point = mesh.worldToLocal(film.camera.position.clone());
          // An outside bounding box proves clearance cheaply; inspect actual
          // triangles near a glyph, including its raised ink and hatching.
          if (bounds.distanceToPoint(point) > 2) continue;
          for (const triangle of triangles) {
            clearance = Math.min(clearance, triangle.closestPointToPoint(point, nearest).distanceTo(point));
          }
        }
        assert.ok(clearance > 2,
          `camera clears actual equatorial letter surfaces: ${clearance} at ${seconds}s, weave ${weave}, aspect ${aspect}`);
      }
    }
  }
}

function verifyOpaqueOpening(film) {
  film.update(6, 1.8);
  film.scene.updateMatrixWorld(true);
  const earth = film.scene.getObjectByName('earth');
  const earthTransform = earth.matrixWorld.elements.slice();
  const earthGeometry = earth.children.map((mesh) => ({
    mesh, geometry: mesh.geometry, vertices: mesh.geometry.attributes.position.array.slice(),
  }));
  const letters = film.scene.getObjectByName('snn-orbit-letters');
  const appearance = () => {
    const result = [{ visible: letters.parent.visible, scale: letters.parent.scale.toArray() }];
    letters.traverse((object) => {
      const materials = Array.isArray(object.material) ? object.material : [object.material].filter(Boolean);
      result.push({
        name: object.name, visible: object.visible, scale: object.scale.toArray(),
        materials: materials.map(({ opacity, transparent, depthTest, depthWrite }) => (
          { opacity, transparent, depthTest, depthWrite }
        )),
      });
    });
    return result;
  };
  const originalAppearance = appearance();
  const volumes = ['snn-letter-s-volume', 'snn-letter-n-1-volume', 'snn-letter-n-2-volume']
    .map((name) => letters.getObjectByName(name));
  for (const object of originalAppearance) {
    assert.equal(object.visible, true, 'the complete word and every part are visible from the opening');
    if (!object.name?.endsWith('-volume')) continue;
    for (const material of object.materials) {
      assert.equal(material.opacity, 1, 'the visible letters are fully opaque');
      assert.equal(material.transparent, false);
      assert.equal(material.depthTest, true);
      assert.equal(material.depthWrite, true);
    }
  }
  for (let sample = 0; sample <= 16; sample += 1) {
    film.update(6 + APPROACH_DURATION * sample / 16, 1.8);
    film.scene.updateMatrixWorld(true);
    assert.deepEqual(appearance(), originalAppearance, 'Shot 01 never fades, scales, or hides the type');
    assert.equal(film.scene.getObjectByName('earth'), earth, 'one Earth occludes the letters throughout Shot 01');
    assert.deepEqual(earth.matrixWorld.elements, earthTransform, 'Earth stays fixed while the camera moves');
    for (const { mesh, geometry, vertices } of earthGeometry) {
      assert.equal(mesh.geometry, geometry);
      assert.deepEqual(mesh.geometry.attributes.position.array, vertices, 'Earth geometry stays unchanged');
    }
  }
  let occludedSurfaces = 0;
  for (const aspect of [0.6, 1, 1.8]) {
    for (const seconds of [6, 6.05, 6.1, 6.2, 6.5, 7]) {
      film.update(seconds, aspect);
      film.scene.updateMatrixWorld(true);
      assert.equal(letters.visible, true, 'the word has no initial visibility gate');
      for (const volume of volumes) {
        const direction = volume.getWorldPosition(new Vector3()).sub(film.camera.position).normalize();
        const raycaster = new Raycaster(film.camera.position, direction);
        const front = raycaster.intersectObject(earth.getObjectByName('globe-surface'))[0];
        const hidden = raycaster.intersectObject(volume)[0];
        if (!front || !hidden || front.distance >= hidden.distance) continue;
        const frontDepth = (front.point.clone().project(film.camera).z + 1) / 2;
        const hiddenDepth = (hidden.point.clone().project(film.camera).z + 1) / 2;
        assert.ok(frontDepth >= 0 && hiddenDepth <= 1, 'both actual surfaces lie inside the clipping planes');
        assert.ok((hiddenDepth - frontDepth) * (2 ** 24 - 1) > 1024,
          `Earth and hidden type retain ample 24-bit depth separation at ${seconds}s, aspect ${aspect}`);
        occludedSurfaces += 1;
      }
    }
  }
  assert.ok(occludedSurfaces > 0, 'actual Earth occlusion still exercises the distant lens depth precision');
}

function verifyConsistentLetterOrbit(film, letters) {
  const rings = film.scene.getObjectByName('snn-orbit-rings');
  const north = new Vector3(0, 1, 0);
  const orbitCenter = new Vector3(0, 18, 0);
  const sample = (time) => {
    film.update(6 + time, 1.8);
    film.scene.updateMatrixWorld(true);
    return { center: letters.getWorldPosition(new Vector3()), rotation: letters.getWorldQuaternion(new Quaternion()) };
  };
  let previous;
  for (let index = 0; index <= 180; index += 1) {
    const time = index / 10;
    const current = sample(time);
    const offset = current.center.clone().sub(orbitCenter);
    assert.ok(Math.abs(current.center.y - 18) < 1e-8 && Math.abs(Math.hypot(current.center.x, current.center.z) - 205) < 1e-8,
      `the physical word follows the same equatorial plane and radius at film ${6 + time}s`);
    const authoredAngle = letterAngle(time);
    const expectedCenter = new Vector3(Math.sin(authoredAngle) * 205, 18, Math.cos(authoredAngle) * 205);
    assert.ok(current.center.distanceTo(expectedCenter) < 1e-8, 'the orbit preserves the authored angular schedule');
    assert.ok(north.clone().applyQuaternion(current.rotation).distanceTo(north) < 1e-8,
      'the actual lettering stays upright instead of inheriting the camera-route tilt');
    assert.ok(north.clone().applyQuaternion(rings.getWorldQuaternion(new Quaternion())).distanceTo(north) < 1e-8,
      'the rings keep the same equatorial normal throughout the film');
    assert.ok(getOrbitPose(time).frame.angleTo(new Quaternion()) < 1e-8,
      'the returned orbital frame remains the world frame before and after the reveal');
    assert.equal(letters.visible, true, `the letters remain enabled at film ${6 + time}s`);
    if (previous && time <= 11) {
      const angle = Math.atan2(north.dot(previous.offset.clone().cross(offset)), previous.offset.dot(offset));
      assert.ok(Math.abs(angle - (-0.16 * 0.1)) < 1e-8,
        'the original constant angular speed remains unchanged through the first two shots');
      const expected = new Quaternion().setFromAxisAngle(north, angle).multiply(previous.rotation);
      assert.ok(expected.angleTo(current.rotation) < 1e-6,
        'the word rotates with its orbit without a camera-dependent facing adjustment');
    }
    previous = { ...current, offset };
  }
}

function verifyWordJustOutsideFrame(film) {
  const seconds = 11.9;
  const aspect = 16 / 9;
  film.update(seconds, aspect);
  film.scene.updateMatrixWorld(true);
  const letters = film.scene.getObjectByName('snn-orbit-letters');
  assert.equal(letters.visible, true, 'the authored starting phase keeps the word enabled');
  const cameraMatrix = film.camera.matrixWorld.elements.slice();
  let minimumX = Infinity;
  let checkedInk = false;
  let checkedFill = false;
  letters.traverse((mesh) => {
    if (!mesh.isMesh) return;
    if (mesh.name.endsWith('-ink')) checkedInk = true;
    if (mesh.name.endsWith('-volume')) checkedFill = true;
    const vertices = mesh.geometry.attributes.position;
    for (let index = 0; index < vertices.count; index += 1) {
      const point = new Vector3().fromBufferAttribute(vertices, index).applyMatrix4(mesh.matrixWorld);
      assert.ok(point.clone().applyMatrix4(film.camera.matrixWorldInverse).z < 0,
        'the word remains in front of the camera rather than disappearing behind it');
      point.project(film.camera);
      assert.ok(point.z > -1 && point.z < 1, 'depth clipping does not hide the shifted word');
      minimumX = Math.min(minimumX, point.x);
    }
  });
  assert.ok(checkedInk && checkedFill, 'the frame check includes actual stroke and fill geometry');
  // With all vertices in front of the lens and beyond the same right plane,
  // every triangle is outside, including edges whose endpoints could otherwise
  // straddle the frame. The ink has a small margin beyond the body of the type.
  assert.ok(minimumX > 1 && minimumX < 1.02,
    `the entire word sits just beyond the 16:9 right edge at 11.9s: x=${minimumX}`);

  film.update(seconds, aspect, { orbitSettings: { phase: 2 } });
  film.scene.updateMatrixWorld(true);
  assert.deepEqual(film.camera.matrixWorld.elements, cameraMatrix,
    'changing the starting phase does not move the authored camera');
  const frustum = new Frustum().setFromProjectionMatrix(
    film.camera.projectionMatrix.clone().multiply(film.camera.matrixWorldInverse),
  );
  let inkReturns = false;
  letters.traverse((mesh) => {
    if (!mesh.isMesh || !mesh.name.endsWith('-ink')) return;
    const vertices = mesh.geometry.attributes.position;
    for (let index = 0; index < vertices.count; index += 1) {
      const point = new Vector3().fromBufferAttribute(vertices, index).applyMatrix4(mesh.matrixWorld);
      if (frustum.containsPoint(point)) inkReturns = true;
    }
  });
  assert.ok(inkReturns, 'undoing two degrees returns real ink geometry inside the camera frustum');
  film.update(seconds, aspect);
}

function verifyEditedOrbitScene(film, letters, rings) {
  const variants = [
    { radius: 270, tilt: 24, heading: -38, phase: 55, speed: 1.5 },
    { radius: 360, tilt: -90, heading: 180, phase: -180, speed: -0.5 },
    { phase: 30 },
    { radius: Infinity, tilt: NaN, heading: 'west', phase: null, speed: 'fast' },
    { radius: 1000, tilt: -120, heading: 900, phase: -1000, speed: -1000 },
    null,
  ];
  const geometry = [];
  for (const group of [letters, rings]) group.traverse((object) => {
    if (object.isMesh && object.geometry?.attributes.position) geometry.push(object);
  });
  for (const aspect of [0.6, 1, 1.8]) {
    for (const time of [0, 1.8, 5.8, 7.2, 8.6, 11, 12, 14, 18]) {
      const options = { weave: 0.7, ringSpeed: 1.25 };
      film.update(6 + time, aspect, options);
      film.scene.updateMatrixWorld(true);
      const cameraMatrix = film.camera.matrixWorld.elements.slice();
      const projection = film.camera.projectionMatrix.elements.slice();
      const lens = { fov: film.camera.fov, aspect: film.camera.aspect };
      const ringScale = rings.scale.clone();
      for (const orbitSettings of variants) {
        const expected = applyOrbitSettings(getOrbitPose(time, options.weave, aspect), time, orbitSettings);
        const expectedRadius = Math.sqrt(expected.center.lengthSq() - 18 ** 2);
        film.update(6 + time, aspect, { ...options, orbitSettings });
        film.scene.updateMatrixWorld(true);
        assert.deepEqual(film.camera.matrixWorld.elements, cameraMatrix,
          'editing the orbit never moves or rotates the actual film camera');
        assert.deepEqual({ fov: film.camera.fov, aspect: film.camera.aspect }, lens);
        for (const index of [0, 5, 8, 9]) assert.ok(
          Math.abs(film.camera.projectionMatrix.elements[index] - projection[index]) < 1e-12 * Math.max(1, Math.abs(projection[index])),
          'camera framing stays identical while depth clipping can expand');
        assert.ok(letters.getWorldPosition(new Vector3()).distanceTo(expected.center) < 1e-8,
          'the actual letters use the edited radius, phase, speed, and orbital plane');
        assert.ok(letters.getWorldQuaternion(new Quaternion()).angleTo(expected.letterQuaternion) < 1e-7,
          'the actual lettering follows the edited orbital orientation');
        const ringNormal = new Vector3(0, 1, 0).applyQuaternion(rings.getWorldQuaternion(new Quaternion()));
        assert.ok(ringNormal.distanceTo(new Vector3(0, 1, 0).applyQuaternion(expected.frame)) < 1e-8,
          'the real rings share the edited plane with the type');
        const expectedScale = ringScale.clone().multiply(new Vector3(expectedRadius / 205, 1, expectedRadius / 205));
        assert.ok(rings.scale.distanceTo(expectedScale) < 1e-10,
          'ring radii scale with the orbit while preserving their vertical spacing and reveal scale');
        assert.ok(rings.scale.toArray().every((value) => Number.isFinite(value) && value > 0));
        assert.ok(Number.isFinite(film.camera.near) && film.camera.near > 0
          && Number.isFinite(film.camera.far) && film.camera.far > film.camera.near);
        assert.ok(film.camera.projectionMatrix.elements.every(Number.isFinite));
        if (expectedRadius > 359.9) {
          for (const mesh of geometry) {
            const vertices = mesh.geometry.attributes.position;
            for (let index = 0; index < vertices.count; index += 1) {
              const point = new Vector3().fromBufferAttribute(vertices, index).applyMatrix4(mesh.matrixWorld)
                .applyMatrix4(film.camera.matrixWorldInverse);
              assert.ok(-point.z <= film.camera.far + 1e-6,
                'the far plane contains all actual type and ring geometry at maximum radius');
              if (time === 0) assert.ok(-point.z >= film.camera.near - 1e-6,
                'the opening near plane also contains the expanded scene');
            }
          }
        }
        film.update(6 + time, aspect, { ...options, orbitSettings });
        assert.ok(rings.scale.distanceTo(expectedScale) < 1e-10,
          'repeated rendering does not compound the edited ring scale');
      }
    }
  }
}

function verifyPacificArcAndApproach(film) {
  film.update(6, 1.8);
  film.scene.updateMatrixWorld(true);
  const earth = film.scene.getObjectByName('earth');
  const surface = earth.getObjectByName('globe-surface');
  for (const aspect of [0.6, 1, 1.8]) {
    const step = 1e-5;
    const arrival = [-2, -1, 0, 1, 2].map((offset) => {
      const time = COAST_START + offset * step;
      film.update(6 + time, aspect);
      return { position: film.camera.position.clone(), target: getOrbitPose(time, 1, aspect).target,
        rotation: film.camera.quaternion.clone() };
    });
    for (const property of ['position', 'target']) {
      const incoming = arrival[2][property].clone().add(arrival[0][property])
        .addScaledVector(arrival[1][property], -2).divideScalar(step ** 2);
      const outgoing = arrival[4][property].clone().add(arrival[2][property])
        .addScaledVector(arrival[3][property], -2).divideScalar(step ** 2);
      assert.ok(incoming.distanceTo(outgoing) < Math.max(0.05, 0.02 * Math.max(incoming.length(), outgoing.length())),
        `${property} acceleration joins softly into the orbital arc at aspect ${aspect}`);
    }
    const angularVelocity = (from, to) => {
      const turn = to.clone().multiply(from.clone().invert());
      if (turn.w < 0) turn.set(-turn.x, -turn.y, -turn.z, -turn.w);
      const axis = new Vector3(turn.x, turn.y, turn.z);
      return axis.normalize().multiplyScalar(2 * Math.atan2(Math.hypot(turn.x, turn.y, turn.z), turn.w) / step);
    };
    const incomingTurn = angularVelocity(arrival[1].rotation, arrival[2].rotation);
    const outgoingTurn = angularVelocity(arrival[2].rotation, arrival[3].rotation);
    assert.ok(incomingTurn.distanceTo(outgoingTurn) < Math.max(0.001, 0.02 * Math.max(incomingTurn.length(), outgoingTurn.length())),
      'the actual camera turns into the cruise without a sudden angular-velocity change');
    const anchors = [COAST_START, (COAST_START + COAST_END) / 2, COAST_END].map((route) => {
      film.update(6 + orbitTimeForRoute(route), aspect);
      return film.camera.position.clone();
    });
    const planeNormal = anchors[1].clone().sub(anchors[0]).cross(anchors[2].clone().sub(anchors[0])).normalize();
    const circleCenter = planeNormal.clone().multiplyScalar(planeNormal.dot(anchors[0]));
    const circleRadius = anchors[0].distanceTo(circleCenter);
    const angularSpeeds = [];
    let previousFrame;
    let pitch;
    let previousLongitude = Infinity;
    let crossedAlaska = false;
    let crossedRussia = false;
    for (let sample = 0; sample <= 80; sample += 1) {
      const route = COAST_START + (COAST_END - COAST_START) * sample / 80;
      const time = orbitTimeForRoute(route);
      film.update(6 + time, aspect);
      film.scene.updateMatrixWorld(true);
      assert.ok(Math.abs(film.camera.position.length() - COAST_RADIUS) < 1e-6,
        `the actual camera stays on a concentric Pacific orbit at aspect ${aspect}`);
      const offset = film.camera.position.clone().sub(circleCenter);
      assert.ok(Math.abs(offset.dot(planeNormal)) < 1e-6 && Math.abs(offset.length() - circleRadius) < 1e-6,
        'the broad arc stays in one plane with constant curvature');
      const radial = film.camera.position.clone().normalize();
      const forward = film.camera.getWorldDirection(new Vector3());
      const tangent = planeNormal.clone().cross(offset).normalize();
      assert.ok(forward.clone().projectOnPlane(radial).normalize().dot(tangent) > 0.999999,
        'the horizontal camera heading follows the orbit tangent');
      const currentPitch = forward.dot(radial);
      if (pitch === undefined) pitch = currentPitch;
      assert.ok(pitch < -0.4 && pitch > -0.8 && Math.abs(currentPitch - pitch) < 1e-6,
        'the camera keeps a fixed downward pitch instead of chasing the coastline');
      if (previousFrame) {
        const angle = film.camera.quaternion.angleTo(previousFrame.quaternion);
        assert.ok(Math.abs(angle - offset.angleTo(previousFrame.offset)) < 1e-6,
          'the camera frame turns steadily with the orbit without extra yaw, pitch, or roll');
        angularSpeeds.push(angle / (time - previousFrame.time));
      }
      previousFrame = { quaternion: film.camera.quaternion.clone(), offset, time };
      const local = earth.worldToLocal(film.camera.position.clone());
      let longitude = Math.atan2(-local.z, local.x) * 180 / Math.PI;
      if (longitude > 0) longitude -= 360;
      const latitude = Math.asin(local.y / local.length()) * 180 / Math.PI;
      assert.ok(longitude < previousLongitude, 'the broad arc continues west across the dateline');
      assert.ok(latitude > 18 && latitude < 65, 'the orbital arc avoids a polar shortcut');
      previousLongitude = longitude;
      if (longitude < -135 && longitude > -170 && latitude > 55) crossedAlaska = true;
      if (longitude < -180 && longitude > -210 && latitude > 50) crossedRussia = true;
      if (sample === 0) assert.ok(longitude > -116 && longitude < -108 && latitude > 18 && latitude < 24,
        'the concentric route starts just south of Baja');
      if (sample === 80) assert.ok(longitude < -215 && longitude > -230 && latitude < 43,
        'the concentric route finishes by Korea and Japan');
      const ray = new Raycaster(film.camera.position, forward);
      const hit = ray.intersectObject(surface)[0];
      assert.ok(hit && Math.abs(hit.point.length() - 140) < 0.2,
        'the fixed horizon pitch keeps the real Earth beneath the optical axis');
    }
    const meanAngularSpeed = angularSpeeds.reduce((sum, value) => sum + value, 0) / angularSpeeds.length;
    assert.ok(angularSpeeds.every((speed) => Math.abs(speed - meanAngularSpeed) / meanAngularSpeed < 1e-5),
      'camera orientation has constant angular speed throughout the broad orbital arc');
    assert.ok(crossedAlaska && crossedRussia, 'the arc passes Alaska and Russia between Baja and Japan');
  }
}

function verifyOutsideInsideOutsidePass(film, letters) {
  for (const aspect of [0.6, 1, 1.8]) {
    film.update(14, aspect);
    film.scene.updateMatrixWorld(true);
    const arrival = letters.worldToLocal(film.camera.position.clone());
    assert.ok(arrival.x > 110 && arrival.z < -24,
      'the camera arrives behind the trailing N and clear of its right upright');

    for (const weave of [0, 1, 1.5]) {
      const path = [];
      let previousX = Infinity;
      let previousRadial;
      for (let index = 0; index <= 600; index += 1) {
        const seconds = 14 + 3 * index / 600;
        film.update(seconds, aspect, { weave });
        film.scene.updateMatrixWorld(true);
        const local = letters.worldToLocal(film.camera.position.clone());
        path.push({ seconds, local });
        assert.ok(local.x <= previousX + 1e-8, 'the weave progresses from the trailing N toward S without reversing');
        previousX = local.x;
        const radial = film.camera.position.clone().setY(0).normalize();
        if (previousRadial) {
          const angle = Math.atan2(new Vector3(0, 1, 0).dot(previousRadial.clone().cross(radial)), previousRadial.dot(radial));
          assert.ok(angle < 0, 'the camera keeps following the actual orbital direction during each inward/outward crossing');
        }
        previousRadial = radial;
      }
      // Locate geometric events instead of requiring the route to visit the
      // old spline knots at specific times. The physical glyphs define sides.
      const passes = [];
      for (const [letterName, side] of [
        ['snn-letter-n-2', 1], ['snn-letter-n-1', -1], ['snn-letter-s', 1],
      ]) {
        const glyph = letters.getObjectByName(letterName);
        const nearest = path.reduce((best, sample) => (
          Math.abs(sample.local.x - glyph.position.x) < Math.abs(best.local.x - glyph.position.x) ? sample : best
        ));
        assert.ok(Math.abs(nearest.local.x - glyph.position.x) < 1,
          `the camera passes the center of ${letterName}`);
        assert.ok(side * nearest.local.z > 24, `${letterName} uses the requested Earth-relative side`);
        film.update(nearest.seconds, aspect, { weave });
        film.scene.updateMatrixWorld(true);
        const radialDifference = film.camera.position.length() - glyph.getWorldPosition(new Vector3()).length();
        assert.ok(side * radialDifference > 15,
          `${letterName}: outside means farther from Earth, inside means closer`);
        passes.push(nearest.seconds);
      }
      assert.ok(passes[0] < passes[1] && passes[1] < passes[2],
        'the camera passes outside the last N, inside the middle N, then outside S in order');
      const crossings = [[], []];
      for (const sample of path) {
        if (sample.seconds <= passes[0] || sample.seconds >= passes[2] || Math.abs(sample.local.z) > 18) continue;
        const gap = sample.local.x > 0 ? 37 : -37;
        assert.ok(Math.abs(sample.local.x - gap) < 3,
          'the depth crossings stay centered in the actual gaps between glyphs');
        crossings[gap > 0 ? 0 : 1].push(sample.local.z);
      }
      for (const [index, crossing] of crossings.entries()) {
        const direction = index === 0 ? -1 : 1;
        assert.ok(crossing.length > 20 && Math.min(...crossing) < -17 && Math.max(...crossing) > 17,
          'each gap passage crosses the complete 34-unit glyph depth');
        for (let index = 1; index < crossing.length; index += 1) assert.ok(
          direction * (crossing[index] - crossing[index - 1]) > 0,
          'each gap crosses the word depth in one direction');
      }
    }

    let previousRotation;
    const step = 0.005;
    for (let time = APPROACH_DURATION - 0.02; time <= 14 + 0.02; time += step) {
      film.update(6 + time, aspect);
      if (previousRotation) {
        const degreesPerSecond = film.camera.quaternion.angleTo(previousRotation) * 180 / Math.PI / step;
        assert.ok(degreesPerSecond < 240,
          `the approach, weave and retreat avoid camera whips or pole flips: ${degreesPerSecond}°/s at ${6 + time}s`);
      }
      previousRotation = film.camera.quaternion.clone();
    }

    const delta = 1e-4;
    const angularVelocity = (from, to) => {
      const turn = to.clone().multiply(from.clone().invert());
      if (turn.w < 0) turn.set(-turn.x, -turn.y, -turn.z, -turn.w);
      const axis = new Vector3(turn.x, turn.y, turn.z);
      return axis.normalize().multiplyScalar(2 * Math.atan2(Math.hypot(turn.x, turn.y, turn.z), turn.w) / delta);
    };
    for (const join of WEAVE_JOINS.concat(14)) {
      const rotations = [-delta, 0, delta].map((offset) => {
        film.update(6 + join + offset, aspect);
        return film.camera.quaternion.clone();
      });
      const incoming = angularVelocity(rotations[0], rotations[1]);
      const outgoing = angularVelocity(rotations[1], rotations[2]);
      assert.ok(incoming.distanceTo(outgoing) < Math.max(0.05, 0.03 * Math.max(incoming.length(), outgoing.length())),
        `actual camera angular velocity stays continuous at film ${6 + join}s`);
    }
  }
}

test('orbit film seeks reversibly, clears letter volumes, and reveals readable moving SNN', async () => {
  const originalDocument = globalThis.document;
  const context = Object.fromEntries(
    ['fillRect', 'beginPath', 'moveTo', 'lineTo', 'closePath', 'arc', 'fill', 'stroke']
      .map((name) => [name, () => {}]),
  );
  globalThis.document = { createElement: () => ({ width: 0, height: 0, getContext: () => context }) };
  const server = await createServer({
    server: { middlewareMode: true, hmr: false, watch: null },
    appType: 'custom', logLevel: 'silent',
  });
  let film;
  let opening;
  try {
    const { createOrbitFilm } = await server.ssrLoadModule('/src/orbit-film.js');
    const { createFlatInkTransition } = await server.ssrLoadModule('/src/transition-flat.js');
    const renderer = { capabilities: { getMaxAnisotropy: () => 1 } };
    film = createOrbitFilm(renderer);
    opening = createFlatInkTransition(renderer, 'nose');
    verifyOpaqueOpening(film);
    verifyPacificArcAndApproach(film);
    verifyWordJustOutsideFrame(film);

    for (const aspect of [0.6, 1, 1.8]) {
      opening.update(1, aspect);
      opening.camera.updateMatrixWorld(true);
      film.update(6, aspect);
      film.scene.updateMatrixWorld(true);
      film.camera.updateMatrixWorld(true);
      const earth = film.scene.getObjectByName('earth');
      for (const [longitude, latitude] of [[-115, 12], [-120, 37], [-71, -30], [-36, -10]]) {
        const point = geoVector(longitude, latitude, 140);
        const before = point.clone().project(opening.camera);
        const after = earth.localToWorld(point.clone()).project(film.camera);
        assert.ok(Math.hypot(before.x - after.x, before.y - after.y) < 0.002,
          `globe composition matches the flat-opening endpoint at aspect ${aspect}`);
      }
    }

    for (const selected of ['nose', 'eye', 'ear']) {
      const settings = { opening: selected, weave: 1, ringSpeed: 1.25 };
      const forward = new Map();
      for (const seconds of [0, 2.7, 4, 6, 10, 13.5, 16, 20, 24]) {
        const phase = film.update(seconds, 1.8, settings);
        assert.ok(film.camera.projectionMatrix.elements.every(Number.isFinite));
        assert.ok(film.camera.projectionMatrix.elements[0] > 0);
        assert.ok(film.camera.projectionMatrix.elements[5] > 0);
        forward.set(seconds, playbackState(film, phase));
      }
      for (const seconds of [...forward.keys()].reverse()) {
        const phase = film.update(seconds, 1.8, settings);
        assert.deepEqual(playbackState(film, phase), forward.get(seconds),
          `${selected} opening and orbital scene seek exactly to ${seconds}`);
      }
    }

    film.update(6, 1.8);
    const letters = film.scene.getObjectByName('snn-orbit-letters');
    const letterGroups = ['snn-letter-s', 'snn-letter-n-1', 'snn-letter-n-2']
      .map((name) => letters.getObjectByName(name));
    verifyConsistentLetterOrbit(film, letters);
    verifyOutsideInsideOutsidePass(film, letters);
    verifyLetterSurfaceClearance(film, letterGroups);
    const contains = letterGroups.map((letter) => extrusionContains(letter.getObjectByName(`${letter.name}-volume`)));
    // Cover every weave slider setting, including intermediate camera offsets.
    for (const aspect of [0.6, 1, 1.8]) {
      for (let setting = 0; setting <= 30; setting += 1) {
        const weave = setting / 20;
        for (let sample = 0; sample <= 360; sample += 1) {
          const seconds = 6 + sample / 20;
          film.update(seconds, aspect, { weave });
          film.scene.updateMatrixWorld(true);
          for (let index = 0; index < contains.length; index += 1) {
            assert.equal(contains[index](film.camera.position), false,
              `camera clears ${letterGroups[index].name} at ${seconds}s, weave ${weave}, aspect ${aspect}`);
          }
        }
      }
    }

    let previousX = Infinity;
    for (const seconds of [20, 21, 22, 23, 24]) {
      film.update(seconds, 1.8);
      film.scene.updateMatrixWorld(true);
      film.camera.updateMatrixWorld(true);
      const centers = letterGroups.map((letter) => letter.getWorldPosition(new Vector3()).project(film.camera));
      assert.ok(centers[0].x < centers[1].x && centers[1].x < centers[2].x, 'S, N, N read left to right');
      const front = new Vector3(0, 0, 1).transformDirection(letters.matrixWorld);
      const toCamera = film.camera.position.clone().sub(letters.getWorldPosition(new Vector3())).normalize();
      assert.ok(front.dot(toCamera) > 0.9, 'the fronts of the letters face the audience');
      const currentX = letters.getWorldPosition(new Vector3()).project(film.camera).x;
      assert.ok(currentX < previousX, 'the readable word travels from right to left');
      if (seconds === 20) assert.ok(currentX > 0, 'the crossing begins right of the globe center');
      if (seconds === 24) assert.ok(currentX < 0, 'the crossing ends left of the globe center');
      previousX = currentX;
    }

    const rings = film.scene.getObjectByName('snn-orbit-rings');
    verifyEditedOrbitScene(film, letters, rings);
    const anglesAt = (seconds, ringSpeed = 1) => {
      film.update(seconds, 1.8, { ringSpeed });
      return rings.children.map((ring) => ring.rotation.y + rings.rotation.y);
    };
    const startAngles = anglesAt(20);
    const endAngles = anglesAt(24);
    const turns = endAngles.map((angle, index) => angle - startAngles[index]);
    assert.ok(turns.every((turn) => Math.abs(turn) > 0.001), 'all rings move');
    assert.ok(Math.abs(turns[0] - turns[1]) > 0.01 && Math.abs(turns[1] - turns[2]) > 0.01,
      'rings rotate at different speeds');
    assert.deepEqual(anglesAt(20, 0), anglesAt(24, 0), 'zero ring speed freezes rotation');
  } finally {
    film?.dispose();
    opening?.dispose();
    await server.close();
    if (originalDocument === undefined) delete globalThis.document;
    else globalThis.document = originalDocument;
  }
});
