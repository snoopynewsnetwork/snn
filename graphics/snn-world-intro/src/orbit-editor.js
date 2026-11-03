import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { createOrbitFilm } from './orbit-film.js';
import { orbitPhase } from './orbit-flight.js';
import {
  getOrbitSettings, setOrbitSettings, resetOrbitSettings,
  subscribeOrbitSettings, exportOrbitSettingsJSON,
} from './orbit-editor-state.js';
import {
  PATH_START, PATH_END, FILM_ASPECT, sampleCameraTrack, sampleOrbitSpeeds, getEditorMotion,
} from './orbit-editor-motion.js';

const PAPER = 0xf8f6f0;
const GOLD = 0xbd9449;
const SLOW = new THREE.Color('#4f9d9b');
const FAST = new THREE.Color('#df806b');
const speedColor = (speed, max) => SLOW.clone().lerp(FAST, Math.min(1, speed / max));

/** The scene editor shares the film's scene, but owns a separate viewing camera. */
export function startOrbitEditor() {
  const section = document.querySelector('#scene-editor');
  if (!section) return;
  const $ = (id) => section.querySelector(`#editor-${id}`);
  const viewport = $('viewport');
  const timeline = $('time');
  const chart = $('speed-chart');
  const events = new AbortController();
  const listen = (element, event, handler) => element.addEventListener(event, handler, { signal: events.signal });
  let settings = getOrbitSettings();
  let time = Number(timeline.value);
  let weave = Number(document.querySelector('#film-weave').value);
  let playing = false;
  let disposed = false;
  let visible = true;
  let previousTime = null;
  let frameId = null;
  let width = 1;
  let height = 1;
  let inset = { x: 0, y: 0, width: 0, height: 0 };
  let renderer;
  let film;

  try {
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.autoClear = false;
    film = createOrbitFilm(renderer);
    film.update(time, FILM_ASPECT);
  } catch (error) {
    console.error('Scene editor could not start:', error);
    $('status').textContent = 'The editor needs WebGL. Reload to try again.';
    section.querySelectorAll('button, input').forEach((control) => { control.disabled = true; });
    renderer?.dispose();
    renderer?.forceContextLoss();
    return;
  }

  viewport.append(renderer.domElement);
  renderer.domElement.setAttribute('aria-hidden', 'true');
  const scene = film.scene;
  const earthMeshes = ['globe-surface', 'globe-ink-outline'].map((name) => scene.getObjectByName(name));
  const earthMaterials = earthMeshes.map((mesh) => mesh.material);
  const ghostMaterials = earthMaterials.map((material) => {
    const ghost = material.clone();
    ghost.onBeforeCompile = material.onBeforeCompile;
    ghost.customProgramCacheKey = material.customProgramCacheKey;
    ghost.transparent = true;
    ghost.opacity = 0.12;
    ghost.depthWrite = false;
    return ghost;
  });
  const overview = new THREE.PerspectiveCamera(48, 1, 0.5, 12000);
  overview.layers.enable(1);
  let controls;

  function updateOverviewClipping() {
    overview.updateMatrixWorld(true);
    const depth = -new THREE.Vector3().applyMatrix4(overview.matrixWorldInverse).z;
    // The flat opening camera can be hundreds of thousands of units away.
    // Fit a depth interval around the world even after manually moving from it.
    overview.near = Math.max(0.35, depth - 1000);
    overview.far = Math.max(12000, depth + 1000);
    overview.updateProjectionMatrix();
    schedule();
  }

  function resetNavigation(target, minDistance = 70, maxDistance = 4000) {
    const mouseMode = controls?.mouseButtons.LEFT ?? THREE.MOUSE.ROTATE;
    const touchMode = controls?.touches.ONE ?? THREE.TOUCH.ROTATE;
    controls?.dispose();
    // OrbitControls caches the camera's up axis at construction. Rebuild when
    // switching between the film's rolled frame and world-up overview presets.
    controls = new OrbitControls(overview, renderer.domElement);
    controls.target.copy(target);
    controls.minDistance = minDistance;
    controls.maxDistance = maxDistance;
    controls.screenSpacePanning = true;
    controls.mouseButtons.LEFT = mouseMode;
    controls.touches.ONE = touchMode;
    controls.listenToKeyEvents(viewport);
    controls.addEventListener('change', updateOverviewClipping);
    controls.update();
    updateOverviewClipping();
  }

  // All diagram marks are on a separate layer, invisible to the live film camera.
  const guides = new THREE.Group();
  guides.name = 'scene-editor-guides';
  scene.add(guides);
  const lineMaterials = [];
  function addGuide(object, parent = guides) {
    object.traverse((child) => child.layers.set(1));
    parent.add(object);
    return object;
  }
  function stroke(positions, color, linewidth = 1.5, options = {}) {
    const geometry = new LineGeometry();
    geometry.setPositions(positions);
    const material = new LineMaterial({ color, linewidth, ...options });
    lineMaterials.push(material);
    return new Line2(geometry, material);
  }

  const orbitGuide = addGuide(new THREE.Group());
  const orbitPoints = [];
  for (let i = 0; i <= 200; i++) {
    const angle = (i / 200) * Math.PI * 2;
    orbitPoints.push(Math.sin(angle), 0, Math.cos(angle));
  }
  addGuide(stroke(orbitPoints, GOLD, 1.8), orbitGuide);
  addGuide(stroke(orbitPoints, GOLD, 1.2, { depthTest: false, transparent: true, opacity: 0.2 }), orbitGuide);
  const orbitCenter = addGuide(new THREE.LineSegments(
    new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-7, 0, 0), new THREE.Vector3(7, 0, 0),
      new THREE.Vector3(0, 0, -7), new THREE.Vector3(0, 0, 7),
    ]), new THREE.LineBasicMaterial({ color: GOLD }),
  ));
  const normal = addGuide(new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(), 65, GOLD, 8, 4));

  const pathGuide = addGuide(new THREE.Group());
  const path = addGuide(stroke([0, 0, 0, 0, 0, 1], 0xffffff, 2.8, { vertexColors: true }), pathGuide);
  const pathBehind = addGuide(stroke([0, 0, 0, 0, 0, 1], 0xffffff, 1.4,
    { vertexColors: true, transparent: true, opacity: 0.16, depthTest: false }), pathGuide);
  const dotGeometry = new THREE.SphereGeometry(2.7, 8, 6);
  const dotMaterial = new THREE.MeshBasicMaterial({ color: 0x65746f });
  const dots = addGuide(new THREE.InstancedMesh(dotGeometry, dotMaterial, 34), pathGuide);
  const cameraRig = addGuide(new THREE.Group());
  const bodyGeometry = new THREE.BoxGeometry(9, 6, 7);
  const bodyEdges = new THREE.EdgesGeometry(bodyGeometry);
  bodyGeometry.dispose();
  addGuide(new THREE.LineSegments(bodyEdges, new THREE.LineBasicMaterial({ color: 0x385e5c })), cameraRig);
  const cone = addGuide(new THREE.LineSegments(new THREE.BufferGeometry(),
    new THREE.LineBasicMaterial({ color: 0x4f9d9b, transparent: true, opacity: 0.75 })), cameraRig);
  const cameraDot = addGuide(new THREE.Mesh(new THREE.SphereGeometry(4, 12, 8),
    new THREE.MeshBasicMaterial({ color: 0x4f9d9b })));
  const orbitDot = addGuide(new THREE.Mesh(new THREE.SphereGeometry(4, 12, 8),
    new THREE.MeshBasicMaterial({ color: GOLD })));

  const viewNote = document.createElement('span');
  viewNote.className = 'editor-view-note';
  viewport.append(viewNote);
  let track;
  let orbitSpeeds;
  let speedMaximum;

  function rebuildTrack() {
    track = sampleCameraTrack(weave);
    speedMaximum = Math.max(...track.map((sample) => sample.speed));
    const positions = track.flatMap((sample) => sample.position.toArray());
    const colors = track.flatMap((sample) => speedColor(sample.speed, speedMaximum).toArray());
    for (const line of [path, pathBehind]) {
      line.geometry.setPositions(positions);
      line.geometry.setColors(colors);
    }
    let count = 0;
    for (let stamp = 7.5; stamp <= PATH_END; stamp += 0.5) {
      const { pose } = getEditorMotion(stamp, weave, settings);
      dots.setMatrixAt(count++, new THREE.Matrix4().makeTranslation(...pose.position.toArray()));
    }
    dots.count = count;
    dots.instanceMatrix.needsUpdate = true;
    dots.computeBoundingSphere();
    orbitSpeeds = sampleOrbitSpeeds(track, weave, settings);
  }

  function setView(view = 'overview') {
    const target = new THREE.Vector3(-40, 40, 185);
    const positions = {
      overview: new THREE.Vector3(760, 520, 1000),
      front: new THREE.Vector3(0, 35, 1200),
      top: new THREE.Vector3(0, 1150, 150.01),
      side: new THREE.Vector3(1100, 35, 150),
    };
    overview.position.copy(positions[view]);
    overview.up.set(0, 1, 0);
    overview.fov = 48;
    overview.zoom = 1;
    overview.lookAt(target);
    resetNavigation(target);
  }

  function matchFilmCamera() {
    setPlaying(false);
    // Refresh synchronously so a recent scrub cannot copy the previous frame.
    film.update(time, FILM_ASPECT, { weave,
      ringSpeed: Number(document.querySelector('#film-ring-speed').value), orbitSettings: settings });
    const { pose } = getEditorMotion(time, weave, settings);
    overview.position.copy(film.camera.position);
    overview.quaternion.copy(film.camera.quaternion);
    overview.up.set(0, 1, 0).applyQuaternion(film.camera.quaternion);
    overview.fov = film.camera.fov;
    overview.zoom = film.camera.zoom;
    // Keep the editor's aspect ratio and guide layer, but match position,
    // viewing direction, roll, and lens. Close shots need a nearby orbit target.
    resetNavigation(pose.target, 0.1, Math.max(4000, overview.position.distanceTo(pose.target) * 2));
    $('status').textContent = `Viewer matched to film camera at ${time.toFixed(2)}s. Drag to explore.`;
  }

  function setPlaying(value) {
    playing = value;
    previousTime = null;
    $('play').textContent = value ? 'Pause' : 'Play';
    schedule();
  }
  function seek(value) {
    time = THREE.MathUtils.clamp(value, 6, PATH_END);
    timeline.value = time.toFixed(2);
    setPlaying(false);
  }

  function schedule() {
    if (!disposed && frameId === null) frameId = requestAnimationFrame(render);
  }

  function formatSpeed(value) {
    return value >= 10000 ? new Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(value) : value.toFixed(1);
  }

  function drawChart() {
    const w = chart.clientWidth;
    if (!w) return;
    const h = 110;
    const dpr = renderer.getPixelRatio();
    if (chart.width !== Math.round(w * dpr)) chart.width = Math.round(w * dpr);
    if (chart.height !== Math.round(h * dpr)) chart.height = Math.round(h * dpr);
    const ctx = chart.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const max = Math.ceil(Math.max(speedMaximum, ...orbitSpeeds) / 50) * 50;
    const x = (stamp) => 34 + (stamp - PATH_START) / (PATH_END - PATH_START) * (w - 44);
    const y = (value) => 90 - value / max * 66;
    ctx.font = '8px monospace';
    ctx.fillStyle = '#8b8171';
    for (const value of [0, max / 2, max]) {
      ctx.strokeStyle = '#ded8cc';
      ctx.lineWidth = 0.7;
      ctx.beginPath(); ctx.moveTo(32, y(value)); ctx.lineTo(w - 8, y(value)); ctx.stroke();
      ctx.fillText(String(value), 0, y(value) + 3);
    }
    for (const stamp of [8, 12, 16, 20, 24]) ctx.fillText(`${stamp}s`, x(stamp) - 6, 106);
    for (let i = 1; i < track.length; i++) {
      ctx.strokeStyle = `#${speedColor(track[i].speed, speedMaximum).getHexString()}`;
      ctx.lineWidth = 1.7;
      ctx.beginPath(); ctx.moveTo(x(track[i - 1].time), y(track[i - 1].speed));
      ctx.lineTo(x(track[i].time), y(track[i].speed)); ctx.stroke();
    }
    ctx.strokeStyle = '#bd9449'; ctx.lineWidth = 1.5; ctx.beginPath();
    track.forEach((sample, i) => ctx[i ? 'lineTo' : 'moveTo'](x(sample.time), y(orbitSpeeds[i])));
    ctx.stroke();
    ctx.fillStyle = '#4f8b89'; ctx.fillText('CAMERA', 34, 10);
    ctx.fillStyle = '#a27d37'; ctx.fillText('SNN', 94, 10);
    if (time >= PATH_START) {
      ctx.strokeStyle = '#514b40'; ctx.lineWidth = 1; ctx.setLineDash([2, 3]);
      ctx.beginPath(); ctx.moveTo(x(time), 17); ctx.lineTo(x(time), 93); ctx.stroke(); ctx.setLineDash([]);
    }
  }

  function render(now) {
    frameId = null;
    if (disposed) return;
    if (playing && visible && !document.hidden && previousTime !== null) {
      time = Math.min(PATH_END, time + Math.min((now - previousTime) / 1000, 0.1));
      timeline.value = time.toFixed(2);
      if (time === PATH_END) { playing = false; $('play').textContent = 'Play'; }
    }
    previousTime = playing && visible && !document.hidden ? now : null;
    const w = Math.round(viewport.clientWidth);
    const h = Math.round(viewport.clientHeight);
    if (!w || !h) return;
    if (w !== width || h !== height) {
      width = w; height = h;
      renderer.setSize(width, height, false);
      overview.aspect = width / height;
      overview.updateProjectionMatrix();
      lineMaterials.forEach((material) => material.resolution.set(width, height));
    }
    film.update(time, FILM_ASPECT, { weave,
      ringSpeed: Number(document.querySelector('#film-ring-speed').value), orbitSettings: settings });
    const { pose, cameraSpeed, orbitSpeed } = getEditorMotion(time, weave, settings);
    orbitGuide.quaternion.copy(pose.frame);
    orbitGuide.position.set(0, 18, 0).applyQuaternion(pose.frame);
    orbitGuide.scale.setScalar(settings.radius);
    orbitGuide.visible = orbitCenter.visible = normal.visible = orbitDot.visible = $('show-orbit').checked;
    orbitCenter.position.copy(orbitGuide.position);
    orbitCenter.quaternion.copy(pose.frame);
    normal.position.copy(orbitGuide.position);
    normal.setDirection(new THREE.Vector3(0, 1, 0).applyQuaternion(pose.frame));
    orbitDot.position.copy(pose.center);
    pathGuide.visible = $('show-path').checked;
    const atFilmCamera = overview.position.distanceToSquared(pose.position) < 0.000001;
    cameraRig.visible = $('show-frustum').checked && time >= PATH_START && !atFilmCamera;
    cameraDot.visible = time >= PATH_START && !atFilmCamera;
    cameraRig.position.copy(film.camera.position);
    cameraRig.quaternion.copy(film.camera.quaternion);
    cameraDot.position.copy(pose.position);
    const depth = 48;
    const halfH = Math.tan(THREE.MathUtils.degToRad(pose.fov) / 2) * depth;
    const halfW = halfH * FILM_ASPECT;
    const corners = [[-halfW, -halfH, -depth], [halfW, -halfH, -depth],
      [halfW, halfH, -depth], [-halfW, halfH, -depth]].map((v) => new THREE.Vector3(...v));
    cone.geometry.setFromPoints(corners.flatMap((corner, i) => [new THREE.Vector3(), corner, corner, corners[(i + 1) % 4]]));
    viewNote.textContent = atFilmCamera ? `AT FILM CAMERA · ${time.toFixed(2)}s · DRAG TO EXPLORE`
      : time < PATH_START ? 'OPENING LENS BLEND · CAMERA OUTSIDE OVERVIEW' : 'CLICK THE CAMERA PATH TO SCRUB';
    $('time-label').textContent = `${time.toFixed(2)}s`;
    $('shot-label').textContent = orbitPhase(time - 6);
    $('camera-speed').textContent = formatSpeed(cameraSpeed);
    $('orbit-speed').textContent = formatSpeed(orbitSpeed);
    $('distance').textContent = pose.position.length().toFixed(1);

    // Ghosting affects only the overview pass.
    if ($('ghost-earth').checked) earthMeshes.forEach((mesh, i) => { mesh.material = ghostMaterials[i]; });
    renderer.setScissorTest(false);
    renderer.setViewport(0, 0, width, height);
    renderer.setClearColor(PAPER, 1);
    renderer.clear();
    renderer.render(scene, overview);
    earthMeshes.forEach((mesh, i) => { mesh.material = earthMaterials[i]; });

    const insetWidth = Math.min(240, Math.floor(width * 0.45));
    const insetHeight = Math.round(insetWidth / FILM_ASPECT);
    inset = { x: width - insetWidth - 16, y: 16, width: insetWidth, height: insetHeight };
    renderer.setScissorTest(true);
    renderer.setScissor(inset.x - 1, inset.y - 1, insetWidth + 2, insetHeight + 2);
    renderer.setClearColor(0xd5cbbb, 1); renderer.clear();
    renderer.setScissor(inset.x, inset.y, insetWidth, insetHeight);
    renderer.setViewport(inset.x, inset.y, insetWidth, insetHeight);
    renderer.setClearColor(PAPER, 1); renderer.clear();
    renderer.render(scene, film.camera);
    renderer.setScissorTest(false);
    renderer.setViewport(0, 0, width, height);
    drawChart();
    if (playing && visible && !document.hidden) schedule();
  }

  function syncSettings(next) {
    settings = next;
    for (const input of section.querySelectorAll('[data-orbit-setting]')) {
      const key = input.dataset.orbitSetting;
      input.value = next[key];
      section.querySelector(`[data-orbit-value="${key}"]`).textContent = key === 'radius' ? `${next[key]} u`
        : key === 'speed' ? `${Number(next[key].toFixed(2))}×` : `${next[key]}°`;
    }
    if (track) orbitSpeeds = sampleOrbitSpeeds(track, weave, settings);
    schedule();
  }
  const unsubscribe = subscribeOrbitSettings((next) => { syncSettings(next); $('status').textContent = 'Orbit updated in all film previews.'; });
  for (const input of section.querySelectorAll('[data-orbit-setting]')) {
    listen(input, 'input', () => setOrbitSettings({ [input.dataset.orbitSetting]: Number(input.value) }));
  }
  listen($('reset-orbit'), 'click', () => {
    syncSettings(resetOrbitSettings());
    $('status').textContent = 'Original orbit restored.';
  });
  listen($('export'), 'click', () => {
    const url = URL.createObjectURL(new Blob([exportOrbitSettingsJSON()], { type: 'application/json' }));
    const link = document.createElement('a');
    link.href = url; link.download = 'snn-orbit-settings.json'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    $('status').textContent = 'Orbit settings exported as JSON.';
  });
  for (const name of ['show-path', 'show-orbit', 'show-frustum', 'ghost-earth']) listen($(name), 'change', schedule);
  for (const view of ['front', 'top', 'side']) listen($(`view-${view}`), 'click', () => setView(view));
  listen($('reset-view'), 'click', () => setView());
  listen($('match-camera'), 'click', matchFilmCamera);
  for (const mode of ['orbit', 'pan']) listen($(`mode-${mode}`), 'click', () => {
    controls.mouseButtons.LEFT = mode === 'orbit' ? THREE.MOUSE.ROTATE : THREE.MOUSE.PAN;
    controls.touches.ONE = mode === 'orbit' ? THREE.TOUCH.ROTATE : THREE.TOUCH.PAN;
    for (const candidate of ['orbit', 'pan']) $(`mode-${candidate}`).setAttribute('aria-pressed', String(mode === candidate));
    renderer.domElement.style.cursor = mode === 'pan' ? 'grab' : 'default';
  });
  for (const [name, factor] of [['zoom-in', 0.8], ['zoom-out', 1.25]]) listen($(name), 'click', () => {
    const offset = overview.position.clone().sub(controls.target);
    offset.setLength(THREE.MathUtils.clamp(offset.length() * factor, controls.minDistance, controls.maxDistance));
    overview.position.copy(controls.target).add(offset); controls.update();
  });
  listen($('play'), 'click', () => { if (time >= PATH_END) time = 6; setPlaying(!playing); });
  listen(timeline, 'input', () => seek(Number(timeline.value)));
  listen(chart, 'pointerdown', (event) => {
    const rect = chart.getBoundingClientRect();
    seek(PATH_START + THREE.MathUtils.clamp((event.clientX - rect.left - 34) / (rect.width - 44), 0, 1) * (PATH_END - PATH_START));
  });
  listen(document.querySelector('#film-weave'), 'input', () => {
    weave = Number(document.querySelector('#film-weave').value); rebuildTrack(); schedule();
  });
  listen(document.querySelector('#film-reset-tuning'), 'click', () => {
    weave = Number(document.querySelector('#film-weave').value); rebuildTrack(); schedule();
  });
  listen(document.querySelector('#film-ring-speed'), 'input', schedule);
  listen(document, 'visibilitychange', () => { previousTime = null; schedule(); });

  let pointerStart;
  listen(renderer.domElement, 'pointerdown', (event) => {
    viewport.focus({ preventScroll: true });
    pointerStart = { x: event.clientX, y: event.clientY, id: event.pointerId, button: event.button };
  });
  listen(renderer.domElement, 'pointerup', (event) => {
    if (!pointerStart || pointerStart.button !== 0 || pointerStart.id !== event.pointerId
      || Math.hypot(event.clientX - pointerStart.x, event.clientY - pointerStart.y) > 4 || !$('show-path').checked) return;
    const rect = viewport.getBoundingClientRect();
    const pointer = new THREE.Vector2(event.clientX - rect.left, event.clientY - rect.top);
    if (pointer.x >= inset.x && pointer.y >= height - inset.y - inset.height) return;
    overview.updateMatrixWorld();
    const projected = track.map((sample) => sample.position.clone().project(overview));
    let best = 8;
    let picked;
    for (let i = 1; i < projected.length; i++) {
      const a = projected[i - 1]; const b = projected[i];
      if (a.z < -1 || a.z > 1 || b.z < -1 || b.z > 1) continue;
      const from = new THREE.Vector2((a.x + 1) * width / 2, (1 - a.y) * height / 2);
      const to = new THREE.Vector2((b.x + 1) * width / 2, (1 - b.y) * height / 2);
      const delta = to.clone().sub(from);
      const fraction = THREE.MathUtils.clamp(pointer.clone().sub(from).dot(delta) / Math.max(delta.lengthSq(), 0.001), 0, 1);
      const distance = pointer.distanceTo(from.addScaledVector(delta, fraction));
      if (distance < best) { best = distance; picked = THREE.MathUtils.lerp(track[i - 1].time, track[i].time, fraction); }
    }
    if (picked !== undefined) seek(picked);
  });

  const resize = new ResizeObserver(schedule);
  resize.observe(viewport);
  const intersection = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting; previousTime = null; if (visible) schedule();
  });
  intersection.observe(section);
  rebuildTrack();
  syncSettings(settings);
  setView();

  function dispose() {
    disposed = true;
    if (frameId !== null) cancelAnimationFrame(frameId);
    events.abort(); unsubscribe(); resize.disconnect(); intersection.disconnect(); controls.dispose();
    guides.traverse((object) => { object.geometry?.dispose(); object.material?.dispose(); });
    guides.removeFromParent(); viewNote.remove();
    ghostMaterials.forEach((material) => material.dispose());
    film.dispose(); renderer.dispose(); renderer.forceContextLoss(); renderer.domElement.remove();
  }
  import.meta.hot?.dispose(dispose);
  return { dispose };
}
