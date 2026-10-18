# SNN World Intro — profile and camera studies

A standalone Three.js study of Snoopy in a flat, left-facing profile, based on
the supplied reference, with a separate volumetric study and an overhead camera
move. The original flat drawing remains available alongside the 3D study.

## Run

Requires Node.js 22.12+ (or a newer supported release) and npm.

```sh
cd graphics/snn-world-intro
npm ci
npm run dev
```

Open the local URL printed by Vite. `npm run check` checks the JavaScript, runs
the camera tests, and builds the production bundle. `npm run preview` serves that bundle locally.
This folder has its own dependencies and does not change the main SNN app.

## Drawing

`src/snoopy.js` constructs the character from editable Bézier paths,
`THREE.ShapeGeometry` fills, and triangulated round strokes. The drawing uses
flat, unlit materials and an orthographic camera. The reference image is only
used by the optional comparison view, never as a texture in the scene.

`createSnoopy()` returns a root group, named parts (`head`, `nose`, `ear`, `body`,
`tail`, `collar`), and a cleanup function. The head has a pivot at the neck.
The coordinates follow the 294 × 340 reference image; the root converts them
to a centered Three.js scene. This original artwork stays planar.

The flat viewer renders on resize or export rather than running an idle animation
loop. It supports three canvas backgrounds and a reference comparison.
**Save PNG** exports just the drawing on transparency at the current canvas
resolution, excluding the viewer labels and selected background.

## 3D camera study

`src/snoopy-3d.js` builds rounded, closed volumes from the profile contours.
The head, torso, ears, nose, feet, and tail have depth; facial strokes follow
their surfaces and use normal depth testing. An orthographic camera and unlit
white materials preserve the drawn appearance from the side. Subtle shading
appears as the camera rises. The 3D reconstruction is an approximation from a
single reference, particularly in the unseen overhead view.

`src/camera-arc.js` defines a two-second shot: 0.5 seconds at profile, a
one-second quarter-circle at constant angular speed, then 0.5 seconds directly
overhead. The camera remains 650 units from a fixed target at the character's
center, moves from +Z to +Y, and looks toward that target. Its up vector rotates
with the path so the overhead pose has no pole flip. The character stays still.

The second panel loops this shot with a cut back to profile. Pause, Replay, and
the timeline slider allow inspection at any angle along the route. Dragging the
3D canvas pauses playback and freely orbits the camera at the same fixed radius,
with zoom and panning disabled. Play and Replay snap back to the start of the
intended profile-to-overhead route. Scrubbing also returns to the scripted route.
Playback starts paused when
reduced motion is requested and suspends while hidden or offscreen. The canvas
background controls apply to both panels.

`npm test` verifies the timing boundaries, angular speed, fixed camera radius,
endpoint, tangent velocity, and camera-up orientation.

## Scope

These studies include Snoopy only. Head animation and the nose-to-globe
transition, Woodstock's entrance and orbit, and the network title are later
steps. The reference is retained in `reference/snoopy-profile.png`.
