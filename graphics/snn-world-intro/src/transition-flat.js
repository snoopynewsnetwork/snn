import * as THREE from 'three';
import { createSnoopy } from './snoopy.js';
import { createGlobe } from './globe.js';
import { geoVector } from './globe-projection.js';

const CUT = 0.46;
const FEATURES = {
  nose: { point: [-108, 49, 0], closeHeight: 8 },
  eye: { point: [3, 96, 0], closeHeight: 5 },
  ear: { point: [85, 48, 0], closeHeight: 20 },
};

function interval(start, end, progress) {
  return THREE.MathUtils.clamp((progress - start) / (end - start), 0, 1);
}

function smooth(start, end, progress) {
  const t = interval(start, end, progress);
  return t * t * (3 - 2 * t);
}

function zoomBetween(start, end, progress) {
  return start * Math.pow(end / start, progress);
}

export function createFlatInkTransition(renderer, feature) {
  const landmark = FEATURES[feature];
  if (!landmark) throw new Error(`Unknown flat ink transition: ${feature}`);

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-215, 215, 215, -215, 0.1, 1800);
  const snoopy = createSnoopy();
  const globe = createGlobe(renderer);
  scene.add(snoopy.root, globe.root);

  const inkPoint = new THREE.Vector3(...landmark.point);
  const landPoint = geoVector(-110, 40, 140);
  const earthDirection = geoVector(-115, 12);
  const profileDirection = new THREE.Vector3(0, 0, 1);
  const target = new THREE.Vector3();

  function frame(direction, height, aspect) {
    camera.position.copy(target).addScaledVector(direction, 650);
    camera.up.set(0, 1, 0);
    camera.lookAt(target);
    camera.left = -height * aspect / 2;
    camera.right = height * aspect / 2;
    camera.top = height / 2;
    camera.bottom = -height / 2;
    camera.updateProjectionMatrix();
  }

  function update(progress, aspect) {
    const p = THREE.MathUtils.clamp(progress, 0, 1);
    const viewAspect = Number.isFinite(aspect) && aspect > 0 ? aspect : 1;
    const longestSide = Math.max(1, viewAspect);
    snoopy.root.visible = p < CUT;
    globe.root.visible = p >= CUT;

    if (p < CUT) {
      // Reuse the untouched, entirely planar reference. Only framing changes:
      // no volumes, head movement, perspective, or orbit on the character.
      target.copy(inkPoint).multiplyScalar(smooth(0.08, 0.30, p));
      const push = interval(0.08, CUT, p);
      const height = zoomBetween(
        Math.max(430, 320 / viewAspect),
        landmark.closeHeight / longestSide,
        push * push,
      );
      frame(profileDirection, height, viewAspect);
    } else {
      // Switch between two genuine areas of solid ink. Keeping the globe
      // unshaded here makes the cut exact, without a fade or black overlay.
      const retreat = interval(CUT, 0.91, p);
      const pull = 1 - (1 - retreat) ** 3;
      target.copy(landPoint).multiplyScalar(1 - smooth(0.51, 0.88, p));
      const height = zoomBetween(20 / longestSide, Math.max(360, 360 / viewAspect), pull);
      frame(earthDirection, height, viewAspect);
    }
    // Bring in depth only after the coastline has established the new image.
    globe.setShadingProgress(smooth(0.56, 0.85, p));

    if (p < 0.08) return 'FLAT PROFILE · HOLD';
    if (p < 0.43) return `INTO THE ${feature.toUpperCase()}`;
    if (p < 0.51) return 'INK → LAND';
    if (p < 0.72) return 'COASTLINES EMERGE';
    if (p < 0.91) return 'PULL BACK TO EARTH';
    return 'EARTH · HOLD';
  }

  return {
    scene,
    camera,
    update,
    dispose() { snoopy.dispose(); globe.dispose(); },
  };
}
