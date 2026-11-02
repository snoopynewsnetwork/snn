import * as THREE from 'three';
import { createSnoopy } from './snoopy.js';
import { startOrbitView } from './orbit-view.js';
import { startGlobeStudies } from './globe.js';
import { startTransitionStudies } from './transition-views.js';
import { startOrbitFilmStudies } from './orbit-film-views.js';
import { startOrbitEditor } from './orbit-editor.js';
import './style.css';

const container = document.querySelector('#scene');
const artboard = document.querySelector('#artboard');
const errorMessage = document.querySelector('#error-message');
const exportButton = document.querySelector('#export');

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
  exportButton.disabled = true;
}

function start() {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  } catch {
    showError('This drawing needs WebGL. Try opening it in a browser with hardware acceleration enabled.');
    return;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.append(renderer.domElement);
  renderer.domElement.setAttribute('aria-hidden', 'true');

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-300, 300, 225, -225, 0.1, 100);
  camera.position.z = 10;
  const snoopy = createSnoopy();
  scene.add(snoopy.root);

  function render() {
    renderer.render(scene, camera);
  }
  function resize() {
    const { width, height } = container.getBoundingClientRect();
    if (!width || !height) return;
    const aspect = width / height;
    // Maintain generous breathing room without clipping on narrow screens.
    const viewHeight = Math.max(430, 320 / aspect);
    camera.left = -viewHeight * aspect / 2;
    camera.right = viewHeight * aspect / 2;
    camera.top = viewHeight / 2;
    camera.bottom = -viewHeight / 2;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
    render();
  }
  const observer = new ResizeObserver(resize);
  observer.observe(container);

  function savePng() {
    // Render immediately before reading: no permanent drawing buffer or loop.
    render();
    renderer.domElement.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'snn-snoopy-profile.png';
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }, 'image/png');
  }
  exportButton.addEventListener('click', savePng);
  renderer.domElement.addEventListener('webglcontextlost', (event) => {
    event.preventDefault();
    showError('The drawing was interrupted. Reload the page to restore it.');
  });

  // Expose a small read-only diagnostic rather than an animation loop.
  container.dataset.renderer = 'three.js';
  container.dataset.ready = 'true';
  resize();

  if (import.meta.hot) {
    import.meta.hot.dispose(() => {
      observer.disconnect();
      exportButton.removeEventListener('click', savePng);
      snoopy.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    });
  }
}

for (const button of document.querySelectorAll('button[data-background]')) {
  button.addEventListener('click', () => {
    for (const frame of document.querySelectorAll('.artboard')) {
      frame.dataset.background = button.dataset.background;
    }
    for (const swatch of document.querySelectorAll('button[data-background]')) {
      swatch.setAttribute('aria-pressed', String(swatch === button));
    }
  });
}

const referenceToggle = document.querySelector('#reference-toggle');
const reference = document.querySelector('#reference');
referenceToggle.addEventListener('click', () => {
  const showing = reference.hidden;
  reference.hidden = !showing;
  referenceToggle.setAttribute('aria-pressed', String(showing));
  referenceToggle.textContent = showing ? 'Hide reference' : 'Show reference';
  artboard.classList.toggle('comparing', showing);
});

start();
startOrbitView();
startGlobeStudies();
startTransitionStudies();
startOrbitFilmStudies();
startOrbitEditor();
