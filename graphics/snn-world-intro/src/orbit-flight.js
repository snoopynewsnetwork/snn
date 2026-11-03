import * as THREE from 'three';
import { geoVector, SPHERE_VIEW } from './globe-projection.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const clamp = THREE.MathUtils.clamp;
export const FILM_DURATION = 24;
export const COAST_START = 1.8;
export const COAST_END = 5.8;
export const PULL_UP_END = 7.2;
export const CORNER_END = 8.6;
export const LETTERS_ENTER = 0;

export function smooth(start, end, time) {
  const t = clamp((time - start) / (end - start), 0, 1);
  return t * t * (3 - 2 * t);
}

function smoother(start, end, time) {
  const t = clamp((time - start) / (end - start), 0, 1);
  return t ** 3 * (10 - 15 * t + 6 * t ** 2);
}

// One physical clock for SNN's angular travel. Its equatorial plane stays
// fixed throughout the film, independently of the camera choreography.
const orbitKeys = [[11, 2.05, -0.16], [14, 0.72, -0.34], [18, -0.35, 0]];
function cameraOrbitAngle(time) {
  const t = clamp(time, 0, 18);
  if (t <= 11) return 3.81 - 0.16 * t;
  const index = t < 14 ? 0 : 1;
  const [a, av, m0] = orbitKeys[index];
  const [b, bv, m1] = orbitKeys[index + 1];
  const u = (t - a) / (b - a);
  return (2 * u ** 3 - 3 * u ** 2 + 1) * av
    + (u ** 3 - 2 * u ** 2 + u) * (b - a) * m0
    + (-2 * u ** 3 + 3 * u ** 2) * bv
    + (u ** 3 - u ** 2) * (b - a) * m1;
}

// Advance the whole orbit so the trailing N's ink clears the film's right
// edge at 11.9s. Keep this phase separate from the authored camera route.
const letterPhase = THREE.MathUtils.degToRad(-32);
export function letterAngle(time) {
  return cameraOrbitAngle(time) + letterPhase;
}

const earthOrientation = new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().lookAt(
  geoVector(SPHERE_VIEW.longitude, SPHERE_VIEW.latitude), V(0, 0, 0), V(0, 1, 0),
)).invert();
// One circle on the sphere sweeps across the North Pacific. These three
// broad landmarks define its plane; individual coastline bends never steer
// the camera. The arc has constant radius and curvature, including its aim.
const baja = geoVector(-112, 21).applyQuaternion(earthOrientation);
const alaska = geoVector(-165, 59).applyQuaternion(earthOrientation);
const japan = geoVector(136, 36).applyQuaternion(earthOrientation);
const coastNormal = alaska.clone().sub(baja).cross(japan.clone().sub(baja)).normalize();
const coastCenter = coastNormal.clone().multiplyScalar(coastNormal.dot(baja));
const coastCircleRadius = baja.distanceTo(coastCenter);
const coastAxisX = baja.clone().sub(coastCenter).normalize();
const coastAxisY = coastNormal.clone().cross(coastAxisX);
const coastSweep = Math.atan2(japan.clone().sub(coastCenter).dot(coastAxisY),
  japan.clone().sub(coastCenter).dot(coastAxisX));
export const COAST_RADIUS = 180;
const beneathN = V(-50, -18, Math.sqrt(COAST_RADIUS ** 2 - 50 ** 2) - 205);
function coastPoint(u, radius = COAST_RADIUS) {
  return coastCenter.clone()
    .addScaledVector(coastAxisX, coastCircleRadius * Math.cos(u * coastSweep))
    .addScaledVector(coastAxisY, coastCircleRadius * Math.sin(u * coastSweep)).multiplyScalar(radius);
}
function coastTangent(u) {
  return coastAxisX.clone().multiplyScalar(-Math.sin(u * coastSweep))
    .addScaledVector(coastAxisY, Math.cos(u * coastSweep));
}

