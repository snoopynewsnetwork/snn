import assert from 'node:assert/strict';
import test from 'node:test';
import { createServer, request as httpRequest } from 'node:http';
import { deflateSync } from 'node:zlib';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { createVideoExportMiddleware } from '../tools/video-export-server.js';

const execute = promisify(execFile);
const header = { 'X-SNN-Export': '1' };

async function localServer(options, run) {
  const middleware = createVideoExportMiddleware(options);
  const server = createServer((request, response) => middleware(request, response, () => {
    response.writeHead(404); response.end();
  }));
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/__snn_export`;
  try { await run(base); } finally {
    await middleware.dispose();
    await new Promise((resolve) => server.close(resolve));
  }
}

function crc32(buffer) {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}
function chunk(type, data) {
  const content = Buffer.concat([Buffer.from(type), data]);
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(content));
  return Buffer.concat([length, content, crc]);
}
function png(width, height, value = 240) {
  const info = Buffer.alloc(13);
  info.writeUInt32BE(width, 0); info.writeUInt32BE(height, 4);
  info[8] = 8; info[9] = 2;
  const rows = Buffer.alloc(height * (width * 3 + 1), value);
  for (let row = 0; row < height; row++) rows[row * (width * 3 + 1)] = 0;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', info),
    chunk('IDAT', deflateSync(rows)), chunk('IEND', Buffer.alloc(0))]);
}

async function request(base, path, method = 'GET', data, headers = header) {
  return new Promise((resolve, reject) => {
    const outgoing = httpRequest(base + path, { method, headers }, (response) => {
      const chunks = [];
      response.on('data', (chunk) => chunks.push(chunk));
      response.on('end', () => {
        try { resolve({ status: response.statusCode, content: JSON.parse(Buffer.concat(chunks)) }); }
        catch (error) { reject(error); }
      });
      response.on('error', reject);
    });
    outgoing.on('error', reject);
    outgoing.end(data);
  });
}

test('export endpoints are local, same-origin, and require an explicit mutation header', async () => {
  await localServer({ ffmpegPath: '/no-such-snn-ffmpeg' }, async (base) => {
    assert.deepEqual(await request(base, '/capabilities'), { status: 200, content: { available: false } });
    assert.equal((await request(base, '/jobs', 'POST', '{}', {})).status, 403);
    assert.equal((await request(base, '/jobs', 'POST', '{}', { ...header, Origin: 'https://example.com' })).status, 403);
    assert.equal((await request(base, '/jobs', 'POST', '{}', { ...header, Host: 'example.com' })).status, 403);
    assert.equal((await request(base, '/jobs', 'POST', '{}', { ...header, 'Sec-Fetch-Site': 'cross-site' })).status, 403);
    const unavailable = await request(base, '/jobs', 'POST', '{}');
    assert.equal(unavailable.status, 503);
    assert.match(unavailable.content.error, /FFmpeg/);
    assert.equal((await request(base, '/jobs/not-a-job/video')).status, 404);
  });
});

test('sequential PNG export makes an exact MP4, rejects incomplete frames, and cancels cleanly', async (context) => {
  try { await execute('ffmpeg', ['-version']); await execute('ffprobe', ['-version']); }
  catch { context.skip('FFmpeg and ffprobe are required for the local encoding integration test.'); return; }
  await localServer({ width: 128, height: 72, fps: 6, frameCount: 6 }, async (base) => {
    assert.equal((await request(base, '/capabilities')).content.available, true);
    const starts = await Promise.all([request(base, '/jobs', 'POST', '{}'), request(base, '/jobs', 'POST', '{}')]);
    assert.deepEqual(starts.map(({ status }) => status).sort(), [201, 409], 'concurrent starts share one creation lock');
    const created = starts.find(({ status }) => status === 201);
    const path = `/jobs/${created.content.id}`;
    assert.equal((await request(base, '/jobs', 'POST', '{}')).status, 409, 'one encoder runs at a time');
    assert.equal((await request(base, `${path}/finish`, 'POST', '{}')).status, 409);
    assert.equal((await request(base, `${path}/frames?index=1`, 'POST', png(128, 72))).status, 409);
    assert.equal((await request(base, `${path}/frames?index=0`, 'POST', Buffer.from('not a PNG'))).status, 400);
    assert.equal((await request(base, `${path}/frames?index=0`, 'POST', png(64, 64))).status, 400);
    for (let index = 0; index < 6; index++) {
      assert.deepEqual(await request(base, `${path}/frames?index=${index}`, 'POST', png(128, 72, 180 + index * 10)),
        { status: 200, content: { frame: index + 1 } });
    }
    assert.equal((await request(base, `${path}/frames?index=6`, 'POST', png(128, 72))).status, 409);
    const finished = await request(base, `${path}/finish`, 'POST', '{}');
    assert.equal(finished.status, 200);
    assert.equal(finished.content.filename, 'snn-world-intro.mp4');
    const video = await fetch(new URL(finished.content.downloadUrl, base));
    assert.equal(video.status, 200);
    assert.equal(video.headers.get('content-type'), 'video/mp4');
    assert.match(video.headers.get('content-disposition'), /attachment/);
    const directory = await mkdtemp(join(tmpdir(), 'snn-export-test-'));
    try {
      const output = join(directory, 'film.mp4');
      await writeFile(output, Buffer.from(await video.arrayBuffer()));
      const { stdout } = await execute('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', output]);
      const info = JSON.parse(stdout);
      const stream = info.streams[0];
      assert.equal(info.streams.length, 1, 'the silent film has one video stream');
      assert.equal(stream.codec_name, 'h264');
      assert.equal(stream.pix_fmt, 'yuv420p');
      assert.equal(stream.width, 128); assert.equal(stream.height, 72);
      assert.equal(stream.sample_aspect_ratio, '1:1');
      assert.equal(stream.r_frame_rate, '6/1');
      assert.equal(stream.nb_frames, '6');
      assert.equal(Number(info.format.duration), 1);
      assert.equal(stream.color_space, 'bt709');
      await execute('ffmpeg', ['-v', 'error', '-i', output, '-f', 'null', '-']);
    } finally { await rm(directory, { recursive: true, force: true }); }
    assert.equal((await request(base, path, 'DELETE')).status, 200);
    assert.equal((await request(base, `${path}/video`)).status, 404);
    const cancelled = await request(base, '/jobs', 'POST', '{}');
    const cancelPath = `/jobs/${cancelled.content.id}`;
    assert.equal((await request(base, cancelPath, 'DELETE')).status, 200);
    assert.equal((await request(base, `${cancelPath}/frames?index=0`, 'POST', png(128, 72))).status, 404);
  });
});
