import assert from 'node:assert/strict';
import test from 'node:test';
import { createServer } from 'vite';
import { Vector3 } from 'three';

function assertIdentityOrientation(object, label) {
  const { x, y, z, w } = object.quaternion;
  assert.ok(x * x + y * y + z * z < 1e-20 && Math.abs(w - 1) < 1e-10, label);
}

function verifyStationaryHeadTransition(transition) {
  const { scene, camera } = transition;
  const root = scene.getObjectByName('snoopy-3d');
  const pivot = scene.getObjectByName('prototype-head-pivot');
  const head = scene.getObjectByName('head');
  const nose = scene.getObjectByName('nose');
  const earth = scene.getObjectByName('earth');
  const patch = scene.getObjectByName('nose-unfolding-into-americas');
  const direction = new Vector3();

  for (const aspect of [0.75, 1.6]) {
    for (const progress of [0, 0.08, 0.18, 0.3, 0.34, 0.42, 0.51, 0.52, 0.65, 0.9, 1, 0.5, 0.2, 0]) {
      transition.update(progress, aspect);
      assertIdentityOrientation(root, `head: character stays still at ${progress}`);
      assertIdentityOrientation(pivot, `head: neck never tilts at ${progress}`);
      assertIdentityOrientation(head, `head: head mesh never rotates at ${progress}`);
    }
  }

  let previousX = -1;
  for (const progress of [0, 0.08, 0.12, 0.18, 0.25, 0.3, 0.34]) {
    transition.update(progress, 1.6);
    camera.getWorldDirection(direction);
    assert.ok(Math.abs(direction.y) < 1e-9, `head: camera stays on the horizontal arc at ${progress}`);
    assert.ok(direction.x >= previousX - 1e-9, 'head: camera moves toward the front without reversing');
    assert.ok(direction.z <= 1e-9, 'head: camera approaches the front from the original profile side');
    previousX = direction.x;
  }
  transition.update(0, 1.6);
  assert.ok(camera.getWorldDirection(direction).distanceTo(new Vector3(0, 0, -1)) < 1e-9,
    'head: opening camera sees the original profile');
  for (const progress of [0.34, 0.42, 0.5, 0.51]) {
    transition.update(progress, 1.6);
    assert.ok(camera.getWorldDirection(direction).distanceTo(new Vector3(1, 0, 0)) < 1e-9,
      `head: camera looks toward positive X from directly in front at ${progress}`);
  }

  function snapshot() {
    return {
      cameraPosition: camera.position.toArray(),
      cameraQuaternion: camera.quaternion.toArray(),
      projection: camera.projectionMatrix.elements.slice(),
      headVertices: head.geometry.attributes.position.array.slice(),
      nosePosition: nose.position.toArray(),
      earthPosition: earth.position.toArray(),
      patchPosition: patch.position.toArray(),
      patchVertices: patch.geometry.attributes.position.array.slice(),
      patchOpacity: patch.material.opacity,
      snoopyVisible: root.visible,
      earthVisible: earth.visible,
    };
  }

  const samples = [0.5, 0.52 - 1e-5, 0.52, 0.52 + 1e-5, 0.54, 0.6];
  const forward = new Map();
  for (const progress of samples) {
    transition.update(progress, 1.6);
    forward.set(progress, snapshot());
  }
  const before = forward.get(0.52 - 1e-5);
  const after = forward.get(0.52 + 1e-5);
  assert.ok(new Vector3().fromArray(before.cameraPosition)
    .distanceTo(new Vector3().fromArray(after.cameraPosition)) < 1e-3,
  'head: camera position stays continuous across the head-to-globe handoff');
  for (const property of ['cameraQuaternion', 'projection']) {
    assert.ok(before[property].every((value, index) => Math.abs(value - after[property][index]) < 1e-6),
      `head: ${property} stays continuous across the head-to-globe handoff`);
  }
  assert.deepEqual(before.headVertices, after.headVertices, 'head: rounding completes before the handoff');
  assert.deepEqual(before.earthPosition, after.earthPosition, 'head: globe position stays fixed during the handoff');
  assert.equal(before.snoopyVisible, true);
  assert.equal(before.earthVisible, false);
  assert.equal(after.snoopyVisible, false);
  assert.equal(after.earthVisible, true);
  for (const progress of samples.toReversed()) {
    transition.update(progress, 1.6);
    assert.deepEqual(snapshot(), forward.get(progress), `head: handoff reverses exactly at ${progress}`);
  }
}

test('transition scenes scrub reversibly, stay finite, and share the same final camera', async () => {
  // Exercise actual geometry and camera updates without needing a GPU. The
  // canvas only supplies the texture's drawing API; browser QA checks pixels.
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
  const renderer = { capabilities: { getMaxAnisotropy: () => 1 } };
  const prototypes = [];
  try {
    for (const [name, factory] of [
      ['head', 'createHeadTransition'], ['nose', 'createNoseTransition'], ['ink', 'createInkTransition'],
    ]) {
      const module = await server.ssrLoadModule(`/src/transition-${name}.js`);
      prototypes.push({ name, transition: module[factory](renderer) });
    }

    const finalCameras = [];
    for (const { name, transition } of prototypes) {
      if (name === 'head') verifyStationaryHeadTransition(transition);
      transition.update(0, 0.75);
      const head = transition.scene.getObjectByName('head');
      const originalHead = head.geometry.attributes.position.array.slice();
      const startPosition = transition.camera.position.clone();
      const startQuaternion = transition.camera.quaternion.clone();
      for (const aspect of [0.75, 1.6]) {
        for (const progress of [0, 0.25, 0.42, 0.51, 0.53, 0.65, 0.8, 1, 0.6, 0.2, 0]) {
          assert.equal(typeof transition.update(progress, aspect), 'string');
          const { camera, scene } = transition;
          assert.ok(camera.position.toArray().every(Number.isFinite), `${name}: finite camera`);
          assert.ok(camera.right > camera.left && camera.top > camera.bottom);
          scene.traverse((object) => {
            assert.ok(object.position.toArray().every(Number.isFinite), `${name}: finite object position`);
            const vertices = object.geometry?.attributes.position?.array;
            if (vertices) assert.ok(vertices.every(Number.isFinite), `${name}: finite vertices in ${object.name}`);
          });
        }
      }
      transition.update(0, 0.75);
      assert.deepEqual(head.geometry.attributes.position.array, originalHead, `${name}: original head restored`);
      assert.ok(transition.camera.position.distanceTo(startPosition) < 1e-9);
      assert.ok(1 - Math.abs(transition.camera.quaternion.dot(startQuaternion)) < 1e-9);

      transition.update(1, 0.75);
      finalCameras.push({ name, position: transition.camera.position.clone(), quaternion: transition.camera.quaternion.clone() });
      assert.equal(transition.scene.getObjectByName('snoopy-3d').visible, false);
      assert.equal(transition.scene.getObjectByName('earth').visible, true);
    }
    const reference = finalCameras[0];
    for (const camera of finalCameras.slice(1)) {
      assert.ok(camera.position.distanceTo(reference.position) < 1e-7, `${camera.name}: matching final position`);
      assert.ok(1 - Math.abs(camera.quaternion.dot(reference.quaternion)) < 1e-7, `${camera.name}: matching final orientation`);
    }
    assert.ok(reference.position.distanceTo(new Vector3()) > 0);
  } finally {
    for (const { transition } of prototypes) transition.dispose();
    await server.close();
    if (originalDocument === undefined) delete globalThis.document;
    else globalThis.document = originalDocument;
  }
});