// Retain the reference frame used to author the camera's Pacific approach
// and close pass. It now guides only the camera, not SNN's physical orbit.
const rendezvousDirection = coastPoint(1, 1);
const rendezvousHeading = coastTangent(1);
const unturnedMeeting = beneathN.clone().add(V(0, 18, 205)).applyAxisAngle(V(0, 1, 0), cameraOrbitAngle(COAST_END));
const tiltedOrbit = new THREE.Quaternion().setFromUnitVectors(unturnedMeeting.normalize(), rendezvousDirection);
const rise = V(1, 0, 0).applyAxisAngle(V(0, 1, 0), cameraOrbitAngle(COAST_END))
  .applyQuaternion(tiltedOrbit).projectOnPlane(rendezvousDirection).normalize();
const heading = rendezvousHeading.clone().projectOnPlane(rendezvousDirection).normalize();
const twist = Math.atan2(rendezvousDirection.dot(rise.clone().cross(heading)), rise.dot(heading));
const meetingFrame = new THREE.Quaternion().setFromAxisAngle(rendezvousDirection, twist).multiply(tiltedOrbit);
function cameraOrbitFrame(time) {
  return meetingFrame.clone().slerp(new THREE.Quaternion(), smooth(11, 14, time));
}
export function letterCenter(time) {
  return V(Math.sin(letterAngle(time)) * 205, 18, Math.cos(letterAngle(time)) * 205);
}
function fromCameraOrbitSpace(point, time) {
  return point.clone().applyAxisAngle(V(0, 1, 0), cameraOrbitAngle(time))
    .add(V(Math.sin(cameraOrbitAngle(time)) * 205, 18, Math.cos(cameraOrbitAngle(time)) * 205))
    .applyQuaternion(cameraOrbitFrame(time));
}
function hermiteCurve(start, end, startVelocity, endVelocity, duration) {
  return new THREE.CubicBezierCurve3(start, start.clone().addScaledVector(startVelocity, duration / 3),
    end.clone().addScaledVector(endVelocity, -duration / 3), end);
}
function quinticCurve(start, end, startVelocity, endVelocity, startAcceleration, endAcceleration, duration) {
  const points = [start,
    start.clone().addScaledVector(startVelocity, duration / 5),
    start.clone().addScaledVector(startVelocity, duration * 2 / 5).addScaledVector(startAcceleration, duration ** 2 / 20),
    end.clone().addScaledVector(endVelocity, -duration * 2 / 5).addScaledVector(endAcceleration, duration ** 2 / 20),
    end.clone().addScaledVector(endVelocity, -duration / 5), end];
  return { getPoint(u) {
    const weights = [1, 5, 10, 10, 5, 1];
    return points.reduce((point, control, index) => point.addScaledVector(control,
      weights[index] * u ** index * (1 - u) ** (5 - index)), V(0, 0, 0));
  } };
}
const meetingUp = V(0, 1, 0).applyQuaternion(meetingFrame);
function coastalPose(time) {
  const u = clamp((time - COAST_START) / (COAST_END - COAST_START), 0, 1);
  const position = coastPoint(u);
  const up = position.clone().normalize();
  // Steer along the orbital tangent with a fixed pitch toward the horizon.
  // Looking at nearby shoreline points made the old route yaw and dip.
  const pitch = THREE.MathUtils.degToRad(40);
  const target = position.clone().addScaledVector(coastTangent(u), 100 * Math.cos(pitch))
    .addScaledVector(up, -100 * Math.sin(pitch));
  return { position, target, up, roll: 0 };
}

