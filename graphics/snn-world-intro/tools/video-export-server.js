import { spawn, execFile } from 'node:child_process';
import { createReadStream } from 'node:fs';
import { mkdtemp, rm, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { promisify } from 'node:util';

const execute = promisify(execFile);
const PREFIX = '/__snn_export';
const PNG = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
const MAX_BODY = 16 * 1024 * 1024;
const LOOPBACK = new Set(['127.0.0.1', '::1', '::ffff:127.0.0.1']);
const HOSTS = new Set(['localhost', '127.0.0.1', '[::1]']);

function failure(status, message) {
  return Object.assign(new Error(message), { status });
}
function json(response, status, value) {
  response.writeHead(status, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
  response.end(JSON.stringify(value));
}
function body(request) {
  if (Number(request.headers['content-length']) > MAX_BODY) {
    request.resume();
    return Promise.reject(failure(413, 'Frame exceeds the 16 MB upload limit.'));
  }
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    const cleanup = () => {
      request.off('data', onData);
      request.off('end', onEnd);
      request.off('error', onError);
      request.off('aborted', onAbort);
    };
    const onError = (error) => { cleanup(); reject(error); };
    const onAbort = () => onError(failure(400, 'Frame upload was interrupted.'));
    const onEnd = () => { cleanup(); resolve(Buffer.concat(chunks)); };
    const onData = (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY) {
        cleanup();
        request.resume();
        reject(failure(413, 'Frame exceeds the 16 MB upload limit.'));
      } else chunks.push(chunk);
    };
    request.on('data', onData);
    request.on('end', onEnd);
    request.on('error', onError);
    request.on('aborted', onAbort);
  });
}

