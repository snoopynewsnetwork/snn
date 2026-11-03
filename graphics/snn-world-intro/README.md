# SNN World Intro — character and globe studies

A standalone Three.js study of Snoopy in a flat, left-facing profile, based on
the supplied reference, with a separate volumetric study and an overhead camera
move. The original flat drawing remains available alongside the 3D study.
Below them, two rows of globe studies show a matching flat and spherical Earth,
first with light land fills and then with black continents.

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
**Reset camera** returns to the initial side profile and pauses playback.
Playback starts paused when
reduced motion is requested and suspends while hidden or offscreen. The canvas
background controls apply to all seventeen panels.

`npm test` verifies the timing boundaries, angular speed, fixed camera radius,
endpoint, tangent velocity, and camera-up orientation, including manual orbit.

## Globe studies

`src/globe.js` renders a flat canvas globe and a true Three.js sphere. Both use
the same Natural Earth 1:110m coastlines, dark rounded ink strokes, and white ocean.
The first globe row uses a very light warm land fill; the separate **The world
in black.** row repeats both views with black continents. There are no country
borders. Each spherical view has its own orbit, grid toggle, and reset controls.

The flat view is an orthographic projection centered at 100°W, 10°N. Spherical
clipping limits the drawing to the visible hemisphere, keeping North and South
America readable. Hawaii is omitted from both flat studies and retained in both
3D globes. The 3D camera starts at 115°W, 12°N: the eastern Pacific lies
in the foreground, with North America above and South America near the right
limb. Most of Europe and Asia are behind the sphere. Drag to orbit at a fixed
distance; **Reset camera** restores this composition. **Grid lines** toggles
latitude circles spaced 15° apart and meridians spaced 22.5° apart. In both 3D
views, the grid is painted beneath the continents, so its light strokes appear
only over the ocean. Toggling the grid preserves the camera position. The sphere
uses subtle shading and an opaque surface so the far side stays hidden.

The view definitions and coordinate mapping live in `src/globe-projection.js`.
Tests verify hemisphere clipping, projected orientation, matching sphere UVs,
and which geographic locations are visible in the intended composition.

