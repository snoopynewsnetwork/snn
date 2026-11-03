import * as THREE from 'three';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';
import { contours, makePath } from './snoopy.js';

const INK = '#252221';
const WHITE = '#ffffff';
const ORIGIN = new THREE.Vector2(147, 170);

// Inflate a traced silhouette into a closed, rounded volume. At z-facing
// orthographic view its projection is the original drawing, not a billboard.
function roundedVolume(commands, center, depth, baseZ = () => 0) {
  const path = makePath(commands);
  path.closePath();
  const boundary = path.getSpacedPoints(192).slice(0, -1);
  const count = boundary.length;
  const rings = 48;
  const positions = [];
  const indices = [];

  for (let ring = 0; ring <= rings; ring++) {
    const phi = -Math.PI / 2 + ring / rings * Math.PI;
    const spread = Math.cos(phi);
    for (const point of boundary) {
      const x = center[0] + (point.x - center[0]) * spread;
      const y = center[1] + (point.y - center[1]) * spread;
      positions.push(x - ORIGIN.x, ORIGIN.y - y, baseZ(x, y) + Math.sin(phi) * depth);
    }
  }
  for (let ring = 0; ring < rings; ring++) {
    for (let point = 0; point < count; point++) {
      const next = (point + 1) % count;
      const a = ring * count + point;
      const b = ring * count + next;
      const c = (ring + 1) * count + point;
      const d = (ring + 1) * count + next;
      indices.push(a, c, b, b, c, d);
    }
  }
  let geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setIndex(indices);

  // Normalize winding, including silhouettes drawn in either direction.
  const area = THREE.ShapeUtils.area(boundary);
  if (area < 0) {
    for (let i = 0; i < indices.length; i += 3) [indices[i], indices[i + 1]] = [indices[i + 1], indices[i]];
    geometry.setIndex(indices);
  }
  // Each end ring collapses to one pole. Weld it before computing normals so
  // the outline shell cannot form radial cracks around duplicated pole vertices.
  const welded = mergeVertices(geometry, 1e-4);
  geometry.dispose();
  geometry = welded;
  geometry.computeVertexNormals();

  // Analytic surface lookup keeps ink attached to the inflated side.
  function front(x, y) {
    const dx = x - center[0];
    const dy = y - center[1];
    if (Math.abs(dx) + Math.abs(dy) < 1e-5) return baseZ(x, y) + depth;
    let intersection = Infinity;
    for (let i = 0; i < count; i++) {
      const a = boundary[i];
      const b = boundary[(i + 1) % count];
      const sx = b.x - a.x;
      const sy = b.y - a.y;
      const cross = dx * sy - dy * sx;
      if (Math.abs(cross) < 1e-8) continue;
      const ax = a.x - center[0];
      const ay = a.y - center[1];
      const t = (ax * sy - ay * sx) / cross;
      const u = (ax * dy - ay * dx) / cross;
      if (t > 0 && u >= 0 && u <= 1) intersection = Math.min(intersection, t);
    }
    const ratio = Number.isFinite(intersection) ? Math.min(1, 1 / intersection) : 1;
    return baseZ(x, y) + depth * Math.sqrt(Math.max(0, 1 - ratio * ratio));
  }
  return { geometry, front };
}

function paintMaterial(color, shading) {
  const material = new THREE.MeshBasicMaterial({ color });
  material.onBeforeCompile = (shader) => {
    shader.uniforms.volumeShading = shading;
    shader.vertexShader = `varying vec3 volumeNormal;\n${shader.vertexShader}`
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvolumeNormal = normalize(normalMatrix * normal);');
    shader.fragmentShader = `uniform float volumeShading;\nvarying vec3 volumeNormal;\n${shader.fragmentShader}`
      .replace('#include <opaque_fragment>', `
        float light = max(dot(normalize(volumeNormal), normalize(vec3(-0.45, 0.8, 1.0))), 0.0);
        outgoingLight *= 1.0 - volumeShading * (1.0 - light) * 0.24;
        #include <opaque_fragment>
      `);
  };
  return material;
}

