import type { ElectionSource } from "./adapters/types";

export function resolveSourceUrl(source: ElectionSource, bodies: Record<string, string>): string {
  let url = source.url;
  if (source.dependsOn) {
    const version = bodies[source.dependsOn]?.trim();
    if (!version || !/^[0-9]{1,12}$/.test(version)) throw new Error(`Version source ${source.dependsOn} is unavailable or invalid.`);
    url = url.replaceAll("{version}", version);
  }
  const parsed = new URL(url);
  if (!/^https?:$/.test(parsed.protocol) || parsed.username || parsed.password || url.includes("{version}"))
    throw new Error("Invalid configured results URL.");
  return parsed.href;
}

export async function readSourceBody(response: Response, source: ElectionSource): Promise<string> {
  const limit = Math.min(source.maxBytes ?? 2_000_000, 32_000_000);
  const reader = response.body?.getReader();
  if (!reader) throw new Error("Source returned an empty response.");
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > limit) { await reader.cancel(); throw new Error(`Source response exceeds its ${limit.toLocaleString("en-US")} byte limit.`); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  if (!size) throw new Error("Source returned an empty response.");
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  if (source.encoding === "base64") {
    let binary = "";
    for (let i = 0; i < bytes.length; i += 16384) binary += String.fromCharCode(...bytes.subarray(i, i + 16384));
    return btoa(binary);
  }
  const text = new TextDecoder("utf-8", { fatal: true, ignoreBOM: false }).decode(bytes);
  if (!text.trim()) throw new Error("Source returned a blank response.");
  return text;
}

export function sourceLayers(sources: ElectionSource[]): ElectionSource[][] {
  const remaining = new Map(sources.map(source => [source.id, source]));
  if (remaining.size !== sources.length) throw new Error("Duplicate source ids in adapter.");
  const done = new Set<string>();
  const layers: ElectionSource[][] = [];
  while (remaining.size) {
    const layer = [...remaining.values()].filter(source => !source.dependsOn || done.has(source.dependsOn));
    if (!layer.length) throw new Error("Missing or circular source dependency.");
    layers.push(layer);
    for (const source of layer) { remaining.delete(source.id); done.add(source.id); }
  }
  return layers;
}
