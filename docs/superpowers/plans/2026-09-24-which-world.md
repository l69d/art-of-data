# Which World Are You In? Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A single-file, offline, walk-up exhibit (`which-world/index.html`) of four guess-then-reveal rooms contrasting Mediocristan and Extremistan.

**Architecture:** One self-contained HTML file. A pure `<script id="model">` block holds all numbers/maths (seeded RNG, crowd, screening, regression, turkey) and is unit-tested from Node by extracting that block. A second `<script>` holds the UI: hash router, one render function per room, canvas for dense dot fields, SVG for axes/bars. Galton data is fetched once by a Python script to `derived/` and inlined into the HTML.

**Tech Stack:** HTML + CSS + vanilla JS (canvas 2D + SVG), Python 3 stdlib (fetch/test), Node 20 (`node:test`, `node:assert`) for the model test, Playwright MCP for visual verification.

**Spec:** `docs/superpowers/specs/2026-09-24-which-world-design.md`

## Global Constraints

- Zero external requests: no CDN, no web fonts; must work from `file://` with the network off.
- One self-contained `which-world/index.html` with its own `<!doctype html>` and meta tags (repo CLAUDE.md).
- Rooms hash-routed: `#home`, `#stadium`, `#turkey`, `#test`, `#shipman`.
- Keyboard: ←/→ move between rooms, Space triggers the current room's primary action.
- Idle 60 s → reset to `#home`; disabled when URL has `?talk`.
- Laptop-first 1280–1920 wide, projector-legible; no horizontal scroll at 390 px.
- On-screen numbers match the books: 0.5% / 99.9%; slope 0.45; 9 of 108 = 8%; ~1,300 false alarms; 1984, 105 vs 59.2.
- Palette: bg `#0e1424`, surface `#161e33`, ink `#eef1f7`, ink-2 `#a9b3c7`, Mediocristan `#3987e5`, Extremistan `#d95926`, guess `#ffffff`.
- Type: display `"Avenir Next Condensed", "Arial Narrow", sans-serif`; body `"Iowan Old Style", Charter, Georgia, serif`.
- Respect `prefers-reduced-motion` (animations jump to end state).
- Every data/viz change updates `which-world/README.md` and the root README Log (repo CLAUDE.md).

## Review Focus

1. Guess at the slider extremes (0% / 100%) → guess marker stays inside the bar and the verdict copy still reads sensibly.
2. Reveal pressed twice, or room left mid-animation → no stacked animations; leaving a room cancels its `requestAnimationFrame`.
3. Window resize / projector switch mid-room → canvases redraw crisp at the new size and `devicePixelRatio`.
4. Prevalence slider at its ends (0.1% and 50%) → PPV stays a finite number; with 0 positives it shows "no positives" not NaN.
5. Space pressed while a slider has focus → reveals, doesn't nudge the slider or scroll the page.

---

### Task 1: Galton data + repo hygiene

**Files:**
- Modify: `.gitignore` (add `.claude/`)
- Create: `which-world/fetch_galton.py`, `which-world/test_galton.py`, `which-world/derived/galton_sons.csv`

**Interfaces:**
- Produces: `which-world/derived/galton_sons.csv` with header `father,son` (inches, one row per son, 481 rows).

- [ ] **Step 1: Write the failing test** — `which-world/test_galton.py`

```python
import csv, statistics as s
from pathlib import Path

rows = list(csv.DictReader(open(Path(__file__).parent / "derived/galton_sons.csv")))
f = [float(r["father"]) for r in rows]
c = [float(r["son"]) for r in rows]
assert len(rows) == 481, len(rows)
assert abs(s.linear_regression(f, c).slope - 0.45) < 0.01
assert abs(s.correlation(f, c) - 0.39) < 0.01
print("ok", len(rows))
```

- [ ] **Step 2: Run it** — `python3 which-world/test_galton.py` → FAIL (`FileNotFoundError`).
- [ ] **Step 3: Implement** — `which-world/fetch_galton.py`

```python
"""Galton's 1886 family heights (HistData::GaltonFamilies via Rdatasets) -> sons only."""
import csv, io, urllib.request
from pathlib import Path

URL = "https://vincentarelbundock.github.io/Rdatasets/csv/HistData/GaltonFamilies.csv"
out = Path(__file__).parent / "derived/galton_sons.csv"
out.parent.mkdir(exist_ok=True)
rows = csv.DictReader(io.StringIO(urllib.request.urlopen(URL).read().decode()))
with open(out, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["father", "son"])
    for r in rows:
        if r["gender"] == "male":
            w.writerow([r["father"], r["childHeight"]])
print("wrote", out)
```

