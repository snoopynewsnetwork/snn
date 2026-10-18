import * as THREE from 'three';
import { createSnoopy3D } from './snoopy-3d.js';
import { orbitPose, sampleCameraArc, TOTAL_SECONDS } from './camera-arc.js';
import { createFixedOrbitControls, syncManualOrbit } from './fixed-orbit-controls.js';

export function startOrbitView() {
  const container = document.querySelector('#orbit-scene');
  const error = document.querySelector('#orbit-error');
  const pauseButton = document.querySelector('#orbit-pause');
  const replayButton = document.querySelector('#orbit-replay');
  const slider = document.querySelector('#orbit-progress');
  const phaseLabel = document.querySelector('#camera-phase');
  const angleLabel = document.querySelector('#camera-angle');
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  } catch {
    error.hidden = false;
    error.textContent = 'The 3D study needs WebGL. Enable hardware acceleration and reload.';
    pauseButton.disabled = replayButton.disabled = slider.disabled = true;
    return;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.setAttribute('aria-hidden', 'true');
  container.append(renderer.domElement);

  const scene = new THREE.Scene();
  const snoopy = createSnoopy3D();
  scene.add(snoopy.root);
  const camera = new THREE.OrthographicCamera(-215, 215, 215, -215, 0.1, 2000);
  const target = new THREE.Vector3(0, 0, 0);
  const radius = 650;
  camera.position.set(0, 0, radius);
  const controls = createFixedOrbitControls(camera, renderer.domElement, target, radius);
  let elapsed = 0;
  let manual = false;
  let playing = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let previousTime = null;
  let frameId = null;
  let visible = true;

  function render() {
    const state = sampleCameraArc(elapsed);
    if (!manual) {
      const pose = orbitPose(state.angleRadians, target, radius);
      camera.position.set(pose.position.x, pose.position.y, pose.position.z);
      camera.up.set(pose.up.x, pose.up.y, pose.up.z);
      camera.lookAt(target);
    }
    const viewProgress = manual
      ? Math.min(1, camera.position.clone().sub(target).angleTo(new THREE.Vector3(0, 0, 1)) / (Math.PI / 2))
      : state.progress;
    snoopy.setViewProgress(viewProgress);
    renderer.render(scene, camera);
    slider.value = String(elapsed);
    slider.setAttribute('aria-valuetext', `${Math.round(state.progress * 90)} degrees, ${state.phase}`);
    angleLabel.textContent = manual ? 'FREE VIEW' : `${Math.round(state.progress * 90)}°`;
    phaseLabel.textContent = manual ? 'DRAG TO ORBIT' : {
      profile: 'PROFILE · HOLD', orbit: 'PROFILE → OVERHEAD', overhead: 'OVERHEAD · HOLD',
    }[state.phase];
    pauseButton.textContent = playing ? 'Pause' : 'Play';
    container.dataset.phase = manual ? 'manual' : state.phase;
    container.dataset.angle = manual ? '' : String(state.angleRadians);
    container.dataset.radius = String(camera.position.distanceTo(target));
    container.dataset.cameraPosition = camera.position.toArray().join(',');
  }

  function resize() {
    const { width, height } = container.getBoundingClientRect();
    if (!width || !height) return;
    const aspect = width / height;
    const viewHeight = Math.max(430, 320 / aspect);
    camera.left = -viewHeight * aspect / 2;
    camera.right = viewHeight * aspect / 2;
    camera.top = viewHeight / 2;
    camera.bottom = -viewHeight / 2;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
    render();
  }

  function tick(time) {
    frameId = null;
    if (!playing || !visible || document.hidden) { previousTime = null; return; }
    if (previousTime !== null) elapsed += (time - previousTime) / 1000;
    previousTime = time;
    // Repeat the 2-second study. The cut back to profile is deliberate;
    // the only animated move is the requested upward quarter-circle.
    elapsed %= TOTAL_SECONDS;
    render();
    frameId = requestAnimationFrame(tick);
  }
  function schedule() {
    previousTime = null;
    if (playing && visible && !document.hidden && frameId === null) frameId = requestAnimationFrame(tick);
  }
  function pause() {
    if (!playing) { replay(); return; }
    playing = false;
    render();
    schedule();
  }
  function replay() {
    manual = false;
    elapsed = 0;
    playing = true;
    render();
    schedule();
  }
  function scrub() {
    manual = false;
    playing = false;
    elapsed = Number(slider.value);
    previousTime = null;
    render();
  }
  function startManualOrbit() {
    playing = false;
    manual = true;
    previousTime = null;
    // OrbitControls caches its world-up basis at construction. Restore that
    // basis only for manual input; scripted playback owns its rotating up vector.
    syncManualOrbit(controls);
    render();
  }
  function changeManualOrbit() {
    if (manual) render();
  }
  function visibilityChange() { schedule(); }
  controls.addEventListener('start', startManualOrbit);
  controls.addEventListener('change', changeManualOrbit);
  pauseButton.addEventListener('click', pause);
  replayButton.addEventListener('click', replay);
  slider.addEventListener('input', scrub);
  document.addEventListener('visibilitychange', visibilityChange);
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(container);
  const visibilityObserver = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    schedule();
  });
  visibilityObserver.observe(container);
  container.dataset.ready = 'true';
  resize();
  schedule();

  if (import.meta.hot) {
    import.meta.hot.dispose(() => {
      if (frameId !== null) cancelAnimationFrame(frameId);
      resizeObserver.disconnect();
      visibilityObserver.disconnect();
      pauseButton.removeEventListener('click', pause);
      replayButton.removeEventListener('click', replay);
      slider.removeEventListener('input', scrub);
      document.removeEventListener('visibilitychange', visibilityChange);
      controls.removeEventListener('start', startManualOrbit);
      controls.removeEventListener('change', changeManualOrbit);
      controls.dispose();
      snoopy.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    });
  }
}
