import * as THREE from 'three';
import { geoVector } from './globe-projection.js';
import { createTransitionStage } from './transition-stage.js';

const INK = '#252221';
const CUT = 0.46;

function easeBetween(start, end, progress) {
  const t = THREE.MathUtils.clamp((progress - start) / (end - start), 0, 1);
  return t * t * (3 - 2 * t);
}

function scaleBetween(start, end, progress) {
  return start * Math.pow(end / start, progress);
}

export function createNoseTransition(renderer) {
  const stage = createTransitionStage(renderer);
  const { scene, camera, snoopy, headPivot, globe } = stage;

  // This point is inside the actual black nose, clear of its white highlight.
  // Drawing coordinates map to world coordinates about (147, 170).
  const nosePoint = new THREE.Vector3(-107, 51, snoopy.parts.nose.front(40, 119));
  const landDirection = geoVector(-100, 40);
  const landPoint = landDirection.clone().multiplyScalar(140);
  const finalDirection = geoVector(-115, 12);
  const target = new THREE.Vector3();
  const direction = new THREE.Vector3();

  // Both sides of the match are real black geometry. This tiny overlap hides
  // their different lighting without exposing the concealed scene change.
  const matchMaterial = new THREE.MeshBasicMaterial({
    color: INK,
    transparent: true,
    opacity: 0,
    depthTest: false,
    depthWrite: false,
    toneMapped: false,
  });
  const matchGeometry = new THREE.PlaneGeometry(1, 1);
  const matchCover = new THREE.Mesh(matchGeometry, matchMaterial);
  matchCover.name = 'nose-to-continent-match';
  matchCover.position.z = -1;
  matchCover.renderOrder = 1000;
  matchCover.frustumCulled = false;
  camera.add(matchCover);
  scene.add(camera);

  function update(progress, aspect) {
    const p = THREE.MathUtils.clamp(progress, 0, 1);
    const viewAspect = Number.isFinite(aspect) && aspect > 0 ? aspect : 1;
    const profileHeight = Math.max(430, 320 / viewAspect);
    const globeHeight = Math.max(360, 360 / viewAspect);
    // Even the longer viewport dimension lies well inside the nose/continent.
    const closeHeight = 2.6 / Math.max(1, viewAspect);
    let viewHeight;

    headPivot.rotation.set(0, 0, 0);
    snoopy.setViewProgress(0);
    globe.setSurfaceProgress(1);
    stage.setSnoopyOpacity(p < CUT ? 1 : 0);
    stage.setGlobeOpacity(p < CUT ? 0 : 1);

    if (p < CUT) {
      // Center the nose while Snoopy is still recognizable, then accelerate
      // the magnification until its black surface fills the entire viewport.
      const push = easeBetween(0.08, 0.455, p);
      const aim = easeBetween(0, 0.45, push);
      target.copy(nosePoint).multiplyScalar(aim);
      const detailHeight = 100 / Math.max(1, viewAspect);
      const noseHeight = 20 / Math.max(1, viewAspect);
      if (p < 0.30) {
        viewHeight = scaleBetween(profileHeight, detailHeight, easeBetween(0.08, 0.30, p));
      } else if (p < 0.415) {
        viewHeight = scaleBetween(detailHeight, noseHeight, easeBetween(0.30, 0.415, p));
      } else {
        // Cross the featureless part quickly, retaining the nose's silhouette
        // and highlight until just before the actual match cut.
        viewHeight = scaleBetween(noseHeight, closeHeight, easeBetween(0.415, 0.455, p));
      }
      stage.setCamera(target.toArray(), [0, 0, 1], viewHeight, viewAspect);
    } else {
      const pull = easeBetween(0.48, 0.92, p);
      // Start on inland North America. Coastlines appear before the camera
      // recenters on the sphere and reaches the final broadcast globe view.
      const recenter = easeBetween(0.08, 0.96, pull);
      const turn = easeBetween(0.32, 1, pull);
      target.copy(landPoint).multiplyScalar(1 - recenter);
      direction.copy(landDirection).lerp(finalDirection, turn).normalize();
      const coastlineHeight = 100;
      viewHeight = p < 0.56
        ? scaleBetween(closeHeight, coastlineHeight, easeBetween(0.48, 0.56, p))
        : scaleBetween(coastlineHeight, globeHeight, easeBetween(0.56, 0.92, p));
      stage.setCamera(target.toArray(), direction.toArray(), viewHeight, viewAspect);
    }

    const cover = easeBetween(0.445, 0.458, p) * (1 - easeBetween(0.478, 0.495, p));
    matchMaterial.opacity = cover;
    matchCover.visible = cover > 0;
    matchCover.scale.set(viewHeight * viewAspect * 1.01, viewHeight * 1.01, 1);

    if (p < 0.08) return 'PROFILE · HOLD';
    if (p < 0.445) return 'INTO THE NOSE';
    if (p < 0.53) return 'NOSE → CONTINENT';
    if (p < 0.75) return 'COASTLINES EMERGE';
    if (p < 0.92) return 'PULL BACK TO EARTH';
    return 'EARTH · HOLD';
  }

  return {
    scene,
    camera,
    update,
    dispose() {
      matchCover.removeFromParent();
      matchGeometry.dispose();
      matchMaterial.dispose();
      stage.dispose();
    },
  };
}
