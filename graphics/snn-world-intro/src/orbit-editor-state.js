import { MathUtils, Quaternion, Vector3 } from 'three';
import { letterAngle } from './orbit-flight.js';

export const DEFAULT_ORBIT_SETTINGS = Object.freeze({ radius: 205, tilt: 0, heading: 0, phase: 0, speed: 1 });
const STORAGE_KEY = 'snn-world-intro:orbit-settings:v1';
const VERSION = 1;
const LIMITS = { radius: [165, 360], tilt: [-90, 90], heading: [-180, 180], phase: [-180, 180], speed: [-0.5, 2] };
const listeners = new Set();

function normalizeSettings(values, fallback = DEFAULT_ORBIT_SETTINGS) {
  return Object.fromEntries(Object.entries(LIMITS).map(([key, [minimum, maximum]]) => {
    const value = values?.[key];
    return [key, typeof value === 'number' && Number.isFinite(value)
      ? MathUtils.clamp(value, minimum, maximum) : fallback[key]];
  }));
}

function loadSettings() {
  try {
    const stored = JSON.parse(globalThis.localStorage?.getItem(STORAGE_KEY) ?? 'null');
    if (stored?.version === VERSION) return normalizeSettings(stored.settings);
  } catch { /* Storage may be disabled, unavailable, or contain an invalid document. */ }
  return { ...DEFAULT_ORBIT_SETTINGS };
}

// Pure pose calculations can run on the server without touching browser storage.
let settings;

function currentSettings() {
  settings ??= loadSettings();
  return settings;
}

export function getOrbitSettings() {
  return { ...currentSettings() };
}

export function exportOrbitSettingsJSON() {
  return JSON.stringify({ version: VERSION, settings: getOrbitSettings() }, null, 2);
}

export function setOrbitSettings(partial) {
  const next = normalizeSettings(partial, currentSettings());
  const changed = Object.keys(DEFAULT_ORBIT_SETTINGS).some((key) => next[key] !== settings[key]);
  settings = next;
  try {
    globalThis.localStorage?.setItem(STORAGE_KEY, exportOrbitSettingsJSON());
  } catch { /* The current session remains editable when persistence is unavailable. */ }
  if (changed) for (const listener of listeners) listener(getOrbitSettings());
  return getOrbitSettings();
}

export function resetOrbitSettings() {
  return setOrbitSettings(DEFAULT_ORBIT_SETTINGS);
}

// Subscribers receive independent snapshots after changes, not an initial call.
export function subscribeOrbitSettings(listener) {
  if (typeof listener !== 'function') throw new TypeError('An orbit settings listener must be a function.');
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/**
 * Adjust only the orbital objects. Camera fields retain their original values.
 * Heading, tilt, and starting phase are degrees. Apply heading around world Y,
 * then tilt around world X: Qx(tilt) * Qy(heading) * the original orbital frame.
 * Speed scales the authored angular travel throughout the film, including
 * its changing pace during the reveal. The orbital plane stays fixed; the
 * authored facing change continues independently of travel around the axis.
 */
export function applyOrbitSettings(pose, seconds, values = DEFAULT_ORBIT_SETTINGS) {
  const normalized = normalizeSettings(values);
  if (Object.keys(DEFAULT_ORBIT_SETTINGS).every((key) => normalized[key] === DEFAULT_ORBIT_SETTINGS[key])) {
    return { ...pose, center: pose.center.clone(), frame: pose.frame.clone(),
      letterQuaternion: pose.letterQuaternion.clone() };
  }

  const deltaAngle = MathUtils.degToRad(normalized.phase)
    + (normalized.speed - 1) * (pose.angle - letterAngle(0));
  const heading = new Quaternion().setFromAxisAngle(new Vector3(0, 1, 0), MathUtils.degToRad(normalized.heading));
  const offset = new Quaternion().setFromAxisAngle(new Vector3(1, 0, 0), MathUtils.degToRad(normalized.tilt)).multiply(heading);
  const frame = offset.multiply(pose.frame);
  const angle = pose.angle + deltaAngle;
  const center = new Vector3(Math.sin(angle) * normalized.radius, 18, Math.cos(angle) * normalized.radius)
    .applyQuaternion(frame);
  const letterQuaternion = frame.clone()
    .multiply(new Quaternion().setFromAxisAngle(new Vector3(0, 1, 0), deltaAngle))
    .multiply(pose.frame.clone().invert()).multiply(pose.letterQuaternion);
  return { ...pose, center, frame, angle, letterQuaternion };
}
