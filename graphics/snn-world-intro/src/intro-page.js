import * as THREE from 'three';
import { createOrbitFilm } from './orbit-film.js';

const container = document.querySelector('#intro-scene');
const playButton = document.querySelector('#intro-play');
const replayButton = document.querySelector('#intro-replay');
const error = document.querySelector('#intro-error');
let renderer;
let film;
let observer;
let elapsed = 0;
let previousTime = null;
let frame = null;
let playing = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let failed = false;
let width = 0;
let height = 0;

function fail(cause) {
  failed = true;
  playing = false;
  if (frame !== null) cancelAnimationFrame(frame);
  frame = null;
  observer?.disconnect();
  console.error('Intro playback failed:', cause);
  error.textContent = 'This film needs WebGL. Reload with hardware acceleration enabled to watch it.';
  error.hidden = false;
  playButton.disabled = replayButton.disabled = true;
  container.dataset.ready = 'false';
}

function render() {
  if (failed || !width || !height) return;
  try {
    film.update(elapsed, width / height, { holdEnding: true });
    renderer.render(film.scene, film.camera);
    container.dataset.time = elapsed.toFixed(3);
    container.dataset.phase = elapsed >= 24 ? 'holding' : 'film';
  } catch (cause) {
    fail(cause);
  }
}

function tick(now) {
  frame = null;
  if (failed || !playing || document.hidden) return;
  if (previousTime !== null) elapsed += (now - previousTime) / 1000;
  previousTime = now;
  render();
  if (!failed) frame = requestAnimationFrame(tick);
}

function syncPlayback() {
  if (frame !== null) cancelAnimationFrame(frame);
  frame = previousTime = null;
  playButton.textContent = playing ? 'Pause' : 'Play';
  container.dataset.playing = String(playing);
  if (playing && !failed && !document.hidden) frame = requestAnimationFrame(tick);
}

try {
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.setAttribute('aria-hidden', 'true');
  container.append(renderer.domElement);
  film = createOrbitFilm(renderer);
  renderer.domElement.addEventListener('webglcontextlost', (event) => {
    event.preventDefault();
    fail(new Error('WebGL context lost'));
  });
  observer = new ResizeObserver(() => {
    if (failed) return;
    const bounds = container.getBoundingClientRect();
    width = bounds.width;
    height = bounds.height;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(width, height, false);
    render();
  });
  observer.observe(container);
  playButton.addEventListener('click', () => {
    playing = !playing;
    syncPlayback();
  });
  replayButton.addEventListener('click', () => {
    elapsed = 0;
    playing = true;
    render();
    syncPlayback();
  });
  document.addEventListener('visibilitychange', syncPlayback);
  playButton.disabled = replayButton.disabled = false;
  container.dataset.ready = 'true';
  syncPlayback();
} catch (cause) {
  fail(cause);
  film?.dispose();
  renderer?.dispose();
}
