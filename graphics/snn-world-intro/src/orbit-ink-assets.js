import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const INK = '#252221';
const PAPER = '#ffffff';
const SIDE = '#e9e5dc';
export const LETTER_WIDTH = 208;
export const LETTER_HEIGHT = 72;
export const LETTER_DEPTH = 34;

// Deliberately cut as single silhouettes: these read as abstract architecture
// close up, then as ordinary block capitals when the camera retreats.
const S = [
  [-18, 36], [30, 36], [30, 21], [-12, 21], [-16, 17], [-16, 10],
  [-12, 6], [16, 6], [30, -8], [30, -22], [16, -36], [-30, -36],
  [-30, -21], [11, -21], [16, -16], [16, -11], [11, -6], [-16, -6],
  [-30, 8], [-30, 22],
];
const N = [
  [-30, -36], [-30, 36], [-14, 36], [14, -9], [14, 36], [30, 36],
  [30, -36], [14, -36], [-14, 9], [-14, -36],
];

function polygon(points) {
  const shape = new THREE.Shape();
  points.forEach(([x, y], index) => {
    if (index === 0) shape.moveTo(x, y);
    else shape.lineTo(x, y);
  });
  shape.closePath();
  return shape;
}

function tubeBetween(a, b, radius, geometries) {
  const delta = new THREE.Vector3().subVectors(b, a);
  if (delta.lengthSq() < 0.000001) return;
  const geometry = new THREE.CylinderGeometry(radius, radius, delta.length(), 6, 1, false);
  geometry.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(
    new THREE.Vector3(0, 1, 0), delta.clone().normalize(),
  ));
  geometry.translate((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2);
  geometries.push(geometry);
}

function mergeInk(geometries, material, name) {
  const geometry = mergeGeometries(geometries, false);
  geometries.forEach((part) => part.dispose());
  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = name;
  return mesh;
}

function createLetter(points, name, materials) {
  const letter = new THREE.Group();
  letter.name = name;
  const geometry = new THREE.ExtrudeGeometry(polygon(points), {
    depth: LETTER_DEPTH, bevelEnabled: false, steps: 1, curveSegments: 1,
  });
  geometry.translate(0, 0, -LETTER_DEPTH / 2);
  const volume = new THREE.Mesh(geometry, [materials.paper, materials.side]);
  volume.name = `${name}-volume`;
  letter.add(volume);

  const ink = [];
  const hatching = [];
  points.forEach(([x, y], index) => {
    const [nx, ny] = points[(index + 1) % points.length];
    const a = new THREE.Vector3(x, y, 17);
    const b = new THREE.Vector3(nx, ny, 17);
    tubeBetween(a, b, 0.82, ink);
    tubeBetween(a.clone().setZ(-17), b.clone().setZ(-17), 0.64, ink);
    tubeBetween(a, a.clone().setZ(-17), 0.58, ink);

    const length = Math.hypot(nx - x, ny - y);
    if (length < 25 || index % 3 === 1) return;
    // Sparse strokes sit just outside the side wall, never across the face.
    // The polygon is clockwise, so its outward normal is to the left.
    const ux = (nx - x) / length;
    const uy = (ny - y) / length;
    const ox = -uy * 0.16;
    const oy = ux * 0.16;
    for (let along = 10; along < length - 7; along += 13) {
      const start = new THREE.Vector3(x + ux * along + ox, y + uy * along + oy, -10);
      const end = new THREE.Vector3(x + ux * (along + 4) + ox, y + uy * (along + 4) + oy, -2);
      tubeBetween(start, end, 0.22, hatching);
    }
  });
  letter.add(mergeInk(ink, materials.ink, `${name}-ink`));
  if (hatching.length) letter.add(mergeInk(hatching, materials.hatch, `${name}-hatching`));
  return letter;
}

