import * as THREE from 'three';
import { createHeadTransition } from './transition-head.js';
import { createNoseTransition } from './transition-nose.js';
import { createInkTransition } from './transition-ink.js';
import { createFlatInkTransition } from './transition-flat.js';

const DURATION = 6;
const factories = {
  head: createHeadTransition, nose: createNoseTransition, ink: createInkTransition,
  'flat-nose': (renderer) => createFlatInkTransition(renderer, 'nose'),
  'flat-eye': (renderer) => createFlatInkTransition(renderer, 'eye'),
  'flat-ear': (renderer) => createFlatInkTransition(renderer, 'ear'),
};

export function startTransitionStudies() {
  startTransitionRow('#original-transition-studies', '#transitions-play-all');
  startTransitionRow('#flat-transition-studies', '#flat-transitions-play-all');
}

function startTransitionRow(sectionSelector, buttonSelector) {
  const section = document.querySelector(sectionSelector);
  if (!section) return;
  const players = [];
  const allButton = section.querySelector(buttonSelector);
  let frameId = null;
  let previousTime = null;

  function updateAllButton() {
    allButton.textContent = players.some((player) => player.playing) ? 'Pause all' : 'Play all ▶';
    allButton.disabled = players.length === 0;
  }
  function schedule() {
    if (frameId === null && !document.hidden && players.some((player) => player.playing && player.visible)) {
      previousTime = null;
      frameId = requestAnimationFrame(tick);
    }
  }
  function tick(time) {
    frameId = null;
    const delta = previousTime === null ? 0 : Math.min((time - previousTime) / 1000, 0.1);
    previousTime = time;
    for (const player of players) {
      if (!player.playing || !player.visible || document.hidden) continue;
      player.progress = Math.min(1, player.progress + delta / DURATION);
      if (player.progress === 1) player.playing = false;
      player.render();
    }
    updateAllButton();
    if (!document.hidden && players.some((player) => player.playing && player.visible)) {
      frameId = requestAnimationFrame(tick);
    } else previousTime = null;
  }

  for (const article of section.querySelectorAll('.transition-study')) {
    const container = article.querySelector('.transition-scene');
    const error = article.querySelector('.error-message');
    const playButton = article.querySelector('.transition-play');
    const replayButton = article.querySelector('.transition-replay');
    const slider = article.querySelector('.transition-progress');
    const phaseLabel = article.querySelector('.transition-phase');
    const timeLabel = article.querySelector('.transition-time');
    let renderer;
    let transition;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.setClearColor(0x000000, 0);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      transition = factories[article.dataset.transition](renderer);
    } catch (cause) {
      console.error('Transition could not start:', cause);
      renderer?.dispose();
      error.textContent = 'This prototype could not start. Reload with WebGL enabled.';
      error.hidden = false;
      playButton.disabled = replayButton.disabled = slider.disabled = true;
      continue;
    }
    renderer.domElement.setAttribute('aria-hidden', 'true');
    container.append(renderer.domElement);
    const player = { progress: 0, playing: false, visible: true, aspect: 1, render, dispose };
    players.push(player);

    function render() {
      const phase = transition.update(player.progress, player.aspect);
      renderer.render(transition.scene, transition.camera);
      phaseLabel.textContent = phase;
      slider.value = String(player.progress);
      slider.setAttribute('aria-valuetext', `${(player.progress * DURATION).toFixed(1)} seconds: ${phase}`);
      timeLabel.textContent = `${(player.progress * DURATION).toFixed(1)} / ${DURATION.toFixed(1)}s`;
      playButton.textContent = player.playing ? 'Pause' : 'Play';
      container.dataset.progress = String(player.progress);
      container.dataset.phase = phase;
    }
    function resize() {
      const { width, height } = container.getBoundingClientRect();
      if (!width || !height) return;
      player.aspect = width / height;
      renderer.setSize(width, height);
      render();
    }
    function toggle() {
      if (!player.playing && player.progress >= 1) player.progress = 0;
      player.playing = !player.playing;
      render(); updateAllButton(); schedule();
    }
    function replay() {
      player.progress = 0;
      player.playing = true;
      render(); updateAllButton(); schedule();
    }
    function scrub() {
      player.playing = false;
      player.progress = Number(slider.value);
      render(); updateAllButton();
    }
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(container);
    const visibilityObserver = new IntersectionObserver(([entry]) => {
      player.visible = entry.isIntersecting;
      schedule();
    });
    visibilityObserver.observe(container);
    playButton.addEventListener('click', toggle);
    replayButton.addEventListener('click', replay);
    slider.addEventListener('input', scrub);
    container.dataset.ready = 'true';
    resize();

    function dispose() {
      resizeObserver.disconnect(); visibilityObserver.disconnect();
      playButton.removeEventListener('click', toggle);
      replayButton.removeEventListener('click', replay);
      slider.removeEventListener('input', scrub);
      transition.dispose(); renderer.dispose(); renderer.domElement.remove();
    }
  }

  function toggleAll() {
    const pause = players.some((player) => player.playing);
    for (const player of players) {
      player.playing = !pause;
      if (!pause) player.progress = 0;
      player.render();
    }
    updateAllButton(); schedule();
  }
  function visibilityChange() { previousTime = null; schedule(); }
  allButton.addEventListener('click', toggleAll);
  document.addEventListener('visibilitychange', visibilityChange);
  updateAllButton();
  if (import.meta.hot) import.meta.hot.dispose(() => {
    if (frameId !== null) cancelAnimationFrame(frameId);
    allButton.removeEventListener('click', toggleAll);
    document.removeEventListener('visibilitychange', visibilityChange);
    players.forEach((player) => player.dispose());
  });
}
