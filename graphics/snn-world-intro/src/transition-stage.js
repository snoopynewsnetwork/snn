import * as THREE from 'three';
import { createSnoopy3D } from './snoopy-3d.js';
import { createGlobe } from './globe.js';

export function createTransitionStage(renderer) {
  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-215, 215, 215, -215, 0.1, 4000);
  const snoopy = createSnoopy3D();
  scene.add(snoopy.root);

  // The reference remains untouched; only these prototype instances get a rig.
  const headIndex = snoopy.root.children.findIndex((child) => child.name === 'head');
  const headChildren = snoopy.root.children.slice(headIndex).filter((child) => child.name !== 'collar');
  const headPivot = new THREE.Group();
  headPivot.name = 'prototype-head-pivot';
  headPivot.position.set(18, -9, 0);
  snoopy.root.add(headPivot);
  snoopy.root.updateMatrixWorld(true);
  for (const child of headChildren) headPivot.attach(child);

  const globe = createGlobe(renderer);
  globe.root.visible = false;
  scene.add(globe.root);

  function opacitySetter(root) {
    const materials = new Set();
    root.traverse((object) => {
      if (object.material) {
        for (const material of [].concat(object.material)) materials.add(material);
      }
    });
    return (value) => {
      const alpha = THREE.MathUtils.clamp(value, 0, 1);
      root.visible = alpha > 0.0001;
      for (const material of materials) {
        const transparent = alpha < 1;
        if (material.transparent !== transparent) {
          material.transparent = transparent;
          material.needsUpdate = true;
        }
        material.opacity = alpha;
      }
    };
  }

  const direction = new THREE.Vector3();
  const target = new THREE.Vector3();
  function setCamera(targetArray, directionArray, viewHeight, aspect) {
    direction.fromArray(directionArray).normalize();
    target.fromArray(targetArray);
    camera.position.copy(target).addScaledVector(direction, 650);
    camera.up.set(0, 1, 0).addScaledVector(direction, -direction.y);
    if (camera.up.lengthSq() < 1e-8) camera.up.set(0, 0, -1);
    camera.up.normalize();
    camera.lookAt(target);
    camera.left = -viewHeight * aspect / 2;
    camera.right = viewHeight * aspect / 2;
    camera.top = viewHeight / 2;
    camera.bottom = -viewHeight / 2;
    camera.updateProjectionMatrix();
  }

  return {
    scene, camera, snoopy, headPivot, globe, setCamera,
    setSnoopyOpacity: opacitySetter(snoopy.root),
    setGlobeOpacity: opacitySetter(globe.root),
    dispose() { snoopy.dispose(); globe.dispose(); },
  };
}
