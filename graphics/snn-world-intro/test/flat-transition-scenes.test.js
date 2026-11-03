import assert from 'node:assert/strict';
import test from 'node:test';
import { createServer } from 'vite';
import { Raycaster, Vector2, Vector3 } from 'three';
import { geoContains } from 'd3-geo';
import { feature } from 'topojson-client';
import world from 'world-atlas/land-110m.json' with { type: 'json' };
import { geoVector, SPHERE_VIEW } from '../src/globe-projection.js';

const land = feature(world, world.objects.land);

function drawingState(root) {
  const state = [];
  root.updateMatrixWorld(true);
  root.traverse((object) => {
    if (!object.geometry) return;
    state.push({
      name: object.name,
      vertices: object.geometry.attributes.position.array.slice(),
      transform: object.matrixWorld.elements.slice(),
    });
  });
  return state;
}

function viewportSamples(camera, inspect) {
  camera.updateMatrixWorld(true);
  const raycaster = new Raycaster();
  // Include viewport edges and interior, since a corner-only check can miss
  // a white highlight or an ocean inlet inside the proposed ink match.
  for (let row = 0; row <= 8; row += 1) {
    for (let column = 0; column <= 8; column += 1) {
      raycaster.setFromCamera(new Vector2(column / 4 - 1, row / 4 - 1), camera);
      inspect(raycaster, `${column},${row}`);
    }
  }
}

function playbackState(transition, phase, uniforms) {
  const { camera, scene } = transition;
  return {
    phase,
    position: camera.position.toArray(),
    quaternion: camera.quaternion.toArray(),
    projection: camera.projectionMatrix.elements.slice(),
    snoopyVisible: scene.getObjectByName('snoopy').visible,
    earthVisible: scene.getObjectByName('earth').visible,
    surfaceProgress: uniforms.surfaceProgress.value,
    shadingProgress: uniforms.shadingProgress.value,
  };
}

test('flat ink transitions preserve the drawing, match solid ink, and scrub reversibly', async () => {
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
  const transitions = [];
  try {
    const { createFlatInkTransition } = await server.ssrLoadModule('/src/transition-flat.js');
    const renderer = { capabilities: { getMaxAnisotropy: () => 1 } };
    for (const name of ['nose', 'eye', 'ear']) {
      const transition = createFlatInkTransition(renderer, name);
      transitions.push(transition);
      const { scene, camera } = transition;
      const snoopy = scene.getObjectByName('snoopy');
      const surface = scene.getObjectByName('globe-surface');
      const shader = {
        uniforms: {}, vertexShader: '#include <begin_vertex>', fragmentShader: '#include <opaque_fragment>',
      };
      surface.material.onBeforeCompile(shader);
      const original = drawingState(snoopy);
      assert.ok(original.length > 0, `${name}: the flat reference contains artwork`);
      for (const mesh of original) {
        for (let index = 2; index < mesh.vertices.length; index += 3) {
          assert.equal(mesh.vertices[index], 0, `${name}: ${mesh.name} is planar`);
        }
      }

      for (const aspect of [0.6, 1, 1.6]) {
        const forward = new Map();
        for (const progress of [0, 0.2, 0.35, 0.46 - 1e-6, 0.46, 0.55, 0.8, 1]) {
          const phase = transition.update(progress, aspect);
          assert.deepEqual(drawingState(snoopy), original, `${name}: artwork stays fixed at ${progress}`);
          if (snoopy.visible) {
            assert.ok(camera.getWorldDirection(new Vector3()).distanceTo(new Vector3(0, 0, -1)) < 1e-10,
              `${name}: camera remains straight-on at ${progress}`);
            assert.ok(camera.isOrthographicCamera, `${name}: the drawing has no perspective`);
          }
          forward.set(progress, playbackState(transition, phase, shader.uniforms));
        }
        for (const progress of [...forward.keys()].reverse()) {
          const phase = transition.update(progress, aspect);
          assert.deepEqual(playbackState(transition, phase, shader.uniforms), forward.get(progress),
            `${name}: reverse scrubbing exactly restores ${progress}`);
        }

        transition.update(0.46 - 1e-6, aspect);
        assert.equal(snoopy.visible, true);
        viewportSamples(camera, (raycaster, sample) => {
          const visible = raycaster.intersectObject(snoopy, true)
            .sort((a, b) => b.object.renderOrder - a.object.renderOrder)[0]?.object;
          assert.ok(visible, `${name}: outgoing viewport ${sample} is covered at aspect ${aspect}`);
          assert.equal(visible.material.color.getHexString(), '252221',
            `${name}: outgoing viewport ${sample} is solid ink at aspect ${aspect}`);
          assert.equal(visible.material.opacity, 1, `${name}: no fading at the match cut`);
        });

        transition.update(0.46, aspect);
        scene.updateMatrixWorld(true);
        assert.equal(snoopy.visible, false);
        assert.equal(scene.getObjectByName('earth').visible, true);
        assert.equal(shader.uniforms.surfaceProgress.value, 1, `${name}: land ink is fully visible at the cut`);
        assert.equal(shader.uniforms.shadingProgress.value, 0, `${name}: incoming ink matches the unshaded drawing`);
        viewportSamples(camera, (raycaster, sample) => {
          const hit = raycaster.intersectObject(surface)[0];
          assert.ok(hit?.uv, `${name}: incoming viewport ${sample} hits the globe`);
          const coordinates = [hit.uv.x * 360 - 180, hit.uv.y * 180 - 90];
          assert.ok(geoContains(land, coordinates),
            `${name}: incoming viewport ${sample} is on land at aspect ${aspect}: ${coordinates}`);
        });

        transition.update(1, aspect);
        assert.equal(shader.uniforms.shadingProgress.value, 1, `${name}: globe has full shading at the end`);
        const expected = geoVector(SPHERE_VIEW.longitude, SPHERE_VIEW.latitude, 650);
        assert.ok(camera.position.distanceTo(expected) < 1e-9, `${name}: matches the existing globe camera`);
        assert.ok(camera.getWorldDirection(new Vector3()).distanceTo(expected.clone().normalize().negate()) < 1e-9,
          `${name}: final camera looks at the globe center`);
      }
    }
  } finally {
    for (const transition of transitions) transition.dispose();
    await server.close();
    if (originalDocument === undefined) delete globalThis.document;
    else globalThis.document = originalDocument;
  }
});