- [ ] **Step 4:** `python3 which-world/fetch_galton.py && python3 which-world/test_galton.py` → `ok 481`.
- [ ] **Step 5: Commit** — `git add .gitignore which-world && git commit -m "which-world: Galton sons data + test"`

### Task 2: Page shell + tested model

**Files:**
- Create: `which-world/index.html`, `which-world/test_model.mjs`

**Interfaces:**
- Produces (globals in `<script id="model">`): `CROWD=1000`, `HEAVIEST_KG=400`, `RICHEST_USD=80e9`, `rng(seed)→()=>[0,1)`, `gauss(r)`, `crowd(seed=7)→{weight:number[], wealth:number[]}`, `sum(a)`, `share(extra, arr)→fraction`, `screen(n, prev, sens=.9, spec=.9)→{ill,well,tp,fp,pos,ppv}`, `fit(xs, ys)→{slope,intercept,r,mx,my}`, `turkey(days=1000)→{weight:number[], confidence:number[]}`, `GALTON: [father,son][]`.
- Produces (UI): `go(hash)`, `rooms = {home, stadium, turkey, test, shipman}` each `{enter(el), leave(), primary()}`; `onRaf(fn)` helper whose frames are cancelled by `leave()`.

- [ ] **Step 1: Write the failing test** — `which-world/test_model.mjs`

```js
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const src = html.match(/<script id="model">([\s\S]*?)<\/script>/)[1];
const m = new Function(src + "; return {crowd, share, screen, fit, turkey, GALTON, HEAVIEST_KG, RICHEST_USD};")();

const c = m.crowd();
assert.equal(c.weight.length, 1000);
const w = m.share(m.HEAVIEST_KG, c.weight);
assert.ok(w > 0.004 && w < 0.006, `weight share ${w}`);
assert.equal((m.share(m.RICHEST_USD, c.wealth) * 100).toFixed(1), "99.9");

const s = m.screen(1000, 0.01);
assert.deepEqual([s.ill, s.tp, s.fp, s.pos], [10, 9, 99, 108]);
assert.equal(Math.round(s.ppv * 100), 8);
assert.ok(Number.isFinite(m.screen(1000, 0.001).ppv) && Number.isFinite(m.screen(1000, 0.5).ppv));

const csv = readFileSync(new URL("./derived/galton_sons.csv", import.meta.url), "utf8").trim().split("\n").slice(1);
assert.equal(m.GALTON.length, csv.length, "inlined Galton data out of sync with CSV");
const g = m.fit(m.GALTON.map(p => p[0]), m.GALTON.map(p => p[1]));
assert.ok(Math.abs(g.slope - 0.45) < 0.01 && Math.abs(g.r - 0.39) < 0.01);

const t = m.turkey();
assert.equal(t.confidence.length, 1000);
assert.ok(t.confidence[999] > 0.99 && t.confidence[0] < 0.7);
console.log("model ok");
```

- [ ] **Step 2: Run** — `node which-world/test_model.mjs` → FAIL (ENOENT index.html).
- [ ] **Step 3: Implement** the shell: tokens from Global Constraints on `:root`; `<main>` with one `<section class="room" data-room>` per room; bottom rail of 4 room buttons (rooms are a real sequence, so numbered 1–4); landing with title "Which world are you in?", premise line "Your gut is a statistician trained in the wrong world.", and a "Start" button → `#stadium`. The model block:

```js
const CROWD = 1000, HEAVIEST_KG = 400, RICHEST_USD = 80e9;
function rng(seed) { return () => { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function gauss(r) { let u = 0; while (!u) u = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * r()); }
const sum = a => a.reduce((x, y) => x + y, 0);
function crowd(seed = 7) {
  const r = rng(seed), weight = [], wealth = [];
  for (let i = 0; i < CROWD; i++) { weight.push(Math.min(160, Math.max(45, 80 + 15 * gauss(r)))); wealth.push(Math.exp(gauss(r))); }
  const k = 80e6 / sum(wealth); // Taleb's stadium: the 1,000 together hold ~$80M
  return { weight, wealth: wealth.map(w => w * k) };
}
const share = (extra, arr) => extra / (extra + sum(arr));
function screen(n, prev, sens = 0.9, spec = 0.9) {
  const ill = Math.round(n * prev), well = n - ill, tp = Math.round(ill * sens), fp = Math.round(well * (1 - spec));
  return { ill, well, tp, fp, pos: tp + fp, ppv: tp + fp ? tp / (tp + fp) : 0 };
}
function fit(xs, ys) {
  const n = xs.length, mx = sum(xs) / n, my = sum(ys) / n; let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) { const dx = xs[i] - mx, dy = ys[i] - my; sxy += dx * dy; sxx += dx * dx; syy += dy * dy; }
  const slope = sxy / sxx; return { slope, intercept: my - slope * mx, r: sxy / Math.sqrt(sxx * syy), mx, my };
}
// Laplace's rule of succession: after d safe days, P(safe tomorrow) = (d+1)/(d+2)
function turkey(days = 1000) {
  const weight = [], confidence = [];
  for (let d = 1; d <= days; d++) { weight.push(5 + 15 * (1 - Math.exp(-d / 250))); confidence.push((d + 1) / (d + 2)); }
  return { weight, confidence };
}
const GALTON = [/* generated from derived/galton_sons.csv: [[78.5,73.2], ...] */];
```

  Inline `GALTON` with: `python3 -c "import csv;print('const GALTON = '+str([[float(r['father']),float(r['son'])] for r in csv.DictReader(open('which-world/derived/galton_sons.csv'))]).replace(' ','')+';')"`.
  UI script: router on `hashchange` calling `leave()` on the old room and `enter()` on the new; keydown (←/→ = prev/next room, Space = `preventDefault()` + `primary()`, also when a slider is focused); idle timer (seconds = `?idle=N` URL param, default 60) reset on `pointermove/keydown/pointerdown`, skipped if `location.search.includes("talk")`; `onRaf` helper; `ResizeObserver` on each canvas re-rendering at `devicePixelRatio`.
- [ ] **Step 4: Run** — `node which-world/test_model.mjs` → `model ok`. Open in Playwright: landing renders, `#stadium` etc. switch, no console errors.
- [ ] **Step 5: Commit** — `git commit -am "which-world: page shell + tested model"` (add new files).

### Task 3: Room 1 — The Stadium (flagship)

**Files:** Modify `which-world/index.html` (stadium section + `rooms.stadium`).

**Interfaces:** Consumes `crowd, share, sum, HEAVIEST_KG, RICHEST_USD, onRaf`.

Behaviour:
1. Enter: canvas draws 1,000 dots on concentric ellipses (stands ring, empty oval pitch). Dot area ∝ value / mean value, base radius `r0 = 3.2px` scaled to viewport. Copy: "1,000 random people fill a stadium."
2. Round A (weight): question "The heaviest person on Earth walks onto the pitch. What share of the stadium's total weight is theirs?" Range slider 0–100 % (step 0.1, shows value) + "Reveal" button (primary). Reveal: a 400 kg dot grows at pitch centre to `r0·√(400/mean)`; below, a full-width share bar (SVG) split into 1,000 slivers plus the newcomer in Extremistan orange at its true width, a white tick at the visitor's guess, big condensed number "0.5%" and verdict line (e.g. "You guessed 12%. Real answer: 0.5%.").
3. Round B (wealth): button "Now try wealth". Dots re-size to wealth (log-normal spread visible). Question: "Now the richest person on Earth walks on. Share of the stadium's total wealth?" Reveal: the pitch dot grows over 2.5 s (ease-out) to `r0·√(RICHEST_USD/mean)` — far past the viewport, turning the screen orange; then the share bar fills to 99.9% with the guess tick; number "99.9%".
4. Recap badges: "Weight lives in Mediocristan. Wealth lives in Extremistan." + source line "Taleb, *The Black Swan*, ch. 3 (figures as published, 2007)". Button "Next room".
5. Hover a stand dot → tooltip "Person 412 · 78 kg" / "· $41,000"; pitch dot → "Heaviest human imaginable · 400 kg" / "Richest person · $80 bn".

- [ ] **Step 1:** Implement per above; the reveal number is computed from `share()`, never hard-coded.
- [ ] **Step 2: Verify** — `node which-world/test_model.mjs` passes; Playwright: set slider to 0 and 100, reveal both rounds, screenshot 1440×900 + 390×844; tick stays in bar; press Reveal twice → one animation; resize mid-room → crisp redraw.
- [ ] **Step 3: Commit** — `git commit -am "which-world: The Stadium room"`

### Task 4: Room 2 — The Turkey vs Galton

**Files:** Modify `which-world/index.html` (turkey section + `rooms.turkey`).

**Interfaces:** Consumes `GALTON, fit, turkey, onRaf`.

