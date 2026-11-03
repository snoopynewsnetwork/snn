import * as THREE from 'three';
import { createFlatInkTransition } from './transition-flat.js';
import { createGlobe } from './globe.js';
import { geoVector, SPHERE_VIEW } from './globe-projection.js';
import { createOrbitInkAssets } from './orbit-ink-assets.js';
import { getOrbitPose, orbitPhase, smooth, FILM_DURATION, COAST_END, PULL_UP_END } from './orbit-flight.js';
import { applyOrbitSettings, DEFAULT_ORBIT_SETTINGS } from './orbit-editor-state.js';
import { getFilmPhase } from './film-shots.js';

export function createOrbitFilm(renderer) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.35, 1000);
  const globe = createGlobe(renderer);
  // Match the existing globe's composition while giving the flight a simpler
  // coordinate system: front is +Z, screen-left is -X, and north stays up.
  const initialView = new THREE.Matrix4().lookAt(
    geoVector(SPHERE_VIEW.longitude, SPHERE_VIEW.latitude), new THREE.Vector3(), new THREE.Vector3(0, 1, 0),
  );
  globe.root.quaternion.setFromRotationMatrix(initialView).invert();
  scene.add(globe.root);
  const assets = createOrbitInkAssets();
  scene.add(assets.root);
  let openingName = 'nose';
  let opening = createFlatInkTransition(renderer, openingName);
  let activeScene = opening.scene;
  let activeCamera = opening.camera;

  function update(seconds, aspect, { opening: selected = 'nose', weave = 1, ringSpeed = 1,
    orbitSettings = DEFAULT_ORBIT_SETTINGS, holdEnding = false } = {}) {
    const time = THREE.MathUtils.clamp(seconds, 0, FILM_DURATION);
    const viewAspect = Number.isFinite(aspect) && aspect > 0 ? aspect : 1;
    if (selected !== openingName) {
      opening.dispose();
      openingName = selected;
      opening = createFlatInkTransition(renderer, selected);
    }
    if (time < 6) {
      activeScene = opening.scene;
      activeCamera = opening.camera;
      opening.update(time / 6, viewAspect);
      return getFilmPhase(time);
    }

    activeScene = scene;
    activeCamera = camera;
    const t = time - 6;
    const pose = applyOrbitSettings(getOrbitPose(t, weave, viewAspect), t, orbitSettings);
    camera.position.copy(pose.position);
    camera.up.copy(pose.up);
    camera.lookAt(pose.target);
    camera.rotateZ(pose.roll);
    camera.fov = pose.fov;
    camera.aspect = viewAspect;
    camera.updateMatrixWorld(true);
    // The opening's near-orthographic lens starts very far from the scene.
    // Fit clipping planes to the actual world so Earth and the opaque type
    // retain distinct depth values even there. Include the edited orbital radius.
    const worldDepth = -new THREE.Vector3().applyMatrix4(camera.matrixWorldInverse).z;
    const orbitRadius = Math.sqrt(Math.max(0, pose.center.lengthSq() - 18 ** 2));
    const sceneRadius = Math.max(350, orbitRadius + 145);
    camera.near = Math.max(0.35, worldDepth - sceneRadius);
    camera.far = Math.max(camera.near + 1, worldDepth + sceneRadius);
    camera.updateProjectionMatrix();
    assets.letters.position.copy(pose.center);
    assets.letters.visible = pose.lettersVisible;
    // Unwind the type toward the audience as its identity is revealed. The
    // orbit keeps moving right to left, but the word never turns backwards.
    assets.letters.quaternion.copy(pose.letterQuaternion);
    // Apply the rings' local spin before tilting their orbital plane.
    assets.rings.rotation.set(0, 0, 0);
    // The ambient ending freezes the authored composition at 24 seconds,
    // while the rings keep their continuous clock (no reset at the join).
    assets.update(holdEnding ? Math.max(0, seconds - 6) : t, { ringSpeed });
    assets.rings.quaternion.premultiply(pose.frame);
    assets.setRingReveal(smooth(COAST_END, PULL_UP_END + 0.5, pose.routeTime));
    assets.rings.scale.x *= orbitRadius / 205;
    assets.rings.scale.z *= orbitRadius / 205;
    return orbitPhase(t);
  }

  return {
    get scene() { return activeScene; },
    get camera() { return activeCamera; },
    update,
    dispose() { opening.dispose(); globe.dispose(); assets.dispose(); },
  };
}
