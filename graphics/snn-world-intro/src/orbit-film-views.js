import * as THREE from 'three';
import { createOrbitFilm } from './orbit-film.js';
import { FILM_SHOTS } from './film-shots.js';
import { getOrbitSettings, subscribeOrbitSettings } from './orbit-editor-state.js';
import { startFilmExport } from './film-export.js';

export function startOrbitFilmStudies() {
  const section = document.querySelector('#orbit-film-studies');
  if (!section) return;

  const storyboard = section.querySelector('#film-storyboards');
  const shotTemplate = section.querySelector('#film-shot-template');
  storyboard.replaceChildren(...FILM_SHOTS.map((shot) => {
    const article = shotTemplate.content.firstElementChild.cloneNode(true);
    article.dataset.shot = shot.id;
    article.dataset.start = String(shot.start);
    article.dataset.end = String(shot.end);
    article.querySelector('.film-shot-number').textContent = shot.number;
    article.querySelector('.film-shot-title').textContent = shot.title;
    article.querySelector('.film-shot-range').textContent = `FILM ${shot.range}`;
    article.querySelector('.artboard-label').append(` SHOT ${shot.number} · ${(shot.end - shot.start).toFixed(1)}s`);
    article.querySelector('.orbit-film-scene').setAttribute('aria-label', `${shot.title} storyboard animation`);
    article.querySelector('.film-phase').textContent = shot.phase;
    article.querySelector('.shot-caption-number').textContent = `${shot.number} / STORYBOARD`;
    article.querySelector('.film-progress').setAttribute('aria-label', `${shot.title} progress`);
    article.querySelector('.film-toolbar').setAttribute('aria-label', `${shot.title} controls`);
    article.querySelector('.globe-note').textContent = shot.description;
    return article;
  }));
  section.querySelector('#film-storyboard-title').textContent = 'Six shots, one continuous film.';
  section.querySelector('#film-timeline-note').textContent = FILM_SHOTS
    .map((shot) => `${shot.range.slice(0, -1)} ${shot.title}`).join(' · ');

  const openingInput = section.querySelector('#film-opening');
  const weaveInput = section.querySelector('#film-weave');
  const ringInput = section.querySelector('#film-ring-speed');
  const speedInput = section.querySelector('#film-speed');
  const resetButton = section.querySelector('#film-reset-tuning');
  const tuningInputs = [openingInput, weaveInput, ringInput, speedInput, resetButton];
  const listeners = new AbortController();
  const players = [];
  const byContainer = new Map();
  let renderer;
  let film;
  let frameId = null;
  let previousTime = null;
  let renderWidth = 0;
  let renderHeight = 0;
  let failed = false;
  let disposed = false;

  function options() {
    return {
      opening: openingInput.value,
      weave: Number(weaveInput.value),
      ringSpeed: Number(ringInput.value),
      orbitSettings: getOrbitSettings(),
    };
  }

  function fail(cause) {
    if (failed || disposed) return;
    failed = true;
    console.error('The globe film could not render:', cause);
    if (frameId !== null) cancelAnimationFrame(frameId);
    frameId = previousTime = null;
    for (const article of section.querySelectorAll('.orbit-film-player')) {
      const error = article.querySelector('.error-message');
      error.textContent = 'This film could not start. Reload with WebGL enabled.';
      error.hidden = false;
      for (const control of article.querySelectorAll('button, input')) control.disabled = true;
      article.querySelector('.orbit-film-scene').dataset.ready = 'false';
      article.querySelector('.film-play').textContent = 'Play';
    }
    for (const input of tuningInputs) input.disabled = true;
    for (const player of players) player.playing = false;
  }

  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(0x000000, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    film = createOrbitFilm(renderer);
  } catch (cause) {
    fail(cause);
    renderer?.dispose();
    renderer?.forceContextLoss();
    return;
  }

  function isActive() {
    return !failed && !disposed && !document.hidden && players.some((player) => player.playing && player.visible);
  }

  function schedule() {
    if (!isActive()) {
      if (frameId !== null) cancelAnimationFrame(frameId);
      frameId = previousTime = null;
    } else if (frameId === null) {
      previousTime = null;
      frameId = requestAnimationFrame(tick);
    }
  }

  function render(player) {
    if (failed || disposed || !player.width || !player.height) return;
    try {
      const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
      if (renderer.getPixelRatio() !== pixelRatio) renderer.setPixelRatio(pixelRatio);
      if (renderWidth !== player.width || renderHeight !== player.height) {
        renderer.setSize(player.width, player.height, false);
        renderWidth = player.width;
        renderHeight = player.height;
      }
      const elapsed = player.progress * player.duration;
      const seconds = player.start + elapsed;
      const phase = film.update(seconds, player.width / player.height, options());
      renderer.render(film.scene, film.camera);

      // Copy synchronously before another panel reuses the shared WebGL buffer.
      const source = renderer.domElement;
      if (player.canvas.width !== source.width || player.canvas.height !== source.height) {
        player.canvas.width = source.width;
        player.canvas.height = source.height;
      }
      player.context.clearRect(0, 0, player.canvas.width, player.canvas.height);
      player.context.drawImage(source, 0, 0);

      player.phaseLabel.textContent = phase;
      player.slider.value = String(player.progress);
      player.slider.setAttribute('aria-valuetext', `${elapsed.toFixed(1)} of ${player.duration.toFixed(1)} seconds; film ${seconds.toFixed(1)} seconds: ${phase}`);
      player.timeLabel.textContent = `${elapsed.toFixed(1)} / ${player.duration.toFixed(1)}s${player.isFull ? '' : ` · film ${seconds.toFixed(1)}s`}`;
      player.playButton.textContent = player.playing ? 'Pause' : 'Play';
      player.container.dataset.ready = 'true';
      player.container.dataset.progress = String(player.progress);
      player.container.dataset.filmTime = String(seconds);
      player.container.dataset.phase = phase;
    } catch (cause) {
      fail(cause);
    }
  }

  function resize(player) {
    const { width, height } = player.container.getBoundingClientRect();
    player.width = width > 0 ? Math.max(1, Math.round(width)) : 0;
    player.height = height > 0 ? Math.max(1, Math.round(height)) : 0;
    render(player);
  }

  function tick(time) {
    frameId = null;
    const delta = previousTime === null ? 0 : Math.min((time - previousTime) / 1000, 0.1);
    previousTime = time;
    const speed = Number(speedInput.value);
    for (const player of players) {
      if (!player.playing || !player.visible || document.hidden || failed) continue;
      const next = player.progress + delta * speed / player.duration;
      if (next >= 1) {
        player.progress = player.loopInput.checked ? next % 1 : 1;
        if (!player.loopInput.checked) player.playing = false;
      } else player.progress = next;
      render(player);
    }
    if (isActive()) frameId = requestAnimationFrame(tick);
    else previousTime = null;
  }

  const resizeObserver = new ResizeObserver((entries) => {
    for (const entry of entries) resize(byContainer.get(entry.target));
  });
  const visibilityObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) byContainer.get(entry.target).visible = entry.isIntersecting;
    schedule();
  });

  for (const article of section.querySelectorAll('.orbit-film-player')) {
    const container = article.querySelector('.orbit-film-scene');
    const canvas = document.createElement('canvas');
    canvas.setAttribute('aria-hidden', 'true');
    const context = canvas.getContext('2d');
    if (!context) {
      fail(new Error('Canvas 2D rendering is unavailable.'));
      break;
    }
    container.append(canvas);
    const slider = article.querySelector('.film-progress');
    const player = {
      container, canvas, context, slider,
      start: Number(article.dataset.start),
      duration: Number(article.dataset.end) - Number(article.dataset.start),
      isFull: article.dataset.shot === 'full',
      playButton: article.querySelector('.film-play'),
      replayButton: article.querySelector('.film-replay'),
      loopInput: article.querySelector('.film-loop'),
      phaseLabel: article.querySelector('.film-phase'),
      timeLabel: article.querySelector('.film-time'),
      progress: Math.max(0, Math.min(1, Number(slider.value))),
      playing: false,
      visible: false,
      width: 0,
      height: 0,
    };
    players.push(player);
    byContainer.set(container, player);
    container.dataset.renderer = 'three.js-shared-canvas';
    container.dataset.ready = 'false';

    player.playButton.addEventListener('click', () => {
      if (!player.playing && player.progress >= 1) player.progress = 0;
      player.playing = !player.playing;
      render(player);
      schedule();
    }, { signal: listeners.signal });
    player.replayButton.addEventListener('click', () => {
      player.progress = 0;
      player.playing = true;
      render(player);
      schedule();
    }, { signal: listeners.signal });
    slider.addEventListener('input', () => {
      player.playing = false;
      player.progress = Math.max(0, Math.min(1, Number(slider.value)));
      render(player);
      schedule();
    }, { signal: listeners.signal });

    resize(player);
    resizeObserver.observe(container);
    visibilityObserver.observe(container);
  }

  function redrawAll() {
    for (const player of players) render(player);
  }
  const unsubscribeOrbit = subscribeOrbitSettings(redrawAll);
  for (const input of [openingInput, weaveInput, ringInput, speedInput]) {
    input.addEventListener('input', redrawAll, { signal: listeners.signal });
  }
  resetButton.addEventListener('click', () => {
    openingInput.value = 'nose';
    weaveInput.value = '1';
    ringInput.value = '1';
    speedInput.value = '1';
    redrawAll();
  }, { signal: listeners.signal });
  document.addEventListener('visibilitychange', () => {
    previousTime = null;
    schedule();
  }, { signal: listeners.signal });
  renderer.domElement.addEventListener('webglcontextlost', (event) => {
    event.preventDefault();
    fail(new Error('The shared WebGL context was lost.'));
  }, { signal: listeners.signal });

  const disposeExport = startFilmExport(section, options, () => {
    for (const player of players) player.playing = false;
    schedule();
    redrawAll();
  });

  function dispose() {
    if (disposed) return;
    disposed = true;
    if (frameId !== null) cancelAnimationFrame(frameId);
    listeners.abort();
    disposeExport();
    unsubscribeOrbit();
    resizeObserver.disconnect();
    visibilityObserver.disconnect();
    film.dispose();
    renderer.dispose();
    renderer.forceContextLoss();
    for (const player of players) {
      player.canvas.remove();
      delete player.container.dataset.ready;
    }
  }
  if (import.meta.hot) import.meta.hot.dispose(dispose);
  return dispose;
}
