import { geoOrthographic } from 'd3-geo';
import { Vector3 } from 'three';

export const FLAT_VIEW = { longitude: -100, latitude: 10 };
export const SPHERE_VIEW = { longitude: -115, latitude: 12 };

/**
 * Geographic coordinates on a Three.js sphere, with north along positive Y.
 * This matches SphereGeometry's default UVs for a texture spanning −180° to 180°.
 */
export function geoVector(longitude, latitude, radius = 1) {
  const longitudeRadians = longitude * Math.PI / 180;
  const latitudeRadians = latitude * Math.PI / 180;
  const horizontalRadius = radius * Math.cos(latitudeRadians);

  return new Vector3(
    horizontalRadius * Math.cos(longitudeRadians),
    radius * Math.sin(latitudeRadians),
    -horizontalRadius * Math.sin(longitudeRadians),
  );
}

/** Orthographic geographic projection with the far hemisphere clipped away. */
export function createFlatProjection(radius, center = [0, 0]) {
  return geoOrthographic()
    .rotate([-FLAT_VIEW.longitude, -FLAT_VIEW.latitude])
    .clipAngle(90)
    .scale(radius)
    .translate(center);
}

/**
 * Coastlines as lines rather than filled polygons: projection clipping must
 * never add a stroked closing edge at the texture's antimeridian seam.
 */
export function coastlineGeometry(land) {
  const coordinates = [];
  const onAntimeridian = ([longitude]) => Math.abs(Math.abs(longitude) - 180) < 1e-8;

  function addRing(ring) {
    if (ring.length < 2) return;
    let line = [ring[0]];
    for (let index = 1; index < ring.length; index += 1) {
      const previous = ring[index - 1];
      const point = ring[index];
      // Some source polygons are already split at ±180°. Their closing seam
      // is a map boundary, not a physical coastline on the globe.
      if (onAntimeridian(previous) && onAntimeridian(point)) {
        if (line.length > 1) coordinates.push(line);
        line = [point];
      } else {
        line.push(point);
      }
    }
    if (line.length > 1) coordinates.push(line);
  }

  function visit(object) {
    if (!object) return;
    if (object.type === 'FeatureCollection') object.features.forEach(visit);
    else if (object.type === 'Feature') visit(object.geometry);
    else if (object.type === 'Polygon') object.coordinates.forEach(addRing);
    else if (object.type === 'MultiPolygon') {
      object.coordinates.forEach((polygon) => polygon.forEach(addRing));
    }
  }

  visit(land);
  return { type: 'MultiLineString', coordinates };
}
