# SNN World Intro — film review workspace

A Three.js review workspace for a 24-second Snoopy News Network intro.
The page opens with the complete film, followed by six storyboard shots, an
interactive scene editor, and the original Snoopy drawing reference. The older
character, globe, and transition comparison panels are no longer on the page.

## Run

Requires Node.js 22.12+ (or a newer supported release) and npm.

```sh
cd graphics/snn-world-intro
npm ci
npm run dev
```

Open the local URL printed by Vite. `npm run check` checks the JavaScript, runs
the tests, and builds the review bundle. `npm run preview` serves that bundle
locally. The folder is also an npm workspace, so a root `npm ci` installs its
dependencies using the repository lockfile. The local lockfile supports running
this graphics project on its own.

## Site intro

The main site serves `/intro`, a minimal full-screen player with Play/Pause and
Replay. It plays the film once, then holds the final camera, Earth, and SNN pose
while the partial rings continue orbiting indefinitely. Playback follows elapsed
time and is not tied to scrolling. Pausing also stops the rings; Replay starts
again from Snoopy.

From the repository root, `npm run dev` builds the intro and starts the actual
Worker site at `http://localhost:8787/intro`. `npm run build:intro` rebuilds only
the intro client after editing its sources. The root build bundles
`src/intro-page.js` and the shared renderer into the generated, ignored
`public/intro/film.js`. The site HTML and CSS live in `public/intro/`; the
storyboard, editor, and MP4 export controls stay in this review workspace.

Cloudflare CI includes these graphics sources, installs workspace dependencies,
and builds the intro with the rest of the site. The standard deployment includes
it automatically; no separate Vite server or video-export server is needed.

## Complete film and storyboard

The full film begins with the original planar Snoopy drawing, travels through
his black ink into Earth, follows a North Pacific arc, and weaves through the
orbiting SNN letterforms before revealing the word across the globe.

The six cards are ranges of that same continuous film. `src/film-shots.js` defines
their boundaries, titles, and descriptions, shared by the storyboard, timeline,
film captions, and editor labels.

| Shot | Film time | Moment |
| --- | --- | --- |
| 01 | 0–6s | Through the ink |
| 02 | 6–11.9s | Across the Pacific |
| 03 | 11.9–14s | Behind the N |
| 04 | 14–17.4s | Between the letters |
| 05 | 17.4–20s | Back to Earth |
| 06 | 20–24s | Across the world |

Each card begins at its midpoint and has independent Play/Pause, Replay, reverse
scrubbing, and a loop toggle. Loops are enabled for storyboard cards and disabled
for the full film by default. Shot numbers and absolute film timestamps provide
reference points for feedback. Offscreen and hidden previews suspend playback.

The shared tuning controls select the nose, eye, or ear opening; vary camera
weave and ring drift; and change preview playback speed. **Reset settings**
restores the initial tuning. Orbit settings in the scene editor also update every
film preview.

### Camera and scene choreography

**Shot 01** keeps Snoopy entirely 2D. The camera pans and zooms into a verified
solid-ink area, cuts to an unshaded patch of North America, then pulls back to the
globe. Coastlines appear before globe shading gradually returns. The opening and
final globe framing each hold briefly.

**Shot 02** descends toward Earth, finishing at 7.8 seconds, then follows a
steady circular arc from just south of Baja California past Alaska and Russia
toward Japan. The camera remains 180 scene units from Earth's center, 40 units
above its surface. Its heading follows the arc with a fixed 40° downward pitch.

**Shot 03** pulls up behind the trailing N and prepares the close pass. The
camera settles into facing its direction of travel before reaching the letters.
**Shot 04** rounds the outside of the trailing N, crosses inside the middle N,
and returns outside the S. The middle-N pass follows one convex arc, with broad
turns into and out of the letter gaps. The camera looks along its world-space
motion, with a stable screen-up direction, until it has passed the S at 17.4s.

**Shot 05** completes an early return bend toward Earth, matching camera velocity
and acceleration through a waypoint at 17.45s. Earth re-enters the frame around
17.4s, keeping the empty interval after the final letter gap to about 0.8s. The
reveal aim settles by 18.5s, and the camera continues pulling back into the wider
20-second composition. Narrow-frame fitting eases smoothly into that view.
**Shot 06** carries the readable SNN word from right to left across Earth.

SNN and the rings share one fixed equatorial plane throughout the globe sequence.
The letters are present from the beginning, with normal depth occlusion by Earth.
Their angular travel is constant from film time 6–17s, then eases through the
reveal and crossing. The authored starting phase is advanced 32° so the trailing
N sits just beyond the camera's right edge at 11.9s. The editor's phase control
adds an offset to that starting position. The letters turn toward the audience
as they resolve into the closing composition.