// "Underneath" means radially between Earth and the N's inward-facing wall.
const entryAim = V(96, -6, -17);
const entry = entryAim.clone().add(V(0, 18, 205)).setLength(COAST_RADIUS).sub(V(0, 18, 205));
const cornerExit = V(112, 8, 29);
const cornerAim = V(86, 4, -2);
const flyout = V(-84, 8, 29);
const flyoutAim = V(-110, 4, -2);
const passageVelocity = V((flyout.x - cornerExit.x) / (11 - CORNER_END), 0, 0);
const corner = hermiteCurve(entry, cornerExit, V(115, 0, 0), passageVelocity, CORNER_END - PULL_UP_END);
const entryDirection = entryAim.clone().sub(entry).normalize();
const cornerDirection = cornerAim.clone().sub(cornerExit).normalize();
const cornerTurn = new THREE.Quaternion().setFromUnitVectors(entryDirection, cornerDirection);
function closePass(time, movement) {
  let local;
  let aim;
  let wave = 0;
  if (time <= CORNER_END) {
    const u = clamp((time - PULL_UP_END) / (CORNER_END - PULL_UP_END), 0, 1);
    local = corner.getPoint(u);
    const turn = smooth(0, 1, u);
    const direction = entryDirection.clone().applyQuaternion(new THREE.Quaternion().slerp(cornerTurn, turn));
    aim = local.clone().addScaledVector(direction,
      THREE.MathUtils.lerp(entry.distanceTo(entryAim), cornerExit.distanceTo(cornerAim), turn));
  } else {
    const u = clamp((time - CORNER_END) / (11 - CORNER_END), 0, 1);
    const envelope = Math.sin(Math.PI * u) ** 2;
    wave = Math.sin(2 * Math.PI * u) * envelope * movement;
    local = cornerExit.clone().lerp(flyout, u);
    local.y += wave * 7;
    local.z += envelope * 4 * movement;
    aim = cornerAim.clone().lerp(flyoutAim, u);
    aim.y += wave * 3;
  }
  return {
    position: fromCameraOrbitSpace(local, time), target: fromCameraOrbitSpace(aim, time),
    up: V(0, 1, 0).applyQuaternion(cameraOrbitFrame(time)), roll: wave * 0.025,
  };
}

const derivativeStep = 0.00001;
function velocity(sample, at, property, backward = false) {
  const delta = backward ? -derivativeStep : derivativeStep;
  return sample(at + delta)[property].sub(sample(at)[property]).divideScalar(delta);
}
function acceleration(sample, at, property, backward = false) {
  const delta = backward ? -0.0001 : 0.0001;
  return sample(at + 2 * delta)[property].add(sample(at)[property])
    .addScaledVector(sample(at + delta)[property], -2).divideScalar(delta ** 2);
}
const coastEntry = coastalPose(COAST_START);
const descent = quinticCurve(V(0, 0, 469), coastEntry.position, V(0, 0, 0),
  velocity(coastalPose, COAST_START, 'position'), V(0, 0, 0),
  acceleration(coastalPose, COAST_START, 'position'), COAST_START);
const descentAim = quinticCurve(V(0, 0, 0), coastEntry.target, V(0, 0, 0),
  velocity(coastalPose, COAST_START, 'target'), V(0, 0, 0),
  acceleration(coastalPose, COAST_START, 'target'), COAST_START);
const descentUp = quinticCurve(V(0, 1, 0), coastEntry.up, V(0, 0, 0),
  velocity(coastalPose, COAST_START, 'up'), V(0, 0, 0),
  acceleration(coastalPose, COAST_START, 'up'), COAST_START);
const coastExit = coastalPose(COAST_END);
const closeEntry = closePass(PULL_UP_END, 0);
const pullUp = quinticCurve(coastExit.position, closeEntry.position,
  velocity(coastalPose, COAST_END, 'position', true),
  velocity((time) => closePass(time, 0), PULL_UP_END, 'position'),
  acceleration(coastalPose, COAST_END, 'position', true),
  acceleration((time) => closePass(time, 0), PULL_UP_END, 'position'), PULL_UP_END - COAST_END);
const viewDirection = ({ position, target }) => ({ direction: target.clone().sub(position).normalize() });
// Interpolate the viewing direction, not a shrinking world-space aim point.
// The latter swept past the camera and caused a last-moment whip upward.
const pullUpDirection = hermiteCurve(viewDirection(coastExit).direction, viewDirection(closeEntry).direction,
  velocity((time) => viewDirection(coastalPose(time)), COAST_END, 'direction', true),
  velocity((time) => viewDirection(closePass(time, 0)), PULL_UP_END, 'direction'), PULL_UP_END - COAST_END);