/** Local-only export service. Options exist for small integration-test renders. */
export function createVideoExportMiddleware({ ffmpegPath = 'ffmpeg', width = 1920, height = 1080,
  fps = 60, frameCount = 1440, ttlMs = 15 * 60 * 1000 } = {}) {
  const jobs = new Map();
  let capabilities;
  let disposed = false;
  let creating = false;
  const checkEncoder = () => capabilities ??= execute(ffmpegPath, ['-hide_banner', '-encoders'],
    { timeout: 10000, maxBuffer: 1024 * 1024 }).then(({ stdout }) => ({ available: /\blibx264\b/.test(stdout) }))
    .catch(() => ({ available: false }));

  async function remove(job) {
    jobs.delete(job.id);
    if (job.child.exitCode === null && job.child.signalCode === null) {
      job.child.kill('SIGKILL');
      await job.done;
    }
    await rm(job.directory, { recursive: true, force: true });
  }
  const reap = setInterval(() => {
    for (const job of jobs.values()) {
      if (!job.downloading && Date.now() - job.touched > ttlMs) void remove(job).catch(() => {});
    }
  }, Math.min(ttlMs, 30000));
  reap.unref();

  async function createJob() {
    if (!(await checkEncoder()).available) throw failure(503, 'MP4 export requires FFmpeg with the libx264 encoder on this computer.');
    if ([...jobs.values()].some((job) => !job.finished && !job.error)) throw failure(409, 'Another video export is already running.');
    if (jobs.size >= 4) {
      const old = [...jobs.values()].find((job) => !job.downloading);
      if (!old) throw failure(409, 'Finish the current downloads before exporting again.');
      await remove(old);
    }
    const directory = await mkdtemp(join(tmpdir(), 'snn-video-'));
    const output = join(directory, 'snn-world-intro.mp4');
    const child = spawn(ffmpegPath, [
      '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
      '-f', 'image2pipe', '-framerate', String(fps), '-vcodec', 'png', '-i', 'pipe:0',
      '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '4',
      '-vf', 'scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,setsar=1',
      '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
      '-frames:v', String(frameCount), '-movflags', '+faststart', output,
    ], { stdio: ['pipe', 'ignore', 'pipe'] });
    const job = { id: randomUUID(), directory, output, child, index: 0, busy: false,
      finished: false, touched: Date.now(), downloading: 0, error: null, stderr: '' };
    child.stderr.on('data', (chunk) => { job.stderr = (job.stderr + chunk.toString()).slice(-8192); });
    child.stdin.on('error', (error) => { job.error ??= error.message; });
    job.done = new Promise((resolve) => {
      child.once('error', (error) => { job.error = error.message; });
      child.once('close', (code, signal) => {
        if (code !== 0) job.error ??= job.stderr.trim() || `FFmpeg stopped (${signal ?? code}).`;
        resolve();
      });
    });
    jobs.set(job.id, job);
    try {
      await new Promise((resolve, reject) => { child.once('spawn', resolve); child.once('error', reject); });
    } catch {
      await remove(job);
      throw failure(503, 'FFmpeg could not start. Check that it is installed and available on PATH.');
    }
    return job;
  }

  async function handle(request, response, next) {
    if (!request.url?.startsWith(PREFIX)) return next();
    try {
      if (disposed) throw failure(503, 'The export server is shutting down.');
      let origin;
      try { origin = new URL(`http://${request.headers.host}`); } catch { throw failure(403, 'Local export requests only.'); }
      if (!LOOPBACK.has(request.socket.remoteAddress) || !HOSTS.has(origin.hostname)) throw failure(403, 'Local export requests only.');
      if ((request.headers.origin && request.headers.origin !== origin.origin)
        || request.headers['sec-fetch-site'] === 'cross-site') throw failure(403, 'Export requests must come from this page.');
      const url = new URL(request.url, origin);
      const method = request.method;
      if (method !== 'GET' && request.headers['x-snn-export'] !== '1') throw failure(403, 'Missing export request header.');
      if (url.pathname === `${PREFIX}/capabilities` && method === 'GET') return json(response, 200, await checkEncoder());
      if (url.pathname === `${PREFIX}/jobs` && method === 'POST') {
        if (creating) throw failure(409, 'Another video export is starting.');
        creating = true;
        try {
          await body(request);
          const job = await createJob();
          return json(response, 201, { id: job.id });
        } finally { creating = false; }
      }
      const match = url.pathname.match(/^\/__snn_export\/jobs\/([a-f0-9-]+)(?:\/(frames|finish|video))?$/);
      const job = match && jobs.get(match[1]);
      if (!job) throw failure(404, 'This video export was not found or has expired.');
      job.touched = Date.now();
      const action = match[2];
      if (!action && method === 'DELETE') {
        await remove(job);
        return json(response, 200, { cancelled: true });
      }
      if (action === 'video' && method === 'GET') {
        if (!job.finished) throw failure(409, 'The video is not ready to download.');
        const info = await stat(job.output);
        job.downloading += 1;
        response.writeHead(200, { 'Content-Type': 'video/mp4', 'Content-Length': info.size,
          'Content-Disposition': 'attachment; filename="snn-world-intro.mp4"', 'Cache-Control': 'no-store' });
        const stream = createReadStream(job.output);
        response.once('close', () => { job.downloading -= 1; job.touched = Date.now(); stream.destroy(); });
        stream.once('error', () => response.destroy());
        stream.pipe(response);
        return;
      }
      if (job.error) throw failure(500, `Video encoding failed: ${job.error}`);
      if (job.busy || job.finished) throw failure(409, 'This video export is busy or already complete.');
      if (action === 'frames' && method === 'POST') {
        if (url.searchParams.get('index') !== String(job.index) || job.index >= frameCount) throw failure(409, `Expected frame ${job.index}.`);
        job.busy = true;
        try {
          const frame = await body(request);
          if (frame.length < 33 || !frame.subarray(0, 8).equals(PNG) || frame.toString('ascii', 12, 16) !== 'IHDR'
            || frame.readUInt32BE(16) !== width || frame.readUInt32BE(20) !== height) {
            throw failure(400, `Each frame must be a ${width}×${height} PNG.`);
          }
          await new Promise((resolve, reject) => job.child.stdin.write(frame, (error) => error ? reject(error) : resolve()));
          if (job.error) throw failure(500, `Video encoding failed: ${job.error}`);
          job.index += 1;
          job.touched = Date.now();
          return json(response, 200, { frame: job.index });
        } finally { job.busy = false; }
      }
      if (action === 'finish' && method === 'POST') {
        if (job.index !== frameCount) throw failure(409, `Expected ${frameCount} frames; received ${job.index}.`);
        job.busy = true;
        try {
          await body(request);
          job.child.stdin.end();
          await job.done;
          if (job.error) throw failure(500, `Video encoding failed: ${job.error}`);
          if (!(await stat(job.output)).size) throw failure(500, 'FFmpeg did not produce a video.');
          job.finished = true;
          job.touched = Date.now();
          return json(response, 200, { downloadUrl: `${PREFIX}/jobs/${job.id}/video`, filename: 'snn-world-intro.mp4' });
        } finally { job.busy = false; }
      }
      throw failure(405, 'Unsupported export request.');
    } catch (error) {
      if (!response.headersSent && !response.destroyed) json(response, error.status ?? 500, { error: error.message || 'Video export failed.' });
    }
  }
  const middleware = (request, response, next) => { void handle(request, response, next); };
  middleware.dispose = async () => {
    disposed = true;
    clearInterval(reap);
    await Promise.all([...jobs.values()].map(remove));
  };
  return middleware;
}

export function videoExportPlugin() {
  function configure(server) {
    const middleware = createVideoExportMiddleware();
    server.middlewares.use(middleware);
    server.httpServer?.once('close', () => { void middleware.dispose(); });
  }
  return { name: 'snn-local-video-export', configureServer: configure, configurePreviewServer: configure };
}