export function createSnoopy3D() {
  const root = new THREE.Group();
  root.name = 'snoopy-3d';
  const shading = { value: 0 };
  const white = paintMaterial(WHITE, shading);
  const black = paintMaterial(INK, shading);
  const lineMaterial = new THREE.MeshBasicMaterial({ color: INK });
  const whiteLine = new THREE.MeshBasicMaterial({ color: WHITE });
  const outline = new THREE.MeshBasicMaterial({ color: INK, side: THREE.BackSide });

  function solid(name, commands, center, depth, baseZ = () => 0, material = white, outlined = true) {
    const volume = roundedVolume(commands, center, depth, baseZ);
    const mesh = new THREE.Mesh(volume.geometry, material);
    mesh.name = name;
    root.add(mesh);
    if (outlined) {
      const hull = new THREE.Mesh(volume.geometry, outline);
      hull.name = `${name}-outline`;
      // Expanding around the volume's center avoids the self-intersections
      // produced by normal extrusion at the drawing's tight concave curves.
      volume.geometry.computeBoundingBox();
      const bounds = volume.geometry.boundingBox;
      const size = bounds.getSize(new THREE.Vector3());
      const origin = bounds.getCenter(new THREE.Vector3());
      hull.scale.set(1 + 8 / size.x, 1 + 8 / size.y, 1 + 8 / size.z);
      hull.position.copy(origin).multiply(new THREE.Vector3(1, 1, 1).sub(hull.scale));
      root.add(hull);
    }
    return volume;
  }

  function ink(name, commands, surface, radius = 1.9, material = lineMaterial, side = 1) {
    const points = makePath(commands).getSpacedPoints(72).map((p) =>
      new THREE.Vector3(p.x - ORIGIN.x, ORIGIN.y - p.y, side * (surface(p.x, p.y) + 1.4)),
    );
    const curve = new THREE.CatmullRomCurve3(points);
    const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, 144, radius, 8, false), material);
    mesh.name = name;
    root.add(mesh);
    for (const point of [points[0], points.at(-1)]) {
      const cap = new THREE.Mesh(new THREE.SphereGeometry(radius, 8, 6), material);
      cap.position.copy(point);
      root.add(cap);
    }
  }

  const body = solid('body', contours.body, [165, 242], 28);
  const legShape = [
    ['M', 170, 279], ['C', 169, 288, 171, 302, 167, 308],
    ['L', 188, 312], ['C', 183, 301, 184, 290, 185, 280], ['Z'],
  ];
  solid('far-leg', legShape, [177, 296], 10, () => -19);
  solid('near-leg', legShape, [177, 296], 10, () => 20);
  const paw = [
    ['M', 167, 305], ['C', 148, 300, 123, 302, 109, 310],
    ['C', 99, 312, 93, 318, 98, 325],
    ['C', 101, 333, 123, 331, 143, 331],
    ['C', 165, 331, 194, 332, 211, 328],
    ['C', 222, 326, 220, 320, 210, 315],
    ['C', 196, 309, 179, 306, 167, 305], ['Z'],
  ];
  const farPaw = paw.map(([command, ...coords]) => [command, ...coords.map((v, i) => v - (i % 2 === 0 ? 10 : 3))]);
  const farFoot = solid('far-foot', farPaw, [145, 315], 16, () => -19);
  const foot = solid('near-foot', paw, [155, 318], 18, () => 20);
  solid('tail', contours.tail, [211, 281], 11, () => -2);
  for (const path of contours.farToes) ink('far-toes', path, farFoot.front, 1.6);
  for (const path of contours.nearToes) ink('near-toes', path, foot.front, 1.6);
  const armOutline = [
    ...contours.arm,
    ['C', 191, 249, 186, 235, 178, 228],
    ['C', 174, 226, 170, 226, 169, 231], ['Z'],
  ];
  const arm = solid('near-arm', armOutline, [179, 255], 6, (x, y) => body.front(x, y) - 2, white, false);
  ink('arm-line', contours.arm, arm.front, 2.1);

  const head = solid('head', contours.head, [162, 91], 66);
  const nose = solid('nose', contours.nose, [39, 119], 17, () => 0, black);
  ink('nose-highlight', [
    ['M', 39, 108], ['C', 30, 109, 25, 118, 29, 124],
    ['C', 31, 129, 35, 129, 39, 126],
  ], nose.front, 2.4, whiteLine);
  ink('eye', [['M', 149, 65], ['C', 148, 70, 150, 76, 150, 81]], head.front, 3.2);
  ink('smile', contours.smile, head.front, 1.75);
  ink('smile-dimple', contours.smileDimple, head.front, 1.9);
  ink('far-eye', [['M', 149, 65], ['C', 148, 70, 150, 76, 150, 81]], head.front, 3.2, lineMaterial, -1);
  ink('far-smile', contours.smile, head.front, 1.75, lineMaterial, -1);
  ink('hair', contours.hair, () => 0, 1.5);

  const earBoundary = [
    ['M', 240, 62], ['C', 229, 63, 207, 86, 202, 107],
    ['C', 198, 123, 200, 145, 209, 152],
    ['C', 220, 161, 237, 153, 248, 141],
    ['C', 262, 124, 266, 99, 259, 80],
    ['C', 255, 70, 250, 62, 240, 62], ['Z'],
  ];
  const ear = solid('near-ear', earBoundary, [231, 112], 7, (x, y) => head.front(x, y) + 2);
  const earPatch = [
    ['M', 243, 66], ['C', 231, 68, 214, 90, 210, 110],
    ['C', 207, 124, 210, 142, 218, 147],
    ['C', 229, 151, 245, 136, 251, 121],
    ['C', 259, 104, 258, 84, 250, 72],
    ['C', 248, 68, 246, 66, 243, 66], ['Z'],
  ];
  const earInk = solid('near-ear-ink', earPatch, [233, 111], 2, (x, y) => ear.front(x, y) + 0.7, black, false);
  for (const path of contours.earHighlights) ink('ear-highlight', path, earInk.front, 0.8, whiteLine);

  const farEar = solid('far-ear', earBoundary, [231, 112], 7, (x, y) => -head.front(x, y) - 2);
  solid('far-ear-ink', earPatch, [233, 111], 2, (x, y) => -ear.front(x, y) - 0.7, black, false);

  // The collar is a real ring around the neck, so it occludes correctly above.
  const collar = new THREE.Mesh(new THREE.TorusGeometry(12.5, 2.9, 10, 64), lineMaterial);
  collar.name = 'collar';
  collar.position.set(18, -10, 0);
  collar.rotation.x = Math.PI / 2;
  collar.rotation.y = -0.13;
  root.add(collar);

  return {
    root,
    parts: { head, nose, ear, farEar, body },
    setViewProgress(progress) { shading.value = progress; },
    dispose() {
      const geometries = new Set();
      root.traverse((object) => { if (object.geometry) geometries.add(object.geometry); });
      for (const geometry of geometries) geometry.dispose();
      for (const material of [white, black, lineMaterial, whiteLine, outline]) material.dispose();
    },
  };
}