function trackPose(time, movement = 1) {
  if (time >= PULL_UP_END) return closePass(time, movement);
  if (time >= COAST_END) {
    const u = (time - COAST_END) / (PULL_UP_END - COAST_END);
    const position = pullUp.getPoint(u);
    const distance = THREE.MathUtils.lerp(coastExit.position.distanceTo(coastExit.target),
      closeEntry.position.distanceTo(closeEntry.target), smooth(0, 1, u));
    const target = position.clone().addScaledVector(pullUpDirection.getPoint(u).normalize(), distance);
    return { position, target,
      up: coastExit.up.clone().lerp(meetingUp, smooth(COAST_END, 6.7, time)).normalize(), roll: 0 };
  }
  if (time >= COAST_START) return coastalPose(time);
  const u = time / COAST_START;
  return {
    position: descent.getPoint(u), target: descentAim.getPoint(u),
    up: descentUp.getPoint(u).normalize(), roll: 0,
  };
}

// Route coordinates are real seconds. Shot previews and the full film sample
// the same physical letter orbit without resetting or re-timing it.
export const orbitTimeForRoute = (time) => time;
export const APPROACH_DURATION = 5.9;
function revealedLetterQuaternion(time, angle = letterAngle(time)) {
  return new THREE.Quaternion().setFromAxisAngle(
    V(0, 1, 0), angle * (1 - smooth(11, 14, time)),
  );
}
// Shot 02 travels in the real letter frame. +Z is away from Earth and
// decreasing X follows SNN's orbit. The middle N has one convex bow;
// its endpoints sit just behind the back face so the curve can start turning
// early without clipping the 14-unit spaces between the extruded strokes.
const passKeys = [
  [8, V(125, -12, -38), V(0, 12, 110)],
  [8.35, V(125, -6, 0), V(0, 20, 110)],
  [8.75, V(80, 6, 43), V(-140, 5, 0)],
  [9.15, V(38, 8, 12), V(-5, 0, -140)],
  [9.45, V(36.5, 8, -21), V(-5, 0, -105)],
  [10.35, V(-36.5, 8, -21), V(-5, 0, 105)],
  [10.65, V(-38, 8, 12), V(-5, 0, 140)],
  [11, V(-74, 14, 55), V(-140, 15, 10)],
];
function keyedCurve(keys) {
  const segments = keys.slice(0, -1).map(([time, point, tangent], index) => {
    const [end, next, nextTangent] = keys[index + 1];
    return { time, end, curve: quinticCurve(point, next, tangent, nextTangent, V(0, 0, 0), V(0, 0, 0), end - time) };
  });
  return (time) => {
    const segment = segments.find(({ end }) => time <= end) ?? segments.at(-1);
    return segment.curve.getPoint((time - segment.time) / (segment.end - segment.time));
  };
}
const passPoint = keyedCurve(passKeys);
const directionKeys = [
  [8, V(-0.6, 0.35, 0.72)],
  [8.75, V(-0.95, 0, -0.3)],
  [9.05, V(-1, 0, 0)],
  [9.5, V(-0.95, 0, 0.3)],
  [10, V(-0.95, 0, 0.3)],
  [10.25, V(-1, 0, 0)],
  [10.7, V(-0.9, -0.05, -0.45)],
  [11, V(-0.4, -0.1, -0.91)],
];
const passDirection = keyedCurve(directionKeys.map(([time, direction], index) => {
  const previous = directionKeys[Math.max(0, index - 1)];
  const next = directionKeys[Math.min(directionKeys.length - 1, index + 1)];
  return [time, direction, next[1].clone().sub(previous[1]).divideScalar(next[0] - previous[0])];
}));
function letterPass(time, movement = 1) {
  const local = passPoint(time);
  const u = (time - 8) / 3;
  // The tuning slider adds a small vertical drift without moving either
  // narrow gap corridor or changing the required outside/inside sequence.
  local.y += (movement - 1) * 4 * Math.sin(Math.PI * u) ** 4 * Math.sin(2 * Math.PI * u);
  const orientation = revealedLetterQuaternion(time);
  const position = local.applyQuaternion(orientation).add(letterCenter(time));
  const direction = passDirection(time).normalize().applyQuaternion(orientation);
  return { position, target: position.clone().addScaledVector(direction, 100) };
}
function cylinder(pose, time) {
  const relative = pose.position.clone().applyAxisAngle(V(0, 1, 0), -letterAngle(time));
  return { coordinates: V(Math.atan2(relative.x, relative.z), Math.hypot(relative.x, relative.z), relative.y) };
}
const approachStart = trackPose(APPROACH_DURATION, 0);
const startCylinder = (time) => cylinder(trackPose(time, 0), time);
const endCylinder = (time) => cylinder(letterPass(time), time);
const approachDuration = 8 - APPROACH_DURATION;
const approachOrbit = quinticCurve(startCylinder(APPROACH_DURATION).coordinates, endCylinder(8).coordinates,
  velocity(startCylinder, APPROACH_DURATION, 'coordinates', true), velocity(endCylinder, 8, 'coordinates'),
  acceleration(startCylinder, APPROACH_DURATION, 'coordinates', true), acceleration(endCylinder, 8, 'coordinates'), approachDuration);
