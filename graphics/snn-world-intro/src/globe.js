import * as THREE from 'three';
import { geoEquirectangular, geoPath } from 'd3-geo';
import { feature } from 'topojson-client';
import world from 'world-atlas/land-110m.json';
import { coastlineGeometry, createFlatProjection, geoVector, SPHERE_VIEW } from './globe-projection.js';
import { createFixedOrbitControls } from './fixed-orbit-controls.js';

const INK = '#252221';
const OCEAN = '#ffffff';
const LAND = '#f7f5ee';
const RADIUS = 140;
const land = feature(world, world.objects.land);
const coastlines = coastlineGeometry(land);
// Omit the five Hawaiian island polygons only from the flat reference study.
const flatLand = {
  ...land,
  features: land.features.map((entry) => ({
    ...entry,
    geometry: {
      ...entry.geometry,
      coordinates: entry.geometry.coordinates.filter((polygon) => !polygon[0].every(
        ([longitude, latitude]) => longitude >= -161 && longitude <= -154
          && latitude >= 18 && latitude <= 23,
      )),
    },
  })),
};
const flatCoastlines = coastlineGeometry(flatLand);

function startFlatGlobe(prefix, landColor) {
  const container = document.querySelector(`#${prefix}-flat-scene`);
  const canvas = document.createElement('canvas');
  canvas.setAttribute('aria-hidden', 'true');
  container.append(canvas);
  const context = canvas.getContext('2d');
  const dpr = Math.min(window.devicePixelRatio || 1, 2);

  function render() {
    const { width, height } = container.getBoundingClientRect();
    if (!width || !height) return;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    const scale = Math.min(width, height) / 360;
    const radius = RADIUS * scale;
    const projection = createFlatProjection(radius, [width / 2, height / 2]);
    const path = geoPath(projection, context);
    context.lineJoin = 'round';
    context.lineCap = 'round';

    context.beginPath();
    path({ type: 'Sphere' });
    context.fillStyle = OCEAN;
    context.fill();

    // D3 clips spherical polygons at the horizon. There is no far-side ink
    // projected into the visible disc, including at the antimeridian.
    context.save();
    context.clip();
    context.beginPath();
    path(flatLand);
    context.fillStyle = landColor;
    context.fill();
    context.beginPath();
    path(flatCoastlines);
    context.strokeStyle = INK;
    context.lineWidth = 2.4 * scale;
    context.stroke();
    context.restore();

    context.beginPath();
    context.arc(width / 2, height / 2, radius, 0, Math.PI * 2);
    context.strokeStyle = INK;
    context.lineWidth = 4.4 * scale;
    context.stroke();
  }
  const observer = new ResizeObserver(render);
  observer.observe(container);
  render();
  container.dataset.ready = 'true';
  return () => { observer.disconnect(); canvas.remove(); };
}

function createEarthTexture(renderer, landColor) {
  const canvas = document.createElement('canvas');
  canvas.width = 4096;
  canvas.height = 2048;
  const context = canvas.getContext('2d');
  const projection = geoEquirectangular()
    .scale(canvas.width / (2 * Math.PI))
    .translate([canvas.width / 2, canvas.height / 2])
    .precision(0.1);
  const path = geoPath(projection, context);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  texture.wrapS = THREE.RepeatWrapping;

  function draw(showGrid) {
    context.fillStyle = OCEAN;
    context.fillRect(0, 0, canvas.width, canvas.height);

    // Paint the grid onto the ocean before the land. This keeps it flush with
    // the sphere and hidden beneath continents at every camera angle.
    if (showGrid) {
      context.beginPath();
      for (let latitude = -75; latitude <= 75; latitude += 15) {
        const y = (90 - latitude) / 180 * canvas.height;
        context.moveTo(0, y);
        context.lineTo(canvas.width, y);
      }
      // Include both texture edges so the antimeridian wraps seamlessly.
      for (let longitude = -180; longitude <= 180; longitude += 22.5) {
        const x = (longitude + 180) / 360 * canvas.width;
        context.moveTo(x, 0);
        context.lineTo(x, canvas.height);
      }
      context.strokeStyle = '#d1cdc3';
      context.lineWidth = 0.72 * canvas.width / (2 * Math.PI * RADIUS);
      context.lineCap = 'butt';
      context.stroke();
    }

    context.beginPath();
    path(land);
    context.fillStyle = landColor;
    context.fill();
    // Stroke geographic rings separately: polygon clipping closes fills at
    // ±180°, and stroking those synthetic edges would draw a false coastline.
    context.beginPath();
    path(coastlines);
    context.strokeStyle = INK;
    context.lineWidth = 2.4 * canvas.width / (2 * Math.PI * RADIUS);
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.stroke();
    texture.needsUpdate = true;
  }

  draw(true);
  return { texture, setGridVisible: draw };
}