## Export MP4

**Export MP4** beneath the complete film renders all 1,440 frames at 1920×1080
and 60 fps, then downloads a 24-second H.264 video. It uses the opening, weave,
ring drift, and orbit settings selected when export starts. The video has an
opaque paper background and excludes editor guides and page labels. Preview
playback speed does not change the exported duration.

Progress and cancellation are available while rendering, with a download link
when the render finishes. Export runs locally with `npm run dev` or
`npm run preview` and requires `ffmpeg` on the server's PATH. Static hosting
supports the review workspace but does not provide the local video encoder.

## Interactive scene editor

Open `/#scene-editor` below the storyboard. Drag to orbit the scene, right-drag
or Shift-drag to pan, and scroll to zoom. The Pan mode button makes ordinary
dragging pan instead. Front, Top, Side, and Reset view provide starting points;
arrow keys pan when the view is focused.

**Match film camera** pauses playback and moves the editor view to the film
camera at the selected timestamp, including its angle, roll, and lens. The view
remains free to orbit, pan, and zoom from there. Reset view restores the overview.

The gold circle shows SNN's orbital plane and radius. Radius, tilt, heading,
starting phase, and orbit-speed controls update all film previews and persist in
this browser. Reset orbit restores the authored choreography; Export settings
downloads the current values as JSON. Orbit edits keep the camera track fixed so
alignment can be inspected directly.

The colored camera path shows actual positions, from teal for slower motion to
coral for faster motion, with a dot every half second. Click the path, speed
graph, or timeline to scrub. Play runs the 6–24s globe sequence. The camera
frustum indicates its viewing direction, and the inset renders the film camera.
The graph and readouts measure camera and SNN-center speeds in scene units per
second.

The editor timeline starts at the globe handoff at 6s. Its path and speed plot
begin at 7.1s so the distant opening lens blend does not dwarf the scene. Ghost
Earth affects only the overview, not the film.

## Drawing reference

The collapsed **Drawing reference** section retains the original flat Snoopy
viewer and the supplied image. It includes three canvas backgrounds, a reference
comparison, and **Save PNG**. PNG export contains the drawing on transparency at
the current canvas resolution, without viewer labels or the selected background.
The viewer renders on resize or export instead of running an idle animation loop.

`src/snoopy.js` builds the drawing from editable Bézier paths, `THREE.ShapeGeometry`
fills, and triangulated round strokes, using flat materials and an orthographic
camera. Its coordinates follow the 294 × 340 reference image and are converted
to a centered Three.js scene. `createSnoopy()` returns the root, named parts, and
a cleanup function. The reference image is a comparison aid, never a texture in
the film; it remains in `reference/snoopy-profile.png`.

## Rendering and source layout

- `src/film-shots.js` holds the shared six-shot breakdown.
- `src/orbit-film-views.js` creates the full-film player and storyboard cards.
  All seven panels share one WebGL renderer and copy frames into separate canvases.
- `src/orbit-film.js` combines the flat opening, globe, letters, and rings.
- `src/orbit-flight.js` defines the camera paths, viewing direction, and timed
  letter orbit. Every pose is a function of time, supporting reversible scrubbing
  and later scroll-driven playback.
- `src/transition-flat.js` implements the nose, eye, and ear opening variants.
- `src/orbit-ink-assets.js` builds the block-letter silhouettes, ink contours,
  paper faces, side hatching, and three independently sliding partial ring bands.
- `src/globe.js` and `src/globe-projection.js` provide Earth geometry, coastline
  rendering, and coordinate mapping. Black continents occlude the light grid;
  the opaque sphere hides the far side.
- `src/orbit-editor.js` provides the free scene view and timeline controls;
  `src/orbit-editor-state.js` persists orbit settings.

Earlier standalone exploration modules and their tests remain in the repository,
but the current page no longer starts those viewers. Tests cover the opening
handoff, geographic orientation, camera continuity and travel-facing direction,
letter clearance, visibility through the exit, reversible scrubbing, ring motion,
readable SNN crossing, shared shot boundaries, and MP4 encoding.

Coastlines are bundled from the pinned
[`world-atlas` land-110m dataset](https://github.com/topojson/world-atlas), derived
from Natural Earth. [Natural Earth data is public domain](https://www.naturalearthdata.com/about/terms-of-use/);
the redistribution package is ISC licensed. The viewer makes no map-data network
requests at runtime.

## Scope

The SNN letters are draft, handbuilt block forms. Woodstock's entrance, the
finished network title treatment, and the final scroll-driven sequence remain
later steps.