function localView(pose, time) {
  return { direction: pose.target.clone().sub(pose.position).normalize().applyAxisAngle(V(0, 1, 0), -letterAngle(time)) };
}
const startView = (time) => localView(trackPose(time, 0), time);
const endView = (time) => localView(letterPass(time), time);
const approachDirection = quinticCurve(startView(APPROACH_DURATION).direction, endView(8).direction,
  velocity(startView, APPROACH_DURATION, 'direction', true), velocity(endView, 8, 'direction'),
  acceleration(startView, APPROACH_DURATION, 'direction', true), acceleration(endView, 8, 'direction'), approachDuration);
const focusDistance = (time) => {
  const pose = trackPose(time, 0);
  return { distance: V(pose.position.distanceTo(pose.target), 0, 0) };
};
const approachFocus = quinticCurve(focusDistance(APPROACH_DURATION).distance, V(100, 0, 0),
  velocity(focusDistance, APPROACH_DURATION, 'distance', true), V(0, 0, 0),
  acceleration(focusDistance, APPROACH_DURATION, 'distance', true), V(0, 0, 0), approachDuration);
function letterApproach(time) {
  const u = (time - APPROACH_DURATION) / approachDuration;
  const coordinates = approachOrbit.getPoint(u);
  const angle = letterAngle(time) + coordinates.x;
  const position = V(Math.sin(angle) * coordinates.y, coordinates.z, Math.cos(angle) * coordinates.y);
  const direction = approachDirection.getPoint(u).normalize().applyAxisAngle(V(0, 1, 0), letterAngle(time));
  const distance = approachFocus.getPoint(u).x;
  return { position, target: position.clone().addScaledVector(direction, distance) };
}
function editedTrack(time, movement = 1) {
  if (time <= APPROACH_DURATION) return trackPose(time, movement);
  if (time < 8) return letterApproach(time);
  return letterPass(time, movement);
}
const retreatEnd = V(0, 95, 560);
const retreatTarget = V(0, 5, 0);
const passExit = letterPass(11);
// Curl back toward Earth just beyond S instead of spending the first half
// of the pullback flying into empty sky. Match position, velocity, and
// acceleration at the bend so the travel-facing camera turns continuously.
const returnTime = 11.45;
const returnPoint = V(195, 40, 155);
const returnVelocity = V(-160, 15, 0);
const exitBend = quinticCurve(passExit.position, returnPoint,
  velocity(letterPass, 11, 'position', true), returnVelocity,
  acceleration(letterPass, 11, 'position', true), V(0, 0, 0), returnTime - 11);