export function createGlobe(renderer, landColor = INK) {
  const root = new THREE.Group();
  root.name = 'earth';
  const { texture, setGridVisible } = createEarthTexture(renderer, landColor);
  const material = new THREE.MeshBasicMaterial({ map: texture });
  const surfaceProgress = { value: 1 };
  const shadingProgress = { value: 1 };
  material.onBeforeCompile = (shader) => {
    shader.uniforms.surfaceProgress = surfaceProgress;
    shader.uniforms.shadingProgress = shadingProgress;
    shader.vertexShader = `varying vec3 globeNormal;\n${shader.vertexShader}`
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nglobeNormal = normalize(normalMatrix * normal);');
    shader.fragmentShader = `uniform float surfaceProgress;\nuniform float shadingProgress;\nvarying vec3 globeNormal;\n${shader.fragmentShader}`
      .replace('#include <opaque_fragment>', `
        float light = max(dot(normalize(globeNormal), normalize(vec3(-0.45, 0.6, 1.0))), 0.0);
        outgoingLight = mix(vec3(1.0), outgoingLight, surfaceProgress);
        outgoingLight *= mix(1.0, 0.84 + 0.16 * light, shadingProgress);
        #include <opaque_fragment>
      `);
  };
  const sphere = new THREE.Mesh(new THREE.SphereGeometry(RADIUS, 128, 96), material);
  sphere.name = 'globe-surface';
  root.add(sphere);

  const outline = new THREE.Mesh(
    new THREE.SphereGeometry(RADIUS + 4.2, 128, 96),
    new THREE.MeshBasicMaterial({ color: INK, side: THREE.BackSide }),
  );
  outline.name = 'globe-ink-outline';
  root.add(outline);

  return {
    root,
    setGridVisible,
    setSurfaceProgress(value) { surfaceProgress.value = THREE.MathUtils.clamp(value, 0, 1); },
    setShadingProgress(value) { shadingProgress.value = THREE.MathUtils.clamp(value, 0, 1); },
    dispose() {
      root.traverse((object) => object.geometry?.dispose());
      material.dispose();
      outline.material.dispose();
      texture.dispose();
    },
  };
}

function startSpatialGlobe(prefix, landColor) {
  const container = document.querySelector(`#${prefix}-spatial-scene`);
  const error = document.querySelector(`#${prefix}-error`);
  const resetButton = document.querySelector(`#${prefix}-reset`);
  const gridButton = document.querySelector(`#${prefix}-grid-toggle`);
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  } catch {
    error.hidden = false;
    error.textContent = 'This globe needs WebGL. Enable hardware acceleration and reload.';
    resetButton.disabled = gridButton.disabled = true;
    return () => {};
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.setAttribute('aria-hidden', 'true');
  container.append(renderer.domElement);

  const scene = new THREE.Scene();
  const globe = createGlobe(renderer, landColor);
  scene.add(globe.root);
  const camera = new THREE.OrthographicCamera(-180, 180, 180, -180, 0.1, 1800);
  const target = new THREE.Vector3();
  const distance = 650;
  const initialPosition = geoVector(SPHERE_VIEW.longitude, SPHERE_VIEW.latitude, distance);
  camera.position.copy(initialPosition);
  camera.lookAt(target);
  const controls = createFixedOrbitControls(camera, renderer.domElement, target, distance);
  let gridVisible = true;

  function render() { renderer.render(scene, camera); }
  function resize() {
    const { width, height } = container.getBoundingClientRect();
    if (!width || !height) return;
    const aspect = width / height;
    const viewHeight = Math.max(360, 360 / aspect);
    camera.left = -viewHeight * aspect / 2;
    camera.right = viewHeight * aspect / 2;
    camera.top = viewHeight / 2;
    camera.bottom = -viewHeight / 2;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
    render();
  }
  function reset() {
    camera.position.copy(initialPosition);
    controls.update();
    render();
  }
  function toggleGrid() {
    gridVisible = !gridVisible;
    globe.setGridVisible(gridVisible);
    gridButton.setAttribute('aria-pressed', String(gridVisible));
    render();
  }
  controls.addEventListener('change', render);
  resetButton.addEventListener('click', reset);
  gridButton.addEventListener('click', toggleGrid);
  const observer = new ResizeObserver(resize);
  observer.observe(container);
  container.dataset.ready = 'true';
  container.dataset.longitude = String(SPHERE_VIEW.longitude);
  container.dataset.latitude = String(SPHERE_VIEW.latitude);
  resize();

  return () => {
    observer.disconnect();
    controls.removeEventListener('change', render);
    controls.dispose();
    resetButton.removeEventListener('click', reset);
    gridButton.removeEventListener('click', toggleGrid);
    globe.dispose();
    renderer.dispose();
    renderer.domElement.remove();
  };
}

export function startGlobeStudies() {
  const disposeViews = [
    { prefix: 'globe', landColor: LAND },
    { prefix: 'globe-black', landColor: INK },
  ].flatMap(({ prefix, landColor }) => [
    startFlatGlobe(prefix, landColor),
    startSpatialGlobe(prefix, landColor),
  ]);
  if (import.meta.hot) {
    import.meta.hot.dispose(() => disposeViews.forEach((dispose) => dispose()));
  }
}