Behaviour: two panels side by side (stacked < 900 px).
- **Galton (Mediocristan, blue):** SVG scatter axes in cm (inches × 2.54), father x, son y. Only one father shown at first: the tallest, 78.5 in = 199 cm (average father ≈ 175 cm). Prompt "This father is 199 cm. Drag to guess his son's height." Draggable horizontal handle on the y-axis (also a range input for keyboard) → white guess dot. Reveal: 481 dots fade in, dashed `y = x` line labelled "if sons matched fathers", solid regression line labelled "what actually happens"; predicted son height `intercept + slope·199` shown vs guess. Caption: "Sons of very tall fathers are tall — but closer to average. Extremes fade." Hover dot → "Father 183 cm · son 180 cm".
- **Turkey (Extremistan, orange):** canvas line of `confidence` over days 1–1,000, auto-drawn in ~4 s on reveal of Galton (or on its own Start button). Prompt at day 1,000: "The turkey has been fed every day for 1,000 days. How sure should it be about day 1,001?" Slider 0–100 %. Reveal: line drops to 0 at day 1,001 (Thanksgiving), axis annotation. Caption: "Its confidence peaked the day the risk was highest." Crosshair tooltip "Day 640 · 99.8% sure".
- Recap: "Same shape of graph, opposite lessons." Sources: *Art of Statistics* ch. 5; *Black Swan* ch. 4.
- `primary()` reveals Galton first, then turkey.

- [ ] **Step 1:** Implement.
- [ ] **Step 2: Verify** — model test passes; Playwright: guess extremes, both reveals, screenshots at both sizes, predicted height displayed = `fit` output (≈ 186 cm).
- [ ] **Step 3: Commit** — `git commit -am "which-world: Turkey vs Galton room"`

### Task 5: Room 3 — The Positive Test

**Files:** Modify `which-world/index.html` (test section + `rooms.test`).

**Interfaces:** Consumes `screen, onRaf`.

Behaviour: prompt "A test for a rare disease is 90% accurate. You test positive. What's the chance you actually have it?" Slider 0–100 % + Reveal. Canvas: 1,000 dots in a 40×25 grid; reveal step 1 colours `ill` dots orange (legend: "has the disease" orange, "doesn't" blue); step 2 animates positives (`tp` orange + `fp` blue) sliding into a right-hand "Tested positive" box, negatives dim. Big number "9 of 108 = 8%" computed from `screen`. Verdict line with the visitor's guess. Then a prevalence slider (0.1–50 %, log-ish steps: 0.1, 0.5, 1, 2, 5, 10, 20, 50) re-runs instantly; at 0 positives shows "No one tested positive". Caption: "When a disease is rare, most positives are false alarms." Source: *Art of Statistics* ch. 8. Hover dot → "Person 37 · has it · tested positive".

- [ ] **Step 1:** Implement.
- [ ] **Step 2: Verify** — Playwright: default shows 9 / 108 / 8%; prevalence 0.1% and 50% show finite numbers; screenshots.
- [ ] **Step 3: Commit** — `git commit -am "which-world: Positive Test room"`

### Task 6: Room 4 — Shipman finale

**Files:** Modify `which-world/index.html` (shipman section).

Content: heading "Counting would have caught him." Three facts: "Harold Shipman killed at least 215 patients." · "Test all 25,000 UK GPs at the usual 5% threshold and ~1,300 innocent doctors get flagged." · "A strict Bonferroni threshold would have flagged Shipman in 1984: 105 deaths where 59.2 were expected." Line tying back: "Same trap as the positive test: test enough people and false alarms drown the signal." Link "Open the Shipman data piece" → `../shipman-data/age_by_year.html`. Closing line + "Start again" → `#home`. Source: *Art of Statistics* intro & ch. 10.

- [ ] **Step 1:** Implement. **Step 2:** Playwright: link resolves (file exists), keyboard → wraps to home. **Step 3:** Commit.

### Task 7: Docs + talk

**Files:** Create `which-world/README.md`, `which-world/TALK.md`; modify root `README.md` (Gallery row + Log line `2026-09-24`).

- README: what it is, rooms with book/chapter refs, sources (GaltonFamilies via Rdatasets; book figures), caveats (481 vs the book's 465 sons; 2007 wealth figures; simulated turkey and crowd, seed 7), rebuild (`fetch_galton.py`, re-inline command from Task 2), tests (`python3 test_galton.py`, `node test_model.mjs`), booth tips (`?talk`, fullscreen, keys).
- TALK.md: 3-minute outline — hook (stadium live), thesis (two worlds), turkey/Galton contrast, positive test, Shipman close, "what I built with Claude" line.

- [ ] Write both, update root README, commit.

### Task 8: Final verification + publish branch

- [ ] `python3 which-world/test_galton.py && node which-world/test_model.mjs`
- [ ] Playwright full walk-through with network requests inspected: zero non-`file://` requests; no console errors; screenshots of every room at 1440×900 and 390×844; idle reset after 60 s (temporarily shorten via `?idle=3` test hook) and disabled with `?talk`.
- [ ] Commit, `git push -u origin which-world`, open a draft PR to `main` (merging = Pages goes live).
