# Which World Are You In? v3 — stories in 3D

**Date:** 2026-09-24 · **Deadline:** 2026-09-26 · Builds on v2 (`2026-09-24-which-world-v2-design.md`):
atlas palette, one crowd of 1,024 ink dots, booth behaviour (offline, `?talk`, idle reset,
Space/←/→), tests. Everything below replaces v2's plate list and interaction pattern.

## Intent (user, 2026-09-24)

Every concept told as a story: put the viewer in a character's seat, ask "what would you
do?" with options, play the scenario out, end with **"Moral of the story"**. The viewer
should get fully invested; the art should mesmerise, rendered in three.js. Galton is
dropped; the Shipman plate stays parked.

## Story pattern (every plate)

1. **The seat**: "You are …": two or three lines of scene and stakes, second person.
2. **What would you do?**: 2–4 option buttons (replace sliders).
3. **It plays out**: a 3D scene or the ink crowd animates the consequence; one line
   answers *your* choice.
4. **Moral of the story**: a pull quote under a hairline rule.
5. **Drawn better** (where a plate has one): the camera settles flat and the dots land on
   engraved SVG axes.

Choices are kept for the finale.

## Plates

| # | route | seat | choice | plays out | moral (gist) |
|---|---|---|---|---|---|
| I | `#stadium` | engineer certifying a stand for 1,000 fans; then fundraiser at the gala | reinforce / ban / do nothing; work the crowd / talk to the one person | 3D stadium bowl; heaviest fan adds 0.5%; each fortune a column, the richest person's rises out of sight (to scale: 10 km if $80k is 1 cm); then flat log-scale histogram | in Mediocristan no one moves the total; in Extremistan one person is the total |
| II | `#turkey` | you are the turkey, day 1,000 | relax / stay alert / run | 1,000 fed days spiral up a tower of ink; day 1,001 the path breaks and falls | a thousand calm days are not evidence of safety |
| III | `#graveyard` | Act 1: Abraham Wald, Statistical Research Group, New York, 1943. Act 2: choosing a fund manager | armour wings / fuselage / engines / everywhere; hire the 10-year genius / an index fund / ask how many started | a particle bomber collects hits from returning planes (few on engines); the planes that never came back rise as red ghosts hit in the engines. 1,024 managers as a field of lights going out year by year | the evidence you see was already filtered by what killed the rest |
| IV | `#dino` | analyst whose boss reads only tables | treat the five branches the same / ask for a chart | points orbit in 3D, collapse flat into dinosaur → star → circle → bullseye → X | never trust a summary you haven't seen drawn |
| V | `#funnel` | health minister; front page: "District 177 worst in the country" | send inspectors / sack the board / ask for a funnel plot | 380 bars as a receding skyline; they fly into a flat funnel plot | small places make extreme numbers by chance |
| VI | `#test` | GP; patient asks "how worried should I be?"; then press officer and headline writer | "90%" / "50–50" / "probably not, let's retest"; "5% die" / "95% survive"; "+18% risk" / "6 → 7 in 100" | 1,000 people fall through the test; positives gather; flat grid and box; framing arrays | when something is rare, most alarms are false; the same fact can frighten or reassure |
| VII | `#record` | — | — | your choices replayed, each marked right or wrong and tagged with its world; a verdict | which world you're in, and how you draw it, decide half the answer |

Wald sources: hits per square foot on returning planes, as popularised by Jordan
Ellenberg, *How Not to Be Wrong* (2014): engine 1.11, fuselage 1.73, fuel system 1.55,
rest of the plane 1.80. The particle simulation is illustrative (seeded) and says so.

## Visual system

v2 atlas palette (paper, Prussian ink, madder, one black swan per plate). In 3D:
ink-drop particles with soft edges, depth fading into the paper, hairline props (tiers,
helix, airframe), slow camera drift in story scenes, camera settles flat for charts.
Type unchanged (Iowan Old Style; Avenir Next for buttons).

## Architecture

- `which-world/three.min.js`: three.js r149 classic build (MIT), vendored and loaded with
  `<script src>` so the page still opens from `file://` offline. A deliberate departure
  from the repo's CDN/importmap convention; noted in the README.
- **Ink engine on WebGL:** same API (`to/set/retarget/nudge/pick`, `D` in document px),
  targets gain optional `z`. World = (x, −y, z) in document px. The **flat pose** places a
  perspective camera so z = 0 maps 1:1 to CSS px (follows scroll), making SVG overlays
  line up. **Scene poses** orbit a subject centred on the figure (principal point
  shifted with `setViewOffset`). A per-plate prop group holds scenery, cleared on leave.
- **Story runner:** each plate's `enter()` starts an async script; helpers `say`,
  `choose(options)`, `cont(label)`, `moral(text)`, `sleep`; a run token cancels it on
  leave. Space presses the visible Continue button; it never picks an option.
- Model stays pure and Node-tested; Galton data and its test are removed; new model:
  `bombers(seed)` (hits by zone, returned vs lost).

## Build order

engine + story runner + home → I Stadium → III Bomber (+ managers) → V League → VI Test →
II Turkey → IV Datasaurus → VII Record → docs/TALK. v2 stays on the branch as fallback.

## Verification

Model tests (numbers, bombers: engine-hit share far lower on returners than on all
planes), Playwright walk-through of every plate at 1440×900 and 1280×720, one network
request per file (page + three.min.js), no console errors, idle + `?talk`, reduced motion.
