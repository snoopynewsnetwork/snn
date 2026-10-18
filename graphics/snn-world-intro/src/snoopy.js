import * as THREE from 'three';
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';

const INK = '#252221';
const WHITE = '#ffffff';

// Coordinates follow the supplied 294 × 340 reference, with y pointing down.
// Every mark is geometry, including the round ink strokes. No image is used
// in the character. Named groups preserve useful pivots for a later head tilt.
export const contours = {
  tail: [
    ['M', 189, 269], ['C', 203, 272, 231, 275, 245, 284],
    ['C', 236, 294, 214, 294, 196, 281], ['Z'],
  ],
  farFoot: [
    ['M', 151, 280], ['C', 153, 288, 151, 296, 147, 300],
    ['C', 133, 298, 120, 300, 110, 303],
    ['C', 106, 301, 99, 303, 97, 307],
    ['C', 89, 308, 84, 314, 85, 322],
    ['C', 86, 330, 100, 331, 115, 330],
    ['L', 172, 329], ['C', 185, 325, 181, 314, 174, 308],
    ['L', 175, 281], ['Z'],
  ],
  body: [
    ['M', 156, 180], ['C', 157, 192, 146, 201, 141, 211],
    ['C', 132, 226, 126, 243, 128, 259],
    ['C', 129, 273, 137, 281, 151, 284],
    ['C', 165, 288, 185, 287, 195, 276],
    ['C', 203, 267, 198, 252, 193, 239],
    ['C', 188, 222, 179, 207, 176, 192],
    ['L', 176, 178], ['Z'],
  ],
  backPatch: [
    ['M', 190, 233], ['C', 197, 244, 201, 261, 197, 272],
    ['C', 194, 278, 187, 281, 181, 278],
    ['C', 186, 270, 189, 261, 189, 251],
    ['C', 188, 244, 188, 237, 190, 233], ['Z'],
  ],
  nearFoot: [
    ['M', 170, 284], ['C', 169, 291, 169, 299, 167, 305],
    ['C', 155, 302, 139, 302, 128, 306],
    ['C', 121, 304, 113, 308, 111, 312],
    ['C', 103, 312, 96, 317, 97, 323],
    ['C', 96, 330, 111, 332, 126, 331],
    ['C', 153, 331, 181, 331, 207, 329],
    ['C', 216, 329, 221, 326, 218, 322],
    ['C', 213, 316, 200, 311, 187, 308],
    ['C', 184, 303, 184, 291, 185, 283],
  ],
  farToes: [
    [['M', 107, 314], ['C', 101, 315, 99, 319, 99, 324]],
  ],
  nearToes: [
    [['M', 121, 316], ['C', 114, 317, 112, 322, 113, 328]],
    [['M', 140, 320], ['C', 134, 320, 131, 325, 132, 330]],
  ],
  arm: [
    ['M', 169, 231], ['C', 167, 245, 166, 260, 168, 271],
    ['C', 169, 277, 172, 280, 177, 280],
    ['C', 181, 280, 182, 276, 182, 271],
    ['C', 182, 279, 187, 282, 191, 278],
    ['C', 194, 276, 192, 272, 189, 269],
    ['C', 196, 272, 199, 269, 196, 265],
    ['L', 192, 261],
  ],
  nose: [
    ['M', 49, 102], ['C', 41, 100, 32, 106, 27, 112],
    ['C', 22, 118, 23, 128, 29, 132],
    ['C', 36, 138, 46, 128, 53, 125], ['Z'],
  ],
  noseInk: [
    ['M', 44, 113], ['C', 37, 111, 31, 117, 33, 124],
    ['C', 36, 131, 46, 126, 51, 121], ['Z'],
  ],
  hair: [
    ['M', 166, 19], ['C', 166, 10, 161, -1, 154, 7],
  ],
  head: [
    ['M', 155, 180], ['C', 157, 167, 147, 160, 132, 155],
    ['C', 118, 152, 106, 153, 93, 150],
    ['C', 77, 148, 64, 144, 56, 135],
    ['C', 48, 126, 45, 116, 47, 104],
    ['C', 47, 88, 56, 73, 66, 62],
    ['C', 79, 48, 92, 40, 107, 39],
    ['C', 122, 37, 128, 42, 143, 36],
    ['C', 156, 31, 163, 19, 176, 11],
    ['C', 189, 2, 202, 3, 214, 8],
    ['C', 227, 14, 236, 23, 246, 31],
    ['C', 257, 42, 262, 56, 264, 72],
    ['C', 270, 86, 272, 101, 267, 116],
    ['C', 264, 130, 256, 144, 246, 151],
    ['C', 231, 162, 215, 160, 204, 150],
    ['C', 194, 154, 183, 164, 178, 179], ['Z'],
  ],
  eye: [
    ['M', 149, 65], ['C', 147, 68, 149, 75, 149, 81],
    ['C', 150, 83, 152, 82, 152, 80],
    ['C', 151, 75, 152, 69, 149, 65], ['Z'],
  ],
  smile: [
    ['M', 119, 152], ['C', 135, 152, 145, 147, 153, 140],
    ['C', 162, 133, 171, 127, 172, 117],
  ],
  smileDimple: [
    ['M', 173, 113], ['C', 176, 116, 174, 119, 171, 121],
  ],
  earOutline: [
    ['M', 214, 76], ['C', 205, 88, 200, 102, 200, 116],
    ['C', 199, 128, 201, 143, 207, 151],
    ['C', 213, 159, 226, 157, 236, 153],
  ],
  ear: [
    ['M', 240, 61], ['C', 234, 66, 230, 76, 225, 83],
    ['L', 230, 68], ['C', 222, 76, 219, 89, 216, 98],
    ['L', 220, 81], ['C', 211, 95, 207, 112, 209, 126],
    ['C', 209, 136, 212, 146, 219, 147],
    ['C', 226, 148, 230, 143, 236, 141],
    ['C', 247, 134, 252, 122, 255, 110],
    ['C', 259, 98, 258, 84, 253, 76],
    ['L', 252, 88], ['C', 251, 77, 250, 65, 245, 65],
    ['L', 239, 79], ['Z'],
  ],
  earHighlights: [
    [['M', 237, 83], ['C', 233, 90, 231, 98, 229, 104]],
    [['M', 248, 82], ['L', 245, 93]],
  ],
  collar: [
    ['M', 151, 183], ['C', 159, 181, 170, 180, 180, 178],
  ],
};

