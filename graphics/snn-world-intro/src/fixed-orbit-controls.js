import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export function createFixedOrbitControls(camera, domElement, target, radius) {
  // OrbitControls caches the orbit axis on construction. Keep that axis fixed
  // even though the scripted camera shot rotates its own up vector.
  camera.up.set(0, 1, 0);
  const controls = new OrbitControls(camera, domElement);
  controls.target.copy(target);
  controls.enableZoom = false;
  controls.enablePan = false;
  controls.enableDamping = false;
  controls.minDistance = radius;
  controls.maxDistance = radius;
  controls.rotateSpeed = 0.7;
  if (domElement) controls.cursorStyle = 'grab';
  controls.update();
  return controls;
}

export function syncManualOrbit(controls) {
  // Read the current scripted position before the first drag. At overhead,
  // OrbitControls makes the polar angle safe by an imperceptible amount.
  controls.object.up.set(0, 1, 0);
  controls.update();
}
