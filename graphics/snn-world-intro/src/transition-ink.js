import * as THREE from 'three';
import { contours, makePath } from './snoopy.js';
import { geoVector, SPHERE_VIEW } from './globe-projection.js';
import { createTransitionStage } from './transition-stage.js';

const INK = '#252221';
const SEGMENTS = 256;
const RING_RADIUS = 142.1;

function ramp(value, start, end) {
  const t = THREE.MathUtils.clamp((value - start) / (end - start), 0, 1);
  return t * t * (3 - 2 * t);
}

/**
 * A graphic handoff: lift the head's contour, redraw it as a circle, then draw
 * curved geographic strokes before the real globe acquires its continents.
 * Every pose is sampled from progress; scrubbing never depends on prior frames.
 */
export function createInkTransition(renderer) {
  const stage = createTransitionStage(renderer);
  const { scene, camera, snoopy, globe } = stage;
  const geometries = [];
  const materials = [];
  const finalDirection = geoVector(SPHERE_VIEW.longitude, SPHERE_VIEW.latitude);
  const direction = new THREE.Vector3();
  const inverseCamera = new THREE.Quaternion();
  const sourcePoint = new THREE.Vector3();

  function material(parameters) {
    const result = new THREE.MeshBasicMaterial(parameters);
    materials.push(result);
    return result;
  }

  function geometry(result) {
    geometries.push(result);
    return result;
  }

  const drawing = new THREE.Group();
  drawing.name = 'head-contour-becomes-circle';
  scene.add(drawing);
  const original = makePath(contours.head).getSpacedPoints(SEGMENTS)
    .map((point) => new THREE.Vector3(point.x - 147, 170 - point.y, 0));
  const points = Array.from({ length: SEGMENTS + 1 }, () => new THREE.Vector3());
  const startAngle = Math.atan2(original[0].y - 79, original[0].x - 15);

  // A broad, rounded-looking ink ribbon, rather than WebGL's one-pixel lines.
  const ribbonGeometry = geometry(new THREE.BufferGeometry());
  const ribbonPositions = new Float32Array((SEGMENTS + 1) * 2 * 3);
  ribbonGeometry.setAttribute('position', new THREE.BufferAttribute(ribbonPositions, 3));
  const ribbonIndices = [];
  for (let index = 0; index < SEGMENTS; index += 1) {
    const a = index * 2;
    ribbonIndices.push(a, a + 1, a + 2, a + 2, a + 1, a + 3);
  }
  ribbonGeometry.setIndex(ribbonIndices);
  const ribbonMaterial = material({
    color: INK, side: THREE.DoubleSide, transparent: true,
    depthTest: false, depthWrite: false,
  });
  const ribbon = new THREE.Mesh(ribbonGeometry, ribbonMaterial);
  ribbon.name = 'unfolding-ink-contour';
  ribbon.renderOrder = 21;
  ribbon.frustumCulled = false;
  drawing.add(ribbon);

  const fillGeometry = geometry(new THREE.BufferGeometry());
  const fillPositions = new Float32Array((SEGMENTS + 2) * 3);
  fillGeometry.setAttribute('position', new THREE.BufferAttribute(fillPositions, 3));
  const fillIndices = [];
  for (let index = 0; index < SEGMENTS; index += 1) fillIndices.push(0, index + 1, index + 2);
  fillGeometry.setIndex(fillIndices);
  const fillMaterial = material({
    color: '#ffffff', side: THREE.DoubleSide, transparent: true,
    depthTest: false, depthWrite: false,
  });
  const fill = new THREE.Mesh(fillGeometry, fillMaterial);
  fill.name = 'drawing-paper';
  fill.renderOrder = 20;
  fill.frustumCulled = false;
  drawing.add(fill);

  const tipMaterial = material({ color: INK, transparent: true, depthTest: false, depthWrite: false });
  const tip = new THREE.Mesh(geometry(new THREE.SphereGeometry(3.2, 12, 8)), tipMaterial);
  tip.name = 'travelling-ink-tip';
  tip.renderOrder = 22;
  drawing.add(tip);

  const wireMaterial = material({ color: '#777168', transparent: true, depthWrite: false });
  const wires = new THREE.Group();
  wires.name = 'sweeping-geographic-ink';
  scene.add(wires);
  const wireStrokes = [];

  function addWire(name, coordinates) {
    const curve = new THREE.CatmullRomCurve3(coordinates, false, 'centripetal');
    const tube = geometry(new THREE.TubeGeometry(curve, 192, 0.85, 6, false));
    const mesh = new THREE.Mesh(tube, wireMaterial);
    mesh.name = name;
    wires.add(mesh);
    wireStrokes.push({ mesh, indexCount: tube.index.count });
  }

  function latitude(value) {
    addWire(`drawing-latitude-${value}`, Array.from({ length: 145 }, (_, index) =>
      geoVector(SPHERE_VIEW.longitude - 90 + index / 144 * 360, value, 140.7)));
  }

  function longitude(value) {
    addWire(`drawing-longitude-${value}`, Array.from({ length: 97 }, (_, index) =>
      geoVector(value, -90 + index / 96 * 180, 140.7)));
  }

  latitude(0);
  longitude(-112.5);
  latitude(30);
  longitude(-157.5);
  latitude(-30);
  longitude(-67.5);
  latitude(60);

  function update(progress, aspect) {
    const p = THREE.MathUtils.clamp(progress, 0, 1);
    const safeAspect = Number.isFinite(aspect) && aspect > 0 ? aspect : 1;
    const rise = ramp(p, 0.06, 0.24) * THREE.MathUtils.degToRad(12);
    direction.set(0, Math.sin(rise), Math.cos(rise));
    direction.lerp(finalDirection, ramp(p, 0.3, 0.64)).normalize();
    const initialHeight = Math.max(430, 320 / safeAspect);
    const finalHeight = Math.max(360, 360 / safeAspect);
    const viewHeight = THREE.MathUtils.lerp(initialHeight, finalHeight, ramp(p, 0.25, 0.72));
    stage.setCamera([0, 0, 0], direction.toArray(), viewHeight, safeAspect);

    stage.headPivot.rotation.set(0, 0, 0);
    snoopy.root.position.set(0, 0, 0);
    snoopy.root.scale.setScalar(1);
    snoopy.setViewProgress(ramp(p, 0.06, 0.24) * 0.35);
    stage.setSnoopyOpacity(1 - ramp(p, 0.25, 0.37));
    globe.root.position.set(0, 0, 0);
    globe.root.scale.setScalar(1);
    stage.setGlobeOpacity(ramp(p, 0.51, 0.6));
    globe.setSurfaceProgress(ramp(p, 0.7, 0.88));

    // Keep the lifted contour on a camera-facing drawing plane. Its source
    // points are projected from Snoopy's actual traced silhouette, so the new
    // moving ink initially sits on his existing head outline.
    drawing.quaternion.copy(camera.quaternion);
    drawing.position.copy(direction).multiplyScalar(190);
    inverseCamera.copy(camera.quaternion).invert();
    const morph = ramp(p, 0.25, 0.54);
    const trace = ramp(p, 0.13, 0.51);
    const contourOpacity = ramp(p, 0.12, 0.16) * (1 - ramp(p, 0.57, 0.66));
    drawing.visible = p > 0.12 && p < 0.66;
    ribbonMaterial.opacity = contourOpacity;
    tipMaterial.opacity = contourOpacity * (1 - ramp(p, 0.5, 0.55));
    fillMaterial.opacity = ramp(p, 0.29, 0.38) * (1 - ramp(p, 0.51, 0.6));
    const halfStroke = THREE.MathUtils.lerp(2.45, 2.1, morph);
    const center = sourcePoint.set(15, 79, 0).applyQuaternion(inverseCamera);
    fillPositions[0] = center.x * (1 - morph);
    fillPositions[1] = center.y * (1 - morph);
    fillPositions[2] = -0.2;

    for (let index = 0; index <= SEGMENTS; index += 1) {
      const angle = startAngle - index / SEGMENTS * Math.PI * 2;
      sourcePoint.copy(original[index]).applyQuaternion(inverseCamera);
      points[index].set(
        THREE.MathUtils.lerp(sourcePoint.x, Math.cos(angle) * RING_RADIUS, morph),
        THREE.MathUtils.lerp(sourcePoint.y, Math.sin(angle) * RING_RADIUS, morph),
        0,
      );
      points[index].toArray(fillPositions, (index + 1) * 3);
    }
    for (let index = 0; index <= SEGMENTS; index += 1) {
      const before = points[(index + SEGMENTS - 1) % SEGMENTS];
      const after = points[(index + 1) % SEGMENTS];
      const dx = after.x - before.x;
      const dy = after.y - before.y;
      const length = Math.hypot(dx, dy) || 1;
      const nx = -dy / length * halfStroke;
      const ny = dx / length * halfStroke;
      const offset = index * 6;
      ribbonPositions[offset] = points[index].x + nx;
      ribbonPositions[offset + 1] = points[index].y + ny;
      ribbonPositions[offset + 2] = 0;
      ribbonPositions[offset + 3] = points[index].x - nx;
      ribbonPositions[offset + 4] = points[index].y - ny;
      ribbonPositions[offset + 5] = 0;
    }
    const traceSegments = Math.floor(trace * SEGMENTS);
    ribbonGeometry.setDrawRange(0, traceSegments * 6);
    ribbonGeometry.attributes.position.needsUpdate = true;
    fillGeometry.attributes.position.needsUpdate = true;
    tip.position.copy(points[Math.min(SEGMENTS, traceSegments)]);
    tip.visible = trace > 0 && trace < 1;

    wires.visible = p > 0.49 && p < 0.88;
    wireMaterial.opacity = (1 - ramp(p, 0.74, 0.88)) * 0.85;
    wireStrokes.forEach(({ mesh, indexCount }, index) => {
      const amount = ramp(p, 0.49 + index * 0.018, 0.67 + index * 0.018);
      mesh.geometry.setDrawRange(0, Math.floor(amount * indexCount / 36) * 36);
      mesh.visible = amount > 0;
    });

    if (p < 0.13) return 'Snoopy in profile';
    if (p < 0.28) return 'Lift the contour';
    if (p < 0.51) return 'Complete the circle';
    if (p < 0.7) return 'Draw a world';
    if (p < 0.88) return 'Ink becomes land';
    return 'The world in black';
  }

  return {
    scene,
    camera,
    update,
    dispose() {
      scene.remove(drawing, wires);
      for (const item of geometries) item.dispose();
      for (const item of materials) item.dispose();
      stage.dispose();
    },
  };
}