const retreat = quinticCurve(returnPoint, retreatEnd,
  returnVelocity, V(0, 0, 0), V(0, 0, 0), V(0, 0, 0), 14 - returnTime);
const retreatAim = quinticCurve(passExit.target, retreatTarget,
  velocity(letterPass, 11, 'target', true), V(0, 0, 0),
  acceleration(letterPass, 11, 'target', true), V(0, 0, 0), 3);
function revealPose(time) {
  const u = (time - 11) / 3;
  const position = time <= returnTime ? exitBend.getPoint((time - 11) / (returnTime - 11))
    : retreat.getPoint((time - returnTime) / (14 - returnTime));
  return { position, target: retreatAim.getPoint(u) };
}

function authoredCameraPose(time, movement, aspect) {
  let position;
  let target;
  let up = V(0, 1, 0);
  let fov = 42;
  let roll = 0;
  if (time <= 11) {
    ({ position, target } = editedTrack(time, movement));
    if (time <= APPROACH_DURATION) ({ up, roll } = trackPose(time, movement));
    fov = THREE.MathUtils.lerp(0.1, 42, smoother(0, 1.1, time));
    position.sub(target).multiplyScalar(Math.tan(Math.PI * 42 / 360) / Math.tan(Math.PI * fov / 360)).add(target);
    // Keep the original framing aim here: narrow-aspect fitting must not
    // move the camera when its viewing direction changes below.
    position.sub(target).multiplyScalar(1 + (Math.max(1, 1 / aspect) - 1)
      * (1 - smoother(0, COAST_START, time))).add(target);
  } else if (time <= 14) {
    ({ position, target } = revealPose(time));
  } else {
    position = V(0, 95, 560).lerp(V(0, 145, 620), smooth(14, 18, time));
    target = V(0, 5, 0);
  }
  if (aspect < 1.3 && time > 11) {
    // Zero endpoint acceleration keeps travel-facing cameras from jerking
    // when portrait framing starts to widen after the letter pass.
    position.sub(target).multiplyScalar(1 + (1.3 / Math.max(0.3, aspect) - 1) * smoother(11, 14, time)).add(target);
  }
  return { position, target, up, fov, roll };
}

function cameraPose(time, movement = 1, aspect = 1.8) {
  const pose = authoredCameraPose(time, movement, aspect);
  // Settle into the track's heading before entering the letters. At 17s
  // we're only beside S's center; keep looking ahead until its far edge
  // has passed at 17.4s, then settle into the reveal by 18.5s so Earth stays
  // in view as the return bend becomes a wider pullback.
  const following = smoother(APPROACH_DURATION, 7.2, time) * (1 - smoother(11.4, 12.5, time));
  if (following === 0) return pose;
  const step = 0.0001;
  const forward = authoredCameraPose(time + step, movement, aspect).position
    .sub(authoredCameraPose(time - step, movement, aspect).position).normalize();
  const distance = pose.position.distanceTo(pose.target);
  const original = pose.target.clone().sub(pose.position).normalize();
  // World-space velocity includes the orbit and any portrait framing; the
  // tangent in the moving letter frame alone would still look sideways.
  const direction = following === 1 ? forward : original.clone().applyQuaternion(
    new THREE.Quaternion().slerp(new THREE.Quaternion().setFromUnitVectors(original, forward), following),
  );
  pose.target = pose.position.clone().addScaledVector(direction, distance);
  return pose;
}

