import * as THREE from 'three';
import { createOrbitFilm } from './orbit-film.js';
import { FILM_DURATION } from './orbit-flight.js';

const API = '/__snn_export';
const WIDTH = 1920;
const HEIGHT = 1080;
const FPS = 60;
const FRAMES = FILM_DURATION * FPS;
const EXPORT_HEADERS = { 'X-SNN-Export': '1' };

async function jsonRequest(path, options = {}) {
  const response = await fetch(`${API}${path}`, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'The video export could not finish.');
  return result;
}

function pngFrame(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error('A film frame could not be captured. Please retry the export.'));
    }, 'image/png');
  });
}

async function renderMp4(settings, signal, onProgress) {
  let job;
  let renderer;
  let film;
  let completed = false;
  let contextLost = false;
  try {
    job = await jsonRequest('/jobs', {
      method: 'POST', headers: { ...EXPORT_HEADERS, 'Content-Type': 'application/json' },
      body: '{}', signal,
    });
    signal.throwIfAborted();
    // A dedicated canvas keeps editor guides, preview sizing, and other
    // playing shots out of the export. Paper must be rendered into the pixels.
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: true });
    renderer.setPixelRatio(1);
    renderer.setSize(WIDTH, HEIGHT, false);
    renderer.setClearColor(0xf8f6f0, 1);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.NoToneMapping;
    renderer.domElement.addEventListener('webglcontextlost', (event) => {
      event.preventDefault();
      contextLost = true;
    });
    film = createOrbitFilm(renderer);
    for (let index = 0; index < FRAMES; index += 1) {
      signal.throwIfAborted();
      if (contextLost) throw new Error('Rendering was interrupted. Please retry the export.');
      film.update(index / FPS, WIDTH / HEIGHT, settings);
      // update() switches both the scene and camera at the Snoopy/Earth cut.
      renderer.render(film.scene, film.camera);
      const frame = await pngFrame(renderer.domElement);
      signal.throwIfAborted();
      if (contextLost) throw new Error('Rendering was interrupted. Please retry the export.');
      await jsonRequest(`/jobs/${job.id}/frames?index=${index}`, {
        method: 'POST', headers: { ...EXPORT_HEADERS, 'Content-Type': 'image/png' }, body: frame, signal,
      });
      onProgress(index + 1, FRAMES);
    }
    const result = await jsonRequest(`/jobs/${job.id}/finish`, {
      method: 'POST', headers: EXPORT_HEADERS, signal,
    });
    completed = true;
    return result;
  } finally {
    film?.dispose();
    renderer?.dispose();
    renderer?.forceContextLoss();
    if (job && !completed) {
      // A canceled request must not leave an encoder running on the server.
      await fetch(`${API}/jobs/${job.id}`, {
        method: 'DELETE', headers: EXPORT_HEADERS, keepalive: true,
      }).catch(() => {});
    }
  }
}

export function startFilmExport(section, getSettings, pausePreviews) {
  const button = section.querySelector('#film-export');
  const cancel = section.querySelector('#film-export-cancel');
  const status = section.querySelector('#film-export-status');
  const progress = section.querySelector('#film-export-progress');
  const download = section.querySelector('#film-export-download');
  const listeners = new AbortController();
  let controller;
  let disposed = false;
  let available = false;

  jsonRequest('/capabilities', { signal: listeners.signal }).then((capability) => {
    if (disposed) return;
    available = capability.available === true;
    button.disabled = !available;
    status.textContent = available ? '1080p · 60 fps · 24 seconds · paper background'
      : capability.error || 'MP4 export needs FFmpeg installed on the local preview server.';
  }).catch(() => {
    if (!disposed) status.textContent = 'MP4 export is available in the local development preview.';
  });

  button.addEventListener('click', async () => {
    if (controller || !available) return;
    controller = new AbortController();
    const signal = controller.signal;
    // Later edits or the preview playback-speed setting cannot change a render
    // halfway through. The exported film always uses its normal 24-second clock.
    const settings = structuredClone(getSettings());
    pausePreviews();
    button.disabled = true;
    button.textContent = 'Exporting…';
    cancel.hidden = false;
    progress.hidden = false;
    progress.max = FRAMES;
    progress.value = 0;
    download.hidden = true;
    status.textContent = 'Preparing the complete film…';
    try {
      const result = await renderMp4(settings, signal, (done, total) => {
        progress.value = done;
        status.textContent = done === total ? 'Finishing the MP4…'
          : `Rendering ${Math.floor(done / total * 100)}% · ${done.toLocaleString()} / ${total.toLocaleString()} frames`;
      });
      if (disposed) return;
      download.href = result.downloadUrl;
      download.download = result.filename;
      download.hidden = false;
      status.textContent = 'MP4 ready · 1080p · 60 fps · 24 seconds';
      download.click();
    } catch (error) {
      if (!disposed) status.textContent = signal.aborted ? 'Export canceled. You can start again.'
        : error.message || 'The video export could not finish. Please try again.';
    } finally {
      controller = undefined;
      if (!disposed) {
        button.disabled = !available;
        button.textContent = 'Export MP4';
        cancel.hidden = true;
        progress.hidden = true;
      }
    }
  }, { signal: listeners.signal });
  cancel.addEventListener('click', () => controller?.abort(), { signal: listeners.signal });
  return () => {
    disposed = true;
    controller?.abort();
    listeners.abort();
  };
}
