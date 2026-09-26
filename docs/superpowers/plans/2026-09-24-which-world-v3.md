# Which World Are You In? v3 (stories in 3D) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the v2 atlas into seven second-person story plates rendered with three.js, ending in a "Your record" finale.

**Architecture:** Swap the 2D ink canvas for a WebGL points renderer with the same API plus a camera (flat pose = 1:1 with CSS px for charts; scene poses for stories) and per-plate props. A small async story runner drives each plate. Model stays pure and tested.

**Tech Stack:** HTML/CSS/vanilla JS, three.js r149 classic build (vendored), SVG overlays, Python 3 + Node 20 tests, Playwright.

**Spec:** `docs/superpowers/specs/2026-09-24-which-world-v3-stories.md`

## Global Constraints

- Offline from `file://`: `index.html` + `three.min.js` only; no other requests.
- Routes: `#home #stadium #turkey #graveyard #dino #funnel #test #record`.
- Space presses the visible Continue/primary button only (never an option); ←/→ plates (no modifiers); idle 60 s → `#home` unless `?talk`.
- Palette/type as v2. "Moral of the story" pull quote on every story plate.
- Numbers on screen match sources/model (0.5% / 99.9%; 10 km; 99.9% turkey; Ellenberg's 1.11/1.73/1.55/1.80; 1 of 1,024; Datasaurus table; funnel: rank-1 inside 99.8%, outlier ranked 6th; 9/108 = 8%; 6 → 7 in 100).
- Reduced motion: tweens and camera moves jump to end; no drift.
- README/log updated; tests pass before each commit.

## Review Focus

1. Leaving a plate mid-story (awaiting a choice, mid-sleep, mid-camera move) → the old script never writes to the DOM or the ink again.
2. Flat-pose charts after scrolling or resizing → dots stay on their SVG axes.
3. Space while options are showing → nothing is chosen; while Continue shows → continues exactly once.
4. WebGL point size limits / devicePixelRatio 2 → dots keep their intended size; hover still names the nearest visible dot through the perspective camera.
5. Record plate reached without playing some plates → shows only what was played, no "undefined".

---

### Task 1: Model + data cleanup (TDD)
- Remove Galton: inline `GALTON`, `fetch_galton.py`, `derived/galton_sons.csv`, Galton lines in `test_data.py`/`test_model.mjs`.
- Add `bombers(seed = 5)` → `{ hits: [{zone, u, v, lost}], returned, lost }`: 200 sorties, hits per plane ~ 1 + Poisson(6), each hit on a zone chosen by area (engines 0.12, fuselage 0.30, fuel 0.10, rest 0.48) with (u, v) ∈ [0,1)² for placement; a plane is lost with probability 1 − Π(1 − q_zone) over its hits, q = {engines .35, fuel .12, fuselage .06, rest .03}.
- Tests: returned planes' engine-hit share < 60% of the all-planes engine share; lost planes' engine-hit share > returned; counts add up to 200.
- Commit.

### Task 2: WebGL ink engine + camera + props + story runner + home
- `ink` rebuilt on THREE.Points with a ShaderMaterial (attributes: position, size, color, alpha; soft round ink drop; depth fade to paper). API as v2 plus `ink.pose(p, ms)`, `ink.flat(ms)`, `ink.props()` (group cleared on leave), `ink.project(i)`.
- Story runner: `RUN` token, `say(html)`, `choose(options)`, `cont(label)`, `moral(text)`, `sleep(ms)`; `record` store.
- Home: 3D stadium bowl orbiting slowly behind the title.
- Playwright: home renders, orbit runs, one request for three.min.js, no errors. Commit.

### Task 3: Plate I, the stadium (story)
Engineer beat → weight reveal (share bar) → moral part 1 → fundraiser beat → columns rise, richest column climbs out of frame with camera tilt, "10 km" line → moral → "Draw it on a log scale" (flat pose, v2 log histogram + axis). Commit.

### Task 4: Plate III, the bomber and the managers (story)
Act 1: particle airframe (props) rotating; returned-plane hits accumulate as crowd dots; Ellenberg table in margin; choice; ghost planes with madder engine hits rise; reply to choice; moral. Act 2: 1,024 lights on a ground plane go out year by year; choice before; moral. Commit.

### Task 5: Plate V, the league table (story)
Minister + newspaper clipping; choice; skyline of 380 bars (props lines + crowd dots at tops) with camera fly-by; dots fly into flat funnel (v2 funnel targets + axes); reply; moral. Commit.

### Task 6: Plate VI, the positive test (story)
GP choice; 1,000 dots fall through a plane in 3D, then flat grid + positives box (v2); reply; prevalence slider kept; press-release choice and headline choice drive the v2 framing arrays; moral. Commit.

### Task 7: Plate II, the turkey (story)
Helix of 1,000 fed days with camera riding up; choice on day 1,000; break and fall; moral. Commit.

### Task 8: Plate IV, the Datasaurus (story)
Analyst; table; choice; 3D cloud orbit → collapse flat → morph cycle with tabs; moral. Commit.

### Task 9: Plate VII, your record
Rows of your choices (right/wrong, world tag), verdict line, closing moral, "Start again". Commit.

### Task 10: Docs, talk, verification, review, publish
README (plates, sources incl. Ellenberg, three.js vendoring note), TALK.md (story-led, plates I, III, V + record), root README log/gallery image; tests; Playwright full pass at 1440×900 and 1280×720; fresh whole-branch review; fix pass; push; PR update.