Coastlines are bundled from the pinned
[`world-atlas` land-110m dataset](https://github.com/topojson/world-atlas), derived
from Natural Earth. [Natural Earth data is public domain](https://www.naturalearthdata.com/about/terms-of-use/);
the redistribution package is ISC licensed. The viewer makes no map-data network
requests at runtime.

## Transition prototypes

The first transition row compares three six-second transitions, each starting with the
profile and finishing on the same black-continent globe:

- **The head becomes the world:** Snoopy stays upright and still while the
  camera arcs from his side to his front. The head then rounds into a sphere,
  followed by an ink-to-geography handoff before the camera pulls back.
- **Through the nose:** a close push into the actual black nose conceals a
  cut to inland North America, followed by a retreat to the whole globe.
- **The drawing becomes a globe:** a contour becomes a circle, sweeping
  strokes construct a wire globe, and the continents settle into place.

**Play all** starts them together. Each also has Play/Pause, Replay, and a
timeline slider. Playback stops at the final frame. There is no automatic
playback, and offscreen or hidden previews suspend their animation work.
Every pose is determined by normalized progress, allowing reverse scrubbing
and later scroll-driven playback without simulation state.

`src/transition-stage.js` creates separate instances of the existing models
with a head pivot. The three `transition-*.js` scene modules own their motion;
`src/transition-views.js` owns the shared player. These are motion sketches for
comparing handoffs, using the current approximate character reconstruction.

The **Flat drawing. Whole world.** row compares three six-second versions
using the original planar drawing: a push through the **nose**, **eye**, or
**ear**, followed by a pullback from North America to the same 3D globe.
Snoopy stays entirely 2D; the framing pans and zooms into his black ink to
conceal the transition. This row has its own **Play all** control, as well as
individual playback and scrubbing controls. The earlier studies remain above
for comparison.

`src/transition-flat.js` shares the motion between these three flat studies.
The zoom accelerates into a verified solid-ink area, then cuts to an unshaded
patch of land. Coastlines appear as the framing pulls back; globe shading
returns gradually afterward. The opening and final frames each hold for about
half a second. Tests check planar geometry, solid coverage on both sides of
the cut, reverse scrubbing, and the common final globe view.

## Globe and SNN film

**Beyond the horizon.** extends the chosen flat opening into a 24-second film:
six seconds from Snoopy to Earth, followed by eighteen seconds around the globe
and through the SNN letterforms. The four storyboard cards show ranges of this
same film, preserving the camera and scene continuity:

| Shot | Film time | Moment |
| --- | --- | --- |
| 01 | 06–11.9s | Around the North Pacific |
| 02 | 11.9–17s | Between the letters |
| 03 | 17–20s | The blocks read SNN |
| 04 | 20–24s | Across the world |

Shot 01 descends quickly toward Earth, then bends gently into a long, smooth
North Pacific arc beginning just south of Baja California, Mexico. The broad
route passes Alaska and Russia toward Japan. The camera’s heading stays tangent
to the circular arc with a fixed 40° downward pitch, at 180 scene units from
Earth’s center, 40 units above its surface.

SNN and the rings share one fixed equatorial plane throughout the globe
sequence, matching the closing composition at 20 seconds and later. The letters
are present from the start of the globe sequence, with ordinary depth occlusion
by Earth. SNN's existing angular pace is retained: constant through the first
two shots, then easing through the closing reveal and crossing.
The starting position is advanced 32° along that orbit so the trailing N,
including its ink outline, sits just beyond the film camera's right edge at
11.9 seconds. Earlier visibility during the zoom is allowed. The editor's
phase control applies an additional offset to this authored starting position.

Shot 02 pulls up behind the trailing N, curves around its outside away from
Earth, then weaves to the inside of the middle N and the outside of the S.
The inner pass follows one convex arc, with broad turns into and out of the
letter gaps instead of shallow bends that fold back on themselves.
The camera loosely follows the word’s orbit while maintaining a stable
screen-up direction. SNN’s orbit is unchanged, and the letters may be readable
before the later pullback.

The descent completes at film time 7.8 seconds, settling into a steady cruise
through 11.8 seconds before the letter passage begins at 11.9 seconds.
The joins match camera position and velocity, with matching acceleration as
the descent meets the cruise. Shot 01 lasts 5.9 seconds and Shot 02 lasts
5.1 seconds; the complete film remains 24 seconds.

Each card begins at its midpoint and has independent playback, reverse
scrubbing, and a loop toggle. Loops are enabled for storyboard cards and
disabled for the full film by default. Shot numbers and source timestamps
provide reference points for feedback.

**Export MP4** beneath the complete film renders all 1,440 frames at
1920×1080 and 60 fps, then downloads a 24-second H.264 video. It uses the
opening, weave, ring drift, and orbit settings selected when export starts.
The video has an opaque paper background and no editor guides or page labels;
preview playback speed does not change its duration. Progress and cancellation
are available while rendering. The download link remains available afterward.
Export runs locally with `npm run dev` (or `npm run preview`) and requires
`ffmpeg` on the server's PATH. Static hosting still supports the studies but
does not provide the local video encoder.

The shared tuning controls select the nose, eye, or ear opening; vary camera
weave and ring drift; and change playback speed. **Reset settings** restores
the initial tuning. The SNN letters are draft, handbuilt block forms intended
to explore the reveal and camera motion before choosing the final lettering.

`src/orbit-flight.js` holds the editable camera paths and timed
letter orbit. The lens moves from the opening's flat projection into perspective,
tracks closely along the extruded faces in one direction, and retreats as the word
crosses in front of Earth. `src/orbit-ink-assets.js` builds the ink contours,
paper faces, side hatching, and three independently sliding partial ring bands.
`src/orbit-film.js` composes the opening and orbital scene; every state is a
function of time, so the same sequence can later be driven by scroll position.

The five film panels share one WebGL renderer and copy their frames to separate
canvases. Tests cover globe handoff, camera continuity, forward motion and
letter clearance at every weave setting, reversible scrubbing, ring movement, and
the readable right-to-left SNN crossing.

## Interactive scene editor

Open `/#scene-editor` below the storyboards. The scene view is a free camera:
drag to orbit, right-drag or Shift-drag to pan, and scroll to zoom. The Pan mode
button makes ordinary dragging pan instead. Front, Top, Side, and Reset view
provide useful starting points; arrow keys pan when the view is focused.
**Match film camera** pauses playback and moves the editor view to the film
camera at the selected timestamp, including its angle, roll, and lens. Drag,
pan, or zoom to explore from there; Reset view restores the overview. The editor
keeps its own viewport proportions.

The gold circle shows SNN's orbital plane and radius at the current film time.
Use the radius, tilt, heading, starting phase, and orbit-speed controls to adjust
it. Changes update all film previews and persist in this browser. Reset orbit
restores the original choreography; Export settings downloads the current values
as JSON. The default orbital plane stays level throughout the film; a tilt or
heading edit applies consistently to the whole orbit.

The colored camera path shows actual camera positions, from teal (slower) to
coral (faster), with a dot every half second. Click the path, speed graph, or
timeline to scrub. Play runs the 6–24s orbital sequence at normal speed. The
camera frustum shows its viewing direction, and the inset always renders the
actual film camera. The graph and readouts measure physical camera and SNN
center speeds in scene units per second.

The distant opening lens blend is visible in the inset and timeline, but the
overview path and speed plot begin at 7.1 seconds so that the near-orthographic
opening does not dwarf the rest of the scene. Ghost Earth is an overview aid
and does not change the film. The camera track stays fixed
while editing the orbit, making it possible to inspect the alignment directly.

## Scope

The character studies include Snoopy only. Woodstock's entrance, the finished
network title treatment, and the final scroll sequence are later steps.
The reference is retained in `reference/snoopy-profile.png`.