function createRing(radius, width, sweep, name, materials) {
  const ring = new THREE.Group();
  ring.name = name;
  const segments = 128;
  const points = [];
  for (let i = 0; i <= segments; i += 1) {
    const angle = sweep * i / segments;
    points.push([Math.cos(angle) * (radius + width / 2), Math.sin(angle) * (radius + width / 2)]);
  }
  for (let i = segments; i >= 0; i -= 1) {
    const angle = sweep * i / segments;
    points.push([Math.cos(angle) * (radius - width / 2), Math.sin(angle) * (radius - width / 2)]);
  }
  const band = new THREE.ExtrudeGeometry(polygon(points), {
    depth: 1.1, bevelEnabled: false, steps: 1, curveSegments: 1,
  });
  band.translate(0, 0, -0.55);
  band.rotateX(Math.PI / 2);
  const surface = new THREE.Mesh(band, [materials.paper, materials.side]);
  surface.name = `${name}-paper`;
  ring.add(surface);

  const ink = [];
  for (const radialOffset of [-width / 2, width / 2]) {
    const r = radius + radialOffset;
    for (let i = 0; i < segments; i += 1) {
      const a = sweep * i / segments;
      const b = sweep * (i + 1) / segments;
      tubeBetween(
        new THREE.Vector3(Math.cos(a) * r, 0.56, Math.sin(a) * r),
        new THREE.Vector3(Math.cos(b) * r, 0.56, Math.sin(b) * r), 0.42, ink,
      );
    }
  }
  for (const angle of [0, sweep]) {
    tubeBetween(
      new THREE.Vector3(Math.cos(angle) * (radius - width / 2), 0.56, Math.sin(angle) * (radius - width / 2)),
      new THREE.Vector3(Math.cos(angle) * (radius + width / 2), 0.56, Math.sin(angle) * (radius + width / 2)),
      0.48, ink,
    );
  }
  ring.add(mergeInk(ink, materials.ink, `${name}-ink`));
  return ring;
}

export function createOrbitInkAssets() {
  const root = new THREE.Group();
  root.name = 'orbit-ink-assets';
  const letters = new THREE.Group();
  letters.name = 'snn-orbit-letters';
  const rings = new THREE.Group();
  rings.name = 'snn-orbit-rings';
  rings.visible = false;
  root.add(letters, rings);

  const materials = {
    paper: new THREE.MeshBasicMaterial({ color: PAPER }),
    side: new THREE.MeshBasicMaterial({ color: SIDE }),
    ink: new THREE.MeshBasicMaterial({ color: INK }),
    hatch: new THREE.MeshBasicMaterial({ color: INK, transparent: true, opacity: 0.54 }),
  };
  const ringMaterials = {
    paper: materials.paper.clone(),
    side: materials.side.clone(),
    ink: materials.ink.clone(),
  };
  const letterS = createLetter(S, 'snn-letter-s', materials);
  const letterN1 = createLetter(N, 'snn-letter-n-1', materials);
  const letterN2 = createLetter(N, 'snn-letter-n-2', materials);
  letterS.position.x = -74;
  letterN2.position.x = 74;
  letters.add(letterS, letterN1, letterN2);

  const arcs = [
    { radius: 180, width: 4.2, sweep: 252, y: -44, phase: 0.3, speed: 0.09 },
    { radius: 201, width: 3.5, sweep: 276, y: -47, phase: 2.25, speed: -0.14 },
    { radius: 223, width: 2.8, sweep: 236, y: -50, phase: 4.1, speed: 0.22 },
  ].map((spec, index) => {
    const mesh = createRing(spec.radius, spec.width, THREE.MathUtils.degToRad(spec.sweep), `snn-orbit-ring-${index + 1}`, ringMaterials);
    mesh.position.y = spec.y;
    rings.add(mesh);
    return { ...spec, mesh };
  });

  function update(time, { ringSpeed = 1 } = {}) {
    const t = time * ringSpeed;
    rings.rotation.y = t * 0.16;
    arcs.forEach(({ mesh, phase, speed }) => {
      mesh.rotation.y = phase + t * speed + 0.13 * Math.sin(t * 0.7 + phase);
    });
  }

  function setRingReveal(progress) {
    const alpha = THREE.MathUtils.clamp(progress, 0, 1);
    rings.visible = alpha > 0;
    rings.scale.setScalar(THREE.MathUtils.lerp(0.92, 1, alpha));
    Object.values(ringMaterials).forEach((material) => {
      const transparent = alpha < 1;
      if (material.transparent !== transparent) material.needsUpdate = true;
      material.transparent = transparent;
      material.opacity = alpha;
      material.depthWrite = !transparent;
    });
  }

  function dispose() {
    root.traverse((object) => object.geometry?.dispose());
    Object.values(materials).forEach((material) => material.dispose());
    Object.values(ringMaterials).forEach((material) => material.dispose());
  }

  update(0);
  setRingReveal(0);
  return { root, letters, rings, update, setRingReveal, dispose };
}