// Looking upward beneath the N used to align the sightline with camera-up,
// producing a near-instant half-turn. Carry the screen's up direction along
// the changing sightline instead. This rotation-minimizing frame has no pole
// singularity and remains deterministic when a storyboard is scrubbed.
const frameSamples = 1700;
const frameEnd = 14;
const initialStep = (frameEnd - COAST_END) / frameSamples;
const initialFrames = [];
let previousDirection = coastExit.target.clone().sub(coastExit.position).normalize();
let transportedUp = coastExit.up.clone().projectOnPlane(previousDirection).normalize();
for (let index = 0; index <= Math.ceil((APPROACH_DURATION - COAST_END) / initialStep); index += 1) {
  const time = THREE.MathUtils.lerp(COAST_END, frameEnd, index / frameSamples);
  const pose = trackPose(time, 0);
  const direction = pose.target.clone().sub(pose.position).normalize();
  transportedUp.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(previousDirection, direction))
    .projectOnPlane(direction).normalize();
  initialFrames.push(transportedUp.clone());
  previousDirection = direction;
}
function initialUp(time, direction) {
  const index = (time - COAST_END) / (frameEnd - COAST_END) * frameSamples;
  const lower = Math.floor(index);
  return initialFrames[lower].clone().lerp(initialFrames[Math.min(lower + 1, initialFrames.length - 1)], index - lower)
    .projectOnPlane(direction).normalize();
}
const frames = [];
previousDirection = approachStart.target.clone().sub(approachStart.position).normalize();
transportedUp = initialUp(APPROACH_DURATION, previousDirection);
for (let index = 0; index <= frameSamples; index += 1) {
  const time = THREE.MathUtils.lerp(APPROACH_DURATION, frameEnd, index / frameSamples);
  const pose = cameraPose(time);
  const direction = pose.target.clone().sub(pose.position).normalize();
  transportedUp.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(previousDirection, direction))
    .projectOnPlane(direction).normalize();
  frames.push({ up: transportedUp.clone(), direction });
  previousDirection = direction;
}
const lastFrame = frames[frameSamples];
const upright = V(0, 1, 0).projectOnPlane(lastFrame.direction).normalize();
const unwindRoll = Math.atan2(lastFrame.direction.dot(lastFrame.up.clone().cross(upright)), lastFrame.up.dot(upright));
for (let index = 0; index <= frameSamples; index += 1) {
  const time = THREE.MathUtils.lerp(APPROACH_DURATION, frameEnd, index / frameSamples);
  frames[index].up.applyAxisAngle(frames[index].direction, unwindRoll * smooth(11, frameEnd, time));
}
function stableUp(time, direction) {
  if (time <= APPROACH_DURATION) return initialUp(time, direction);
  const index = clamp((time - APPROACH_DURATION) / (frameEnd - APPROACH_DURATION), 0, 1) * frameSamples;
  const lower = Math.floor(index);
  return frames[lower].up.clone().lerp(frames[Math.min(lower + 1, frameSamples)].up, index - lower)
    .projectOnPlane(direction).normalize();
}

export function getOrbitPose(seconds, weave = 1, aspect = 1.8) {
  const t = clamp(seconds, 0, 18);
  const movement = clamp(weave, 0, 1.5);
  const { position, target, fov, roll, up: authoredUp } = cameraPose(t, movement, aspect);
  let up = authoredUp;
  const routeTime = t;
  const direction = target.clone().sub(position).normalize();
  up = routeTime >= COAST_END && routeTime <= frameEnd
    ? stableUp(routeTime, direction) : up.projectOnPlane(direction).normalize();
  const frame = new THREE.Quaternion();
  const angle = letterAngle(routeTime);
  const letterQuaternion = revealedLetterQuaternion(routeTime);
  return { position, target, up, fov, roll, routeTime, angle, frame, letterQuaternion,
    center: letterCenter(t), lettersVisible: t >= LETTERS_ENTER };
}

export function orbitPhase(time) {
  // Tolerate rounding when converting full-film timestamps to orbit seconds.
  if (time < APPROACH_DURATION - 1e-9) return '01 · AROUND THE NORTH PACIFIC';
  if (time < 11) return '02 · BETWEEN THE LETTERS';
  if (time < 14) return '03 · THE BLOCKS READ SNN';
  return '04 · ACROSS THE WORLD';
}