export function makePath(commands) {
  const path = new THREE.Shape();
  for (const [command, ...points] of commands) {
    if (command === 'M') path.moveTo(...points);
    else if (command === 'L') path.lineTo(...points);
    else if (command === 'C') path.bezierCurveTo(...points);
    else if (command === 'Z') path.closePath();
  }
  return path;
}

export function createSnoopy() {
  const root = new THREE.Group();
  root.name = 'snoopy';
  const drawing = new THREE.Group();
  drawing.name = 'reference-coordinates';
  drawing.position.set(-147, 170, 0);
  drawing.scale.y = -1;
  root.add(drawing);

  const materials = new Map();
  let layer = 0;
  function material(color) {
    if (!materials.has(color)) {
      materials.set(color, new THREE.MeshBasicMaterial({
        color, side: THREE.DoubleSide, depthTest: false, depthWrite: false,
      }));
    }
    return materials.get(color);
  }
  function addMesh(parent, geometry, color, name) {
    const mesh = new THREE.Mesh(geometry, material(color));
    mesh.name = name;
    mesh.renderOrder = layer++;
    parent.add(mesh);
  }
  function mark(parent, name, commands, fill = WHITE, width = 4.5, stroke = INK) {
    const path = makePath(commands);
    if (fill) addMesh(parent, new THREE.ShapeGeometry(path, 24), fill, `${name}-fill`);
    if (width > 0) {
      const geometry = SVGLoader.pointsToStroke(
        path.getPoints(24), SVGLoader.getStrokeStyle(width, stroke, 'round', 'round'), 12,
      );
      if (geometry) addMesh(parent, geometry, stroke, `${name}-stroke`);
    }
  }
  function group(name, parent = drawing) {
    const result = new THREE.Group();
    result.name = name;
    parent.add(result);
    return result;
  }

  const tail = group('tail');
  mark(tail, 'tail', contours.tail);

  const body = group('body');
  mark(body, 'far-foot', contours.farFoot);
  for (const path of contours.farToes) mark(body, 'far-toes', path, null, 3.5);
  mark(body, 'body', contours.body, WHITE, 4.8);
  mark(body, 'back-patch', contours.backPatch, INK, 0);
  mark(body, 'near-foot', contours.nearFoot, WHITE, 4.5);
  for (const path of contours.nearToes) mark(body, 'near-toes', path, null, 3.5);
  mark(body, 'arm-fill', [
    ...contours.arm,
    ['C', 188, 251, 187, 240, 184, 233], ['Z'],
  ], WHITE, 0);
  mark(body, 'arm', contours.arm, null, 4.4);

  const head = group('head-pivot');
  head.position.set(165, 179, 0);
  const headDrawing = group('head-artwork', head);
  headDrawing.position.set(-165, -179, 0);
  const nose = group('nose', headDrawing);
  mark(nose, 'nose', contours.nose, WHITE, 4.1);
  mark(nose, 'nose-ink', contours.noseInk, INK, 0);
  mark(headDrawing, 'hair', contours.hair, null, 3.2);
  mark(headDrawing, 'head', contours.head, WHITE, 4.9);
  mark(headDrawing, 'eye', contours.eye, INK, 4);
  mark(headDrawing, 'smile', contours.smile, null, 3.6);
  mark(headDrawing, 'smile-dimple', contours.smileDimple, null, 4.1);
  const ear = group('ear', headDrawing);
  mark(ear, 'ear-outline', contours.earOutline, null, 4);
  mark(ear, 'ear', contours.ear, INK, 3.3);
  for (const path of contours.earHighlights) mark(ear, 'ear-highlight', path, null, 1.8, WHITE);

  const collar = group('collar');
  mark(collar, 'collar', contours.collar, null, 6.5);

  return {
    root,
    parts: { head, nose, ear, body, tail, collar },
    dispose() {
      root.traverse((object) => object.geometry?.dispose());
      for (const value of materials.values()) value.dispose();
    },
  };
}
