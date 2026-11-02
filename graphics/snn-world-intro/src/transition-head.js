import * as THREE from 'three';
import { feature } from 'topojson-client';
import world from 'world-atlas/land-110m.json';
import { geoVector } from './globe-projection.js';
import { createTransitionStage } from './transition-stage.js';

const RADIUS = 140;
const HEAD_CENTER = new THREE.Vector3(15, 79, 0);
const NOSE_CENTER = new THREE.Vector3(-108, 51, 0);
const FINAL_DIRECTION = geoVector(-115, 12);

function ease(value, start, end) {
  const t = THREE.MathUtils.clamp((value - start) / (end - start), 0, 1);
  return t * t * (3 - 2 * t);
}

/**
 * The same triangulation starts as a nose-sized circle and opens into the
 * Americas. Subdivided faces stay on the sphere throughout the transformation.
 */
function createInkPatch(initialDirection) {
  const land = feature(world, world.objects.land);
  const rings = land.features.flatMap((entry) => entry.geometry.coordinates.map((polygon) => polygon[0]));
  const ring = rings.find((points) => points.length > 500
    && points.every(([longitude]) => longitude > -175 && longitude < -30));
  const coordinates = ring.slice(0, -1);
  const outline = coordinates.map(([longitude, latitude]) => new THREE.Vector2(longitude, latitude));
  const triangles = THREE.ShapeUtils.triangulateShape(outline, []);
  const side = new THREE.Vector3(0, 0, 1);
  const across = new THREE.Vector3().crossVectors(side, initialDirection).normalize();
  const startVertices = [];
  const endVertices = [];
  const vertices = coordinates.map(([longitude, latitude], index) => {
    const angle = index / coordinates.length * Math.PI * 2;
    return {
      longitude, latitude,
      circle: new THREE.Vector2(Math.cos(angle) * 17, Math.sin(angle) * 17),
      direction: geoVector(longitude, latitude),
    };
  });

  function midpoint(a, b) {
    const longitude = (a.longitude + b.longitude) / 2;
    const latitude = (a.latitude + b.latitude) / 2;
    return {
      longitude, latitude,
      circle: a.circle.clone().add(b.circle).multiplyScalar(0.5),
      direction: geoVector(longitude, latitude),
    };
  }

  function emit(a, b, c, depth = 0) {
    const edges = [
      a.direction.distanceToSquared(b.direction),
      b.direction.distanceToSquared(c.direction),
      c.direction.distanceToSquared(a.direction),
    ];
    const longest = Math.max(...edges);
    if (longest > (18 / RADIUS) ** 2 && depth < 9) {
      const index = edges.indexOf(longest);
      const ordered = index === 0 ? [a, b, c] : index === 1 ? [b, c, a] : [c, a, b];
      const middle = midpoint(ordered[0], ordered[1]);
      emit(ordered[0], middle, ordered[2], depth + 1);
      emit(middle, ordered[1], ordered[2], depth + 1);
      return;
    }
    for (const vertex of [a, b, c]) {
      const start = initialDirection.clone().multiplyScalar(RADIUS)
        .addScaledVector(across, vertex.circle.x)
        .addScaledVector(side, vertex.circle.y)
        .normalize();
      startVertices.push(start.x, start.y, start.z);
      endVertices.push(vertex.direction.x, vertex.direction.y, vertex.direction.z);
    }
  }
  for (const triangle of triangles) emit(...triangle.map((index) => vertices[index]));

  const starts = new Float32Array(startVertices);
  const ends = new Float32Array(endVertices);
  const positions = new Float32Array(starts.length);
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const material = new THREE.MeshBasicMaterial({
    color: '#252221', side: THREE.DoubleSide, transparent: true,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.name = 'nose-unfolding-into-americas';
  let previous = -1;

  return {
    mesh,
    update(progress, opacity) {
      mesh.visible = opacity > 0.001;
      material.opacity = opacity;
      if (progress === previous) return;
      previous = progress;
      for (let index = 0; index < positions.length; index += 3) {
        const x = THREE.MathUtils.lerp(starts[index], ends[index], progress);
        const y = THREE.MathUtils.lerp(starts[index + 1], ends[index + 1], progress);
        const z = THREE.MathUtils.lerp(starts[index + 2], ends[index + 2], progress);
        const scale = (RADIUS + 1.5) / Math.hypot(x, y, z);
        positions[index] = x * scale;
        positions[index + 1] = y * scale;
        positions[index + 2] = z * scale;
      }
      geometry.attributes.position.needsUpdate = true;
      geometry.computeBoundingSphere();
    },
    dispose() { geometry.dispose(); material.dispose(); },
  };
}

export function createHeadTransition(renderer) {
  const stage = createTransitionStage(renderer);
  const { scene, camera, snoopy, headPivot, globe } = stage;
  const head = headPivot.getObjectByName('head');
  const geometry = head.geometry;
  const attribute = geometry.attributes.position;
  const originalPositions = attribute.array.slice();
  const spherePositions = new Float32Array(originalPositions.length);
  const point = new THREE.Vector3();
  for (let index = 0; index < attribute.count; index += 1) {
    point.fromArray(originalPositions, index * 3).sub(HEAD_CENTER)
      .normalize().multiplyScalar(RADIUS).add(HEAD_CENTER);
    point.toArray(spherePositions, index * 3);
  }

  const noseDirection = NOSE_CENTER.clone().sub(HEAD_CENTER).normalize();
  const noseShift = HEAD_CENTER.clone().addScaledVector(noseDirection, RADIUS + 1)
    .sub(NOSE_CENTER);
  const initialPatchDirection = noseDirection.clone();
  const patch = createInkPatch(initialPatchDirection);
  scene.add(patch.mesh);

  const noseParts = [];
  const markings = [];
  for (const object of headPivot.children) {
    if (!object.geometry || object === head || object.name === 'head-outline') continue;
    object.geometry.computeBoundingBox();
    const center = object.geometry.boundingBox.getCenter(new THREE.Vector3());
    if (object.name.startsWith('nose') || (!object.name && center.x < -85)) {
      noseParts.push({ object, position: object.position.clone() });
    } else {
      markings.push(object);
    }
  }
  const center = new THREE.Vector3();
  const target = new THREE.Vector3();
  const direction = new THREE.Vector3();
  let previousRound = -1;

  function update(value, aspect = 1) {
    const progress = THREE.MathUtils.clamp(value, 0, 1);
    const safeAspect = Math.max(0.1, aspect);
    const arc = ease(progress, 0.08, 0.34);
    const rounding = ease(progress, 0.34, 0.5);
    const departure = ease(progress, 0.55, 0.91);
    const geography = ease(progress, 0.76, 0.92);
    const handoff = progress >= 0.52;

    // Snoopy faces -X. Move from his side (+Z) to his front (-X), keeping
    // the character upright and still while the camera supplies the turn.
    headPivot.rotation.set(0, 0, 0);
    // Head and outline share this geometry, so change it exactly once.
    if (rounding !== previousRound) {
      previousRound = rounding;
      for (let index = 0; index < originalPositions.length; index += 1) {
        attribute.array[index] = THREE.MathUtils.lerp(originalPositions[index], spherePositions[index], rounding);
      }
      attribute.needsUpdate = true;
      geometry.computeVertexNormals();
      geometry.computeBoundingSphere();
    }
    for (const { object, position } of noseParts) {
      object.position.copy(position).addScaledVector(noseShift, rounding);
      // The white shine slips out of view as the nose flattens onto the surface.
      object.visible = !(object.name === 'nose-highlight' && progress >= 0.46);
    }
    for (const object of markings) object.visible = progress < 0.47;
    snoopy.setViewProgress(arc * 0.7);
    snoopy.root.updateMatrixWorld(true);
    center.copy(HEAD_CENTER);
    head.localToWorld(center);

    const closeTarget = center.clone().addScaledVector(initialPatchDirection, 32);
    target.set(0, 0, 0).lerp(closeTarget, ease(progress, 0.12, 0.46));
    const zoom = ease(progress, 0.15, 0.48);
    const startHeight = Math.max(430, 320 / safeAspect);
    const closeHeight = Math.max(108, 108 / safeAspect);
    let height = THREE.MathUtils.lerp(startHeight, closeHeight, zoom);
    direction.set(-Math.sin(arc * Math.PI / 2), 0, Math.cos(arc * Math.PI / 2));

    if (handoff) {
      globe.root.position.copy(center).multiplyScalar(1 - departure);
      patch.mesh.position.copy(globe.root.position);
      target.copy(globe.root.position).addScaledVector(initialPatchDirection, 32 * (1 - departure));
      direction.set(-1, 0, 0).lerp(FINAL_DIRECTION, departure).normalize();
      height = THREE.MathUtils.lerp(closeHeight, Math.max(360, 360 / safeAspect), departure);
    } else {
      globe.root.position.copy(center);
      patch.mesh.position.copy(center);
    }
    // The actual head is already spherical here. The exchange happens inside
    // its white surface while the silhouette, eyes, and ears are outside frame.
    stage.setSnoopyOpacity(handoff ? 0 : 1);
    stage.setGlobeOpacity(handoff ? 1 : 0);
    globe.setSurfaceProgress(geography);
    patch.update(ease(progress, 0.54, 0.82),
      ease(progress, 0.5, 0.53) * (1 - ease(progress, 0.88, 0.96)));
    stage.setCamera(target.toArray(), direction.toArray(), height, safeAspect);

    if (progress < 0.08) return 'SNOOPY · PROFILE';
    if (progress < 0.34) return 'CAMERA TO THE FRONT';
    if (progress < 0.52) return 'ROUND THE HEAD';
    if (progress < 0.82) return 'INK BECOMES LAND';
    if (progress < 0.94) return 'REVEAL THE WORLD';
    return 'SNOOPY’S WORLD';
  }

  update(0, 1);
  return {
    scene, camera, update,
    dispose() { patch.dispose(); stage.dispose(); },
  };
}
