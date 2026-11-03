export const PROFILE_HOLD_SECONDS = 0.5;
export const ORBIT_SECONDS = 1;
export const OVERHEAD_HOLD_SECONDS = 0.5;
export const TOTAL_SECONDS =
  PROFILE_HOLD_SECONDS + ORBIT_SECONDS + OVERHEAD_HOLD_SECONDS;

/**
 * Sample one complete shot. The caller decides whether and when to replay it.
 * Linear angular progress keeps the camera's speed constant on its circular arc.
 */
export function sampleCameraArc(elapsedSeconds = 0) {
  const time = Math.min(TOTAL_SECONDS, Math.max(0, elapsedSeconds));
  const progress = Math.min(
    1,
    Math.max(0, (time - PROFILE_HOLD_SECONDS) / ORBIT_SECONDS),
  );

  return {
    angleRadians: progress * Math.PI / 2,
    progress,
    phase: time < PROFILE_HOLD_SECONDS
      ? 'profile'
      : time < PROFILE_HOLD_SECONDS + ORBIT_SECONDS
        ? 'orbit'
        : 'overhead',
    finished: time >= TOTAL_SECONDS,
  };
}

/**
 * A quarter-circle in the Y/Z plane, looking toward a fixed target.
 * Rotating camera-up with the arc keeps the overhead pose well-defined: the
 * up vector stays perpendicular to the view direction, including at the pole.
 */
export function orbitPose(angleRadians, target, radius) {
  const sine = Math.sin(angleRadians);
  const cosine = Math.cos(angleRadians);

  return {
    position: {
      x: target.x,
      y: target.y + radius * sine,
      z: target.z + radius * cosine,
    },
    up: { x: 0, y: cosine, z: -sine },
  };
}
