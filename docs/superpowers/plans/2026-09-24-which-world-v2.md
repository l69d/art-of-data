# Which World Are You In? v2 (Atlas) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `which-world/index.html` as six atlas plates driven by one persistent crowd of 1,024 ink dots, adding the Graveyard, Datasaurus, Funnel and Framing concepts.

**Architecture:** One self-contained HTML file. `<script id="model">` stays pure and Node-tested (existing + new functions and inlined data). A new ink engine (one fixed full-viewport canvas, dots in document coordinates, eased `to()` tweens, hover picking) replaces per-room canvases; each plate computes dot targets from its figure box and draws hairline SVG axes/labels above. v1 code is reused for routing, keys, idle, guess controls.

**Tech Stack:** HTML/CSS/vanilla JS (canvas 2D + SVG), Python 3 stdlib (fetch/test), Node 20 (`node:assert`), Playwright MCP.

**Spec:** `docs/superpowers/specs/2026-09-24-which-world-v2-design.md` (and v1 spec for unchanged booth behaviour).

## Global Constraints

- Zero external requests; opens from `file://`; one `which-world/index.html` with its own doctype/meta.
- Hash routes: `#home`, `#stadium`, `#turkey`, `#graveyard`, `#dino`, `#funnel`, `#test`.
- Keys: ←/→ plates, Space = primary (not on buttons; no key-repeat). Idle 60 s → `#home`; `?talk` disables; `?idle=N`.
- Palette: paper `#e7e9ea`, ink `#1d2a44`, madder `#b3261e`, ink-2 `#46506a`, hairline `rgba(29,42,68,.35)`, swan `#000`.
- Type: `"Iowan Old Style", Charter, Georgia, serif`; UI `"Avenir Next", system-ui, sans-serif` for buttons/slider values only. No all-caps labels.
- Every plate: label "Plate N" (italic), title, "Fig. N." italic caption, one black swan dot with hover "A black swan."
- On-screen numbers match sources: 0.5% / 99.9%; 186 cm; 1 perfect record of 1,024; Datasaurus mean 54.26/47.83, SD 16.77/26.94, r −0.06; 9 of 108 = 8%; 6 → 7 in 100.
- Reduced motion: tweens jump to end. Resize: targets recomputed, canvas crisp at devicePixelRatio.
- Repo: `which-world/README.md` + root README log updated; tests pass before commit.

## Review Focus

1. Page scrolled (short viewport) while dots are drawn → dots stay registered to their figures (document coordinates + scroll offset).
2. Leaving a plate mid-tween / mid-sequence (graveyard years) → next plate's targets win; no stale sequence steps fire after leaving.
3. Datasaurus tab clicked rapidly → morphs retarget from current positions, never jump.
4. Funnel: the district labelled "top of the table" is the one actually ranked first, and the labelled outlier is the only one outside 99.8%.
5. Hover near overlapping dots → tooltip names the nearest visible (a > 0) dot only; faded dots never answer.

---

### Task 1: Datasaurus data + consolidated data test

**Files:** Create `which-world/fetch_datasaurus.py`, `which-world/derived/datasaurus.csv`, `which-world/test_data.py`; delete `which-world/test_galton.py` (folded in).

- [ ] **Step 1: Failing test** — `which-world/test_data.py`

```python
import csv, statistics as s
from pathlib import Path
from collections import defaultdict

D = Path(__file__).parent / "derived"
rows = list(csv.DictReader(open(D / "galton_sons.csv")))
f, c = [float(r["father"]) for r in rows], [float(r["son"]) for r in rows]
assert len(rows) == 481
assert abs(s.linear_regression(f, c).slope - 0.45) < 0.01 and abs(s.correlation(f, c) - 0.39) < 0.01

sets = defaultdict(list)
for r in csv.DictReader(open(D / "datasaurus.csv")):
    sets[r["dataset"]].append((float(r["x"]), float(r["y"])))
assert sorted(sets) == ["bullseye", "circle", "dino", "star", "x_shape"], sorted(sets)
for k, v in sets.items():
    x, y = [p[0] for p in v], [p[1] for p in v]
    assert len(v) == 142
    assert abs(s.mean(x) - 54.26) < .02 and abs(s.mean(y) - 47.83) < .02, k
    assert abs(s.stdev(x) - 16.77) < .02 and abs(s.stdev(y) - 26.94) < .02, k
    assert abs(s.correlation(x, y) + .065) < .01, k
print("ok", len(rows), {k: len(v) for k, v in sets.items()})
```

- [ ] **Step 2:** `python3 which-world/test_data.py` → FAIL (no datasaurus.csv).
- [ ] **Step 3:** `which-world/fetch_datasaurus.py`

```python
"""Datasaurus Dozen (Matejka & Fitzmaurice 2017) via the datasauRus R package -> 5 sets."""
import csv, io, urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/jumpingrivers/datasauRus/HEAD/inst/extdata/DatasaurusDozen-Long.tsv"
KEEP = {"dino", "star", "circle", "bullseye", "x_shape"}
out = Path(__file__).parent / "derived/datasaurus.csv"
rows = csv.DictReader(io.StringIO(urllib.request.urlopen(URL).read().decode()), delimiter="\t")
with open(out, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["dataset", "x", "y"])
    for r in rows:
        if r["dataset"] in KEEP:
            w.writerow([r["dataset"], r["x"], r["y"]])
print("wrote", out)
```

- [ ] **Step 4:** fetch, then `python3 which-world/test_data.py` → `ok 481 {...142 each}`. `git rm which-world/test_galton.py`.
- [ ] **Step 5:** Commit `which-world: Datasaurus data, consolidated data test`.

### Task 2: Model extensions (TDD)

**Files:** Modify `which-world/index.html` (`<script id="model">`), `which-world/test_model.mjs`.

**Produces:** `MANAGERS=1024`, `YEARS=10`, `beat(i,y)→0|1`, `lasted(i)→0..10`, `survivors(y)→number[]`; `poisson(r, mean)`; `districts(seed=DSEED)→{pop,deaths,rate,id}[]` (id 0 = true outlier), `P0=17` (per 100k), `limit(pop, z)→rate`; `BACON={base:6, rel:.18}`; `DINO={dino,star,circle,bullseye,x_shape: [x,y][]}`.

- [ ] **Step 1: Failing tests** appended to `test_model.mjs` (extend the `new Function` return list with the new names):

```js
assert.equal(m.survivors(0).length, 1024);
for (let y = 1; y <= 10; y++) assert.equal(m.survivors(y).length, 1024 >> y);
assert.deepEqual(m.survivors(10), [1023]);
assert.equal(m.lasted(1023), 10); assert.equal(m.lasted(0), 0);

const ds = m.districts(), top = [...ds].sort((a, b) => b.rate - a.rate)[0], out = ds.find(d => d.id === 0);
assert.equal(ds.length, 380);
assert.notEqual(top.id, 0, "top of the table must not be the real outlier");
assert.ok(top.rate < m.limit(top.pop, 3.09), "top of the table inside 99.8%");
assert.ok(out.rate > m.limit(out.pop, 3.09), "outlier outside 99.8%");
assert.equal(ds.filter(d => d.rate > m.limit(d.pop, 3.09)).length, 1, "only one district above 99.8%");

assert.equal(Math.round(m.BACON.base * (1 + m.BACON.rel)), 7);

const st = a => { const n = a.length, mx = a.reduce((s, p) => s + p[0], 0) / n, my = a.reduce((s, p) => s + p[1], 0) / n; return [mx, my]; };
for (const k of ["dino", "star", "circle", "bullseye", "x_shape"]) { const [mx, my] = st(m.DINO[k]); assert.equal(m.DINO[k].length, 142); assert.ok(Math.abs(mx - 54.26) < .02 && Math.abs(my - 47.83) < .02, k); }
```

- [ ] **Step 2:** `node which-world/test_model.mjs` → FAIL (`survivors` undefined).
- [ ] **Step 3:** Implement in the model block:

```js
// Plate III: every possible 10-year record of beating (1) or losing to (0) the market, once each
const MANAGERS = 1024, YEARS = 10;
const beat = (i, y) => (i >> y) & 1;
const lasted = i => { let y = 0; while (y < YEARS && beat(i, y)) y++; return y; };
const survivors = y => [...Array(MANAGERS).keys()].filter(i => lasted(i) >= y);

// Plate V: 380 districts, one true rate everywhere except district 0 (big, genuinely high)
const P0 = 17; // deaths per 100,000 per year
function poisson(r, mean) {
  if (mean > 40) return Math.max(0, Math.round(mean + Math.sqrt(mean) * gauss(r)));
  let k = 0, p = 1; const L = Math.exp(-mean); do { k++; p *= r(); } while (p > L); return k - 1;
}
const limit = (pop, z) => P0 + z * Math.sqrt(P0 / pop * 1e5);
function districts(seed = DSEED) {
  const r = rng(seed), out = [];
  for (let id = 0; id < 380; id++) {
    const pop = id === 0 ? 600000 : Math.round(Math.min(1.2e6, Math.max(2e4, Math.exp(Math.log(1.3e5) + .8 * gauss(r)))));
    const deaths = poisson(r, pop * (id === 0 ? 1.6 * P0 : P0) / 1e5);
    out.push({ id, pop, deaths, rate: deaths / pop * 1e5 });
  }
  return out;
}
const BACON = { base: 6, rel: .18 }; // lifetime bowel-cancer risk per 100, and the "18% higher" headline
```

  `DSEED` = the smallest seed ≥ 1 for which the funnel assertions hold; find it with a throwaway Node loop, then hard-code it. Inline `DINO` from `derived/datasaurus.csv` (generator command recorded in README).
- [ ] **Step 4:** `node which-world/test_model.mjs` → `model ok`.
- [ ] **Step 5:** Commit `which-world: model for graveyard, funnel, framing, datasaurus`.

### Task 3: Ink engine + atlas reskin + home + Plate I (Stadium)

**Files:** Modify `which-world/index.html` (CSS tokens/layout rewritten; `#ink` canvas; engine; home; stadium). Remove the v1 turkey/test/shipman DOM + JS for now (they return in Tasks 7–8) — the page must still load cleanly with rail entries only for built plates.

**Produces (engine):**

```js
// ink: one crowd of 1,024 dots in document coordinates
// target = {x, y, r, c: 0 ink | 1 madder | 2 swan | 3 ink-2, a: 0..1, clip?: [x, y, w, h]}
ink.to(targets, ms = 1100)   // tween every dot from where it is now; missing targets fade to a = 0 in place
ink.set(targets)             // jump (resize)
ink.nudge(i, props)          // live tweak one dot (home attract, blot growth)
ink.pick(clientX, clientY)   // → index of nearest visible dot within its radius + 4 px, or -1
```

  Draw: canvas `position: fixed; inset: 0` behind plates; each frame `ctx.translate(-scrollX, -scrollY)`; dots with `r > 30` drawn as an ink blot (radius wobble `1 + .035·sin(9θ) + .02·sin(23θ)`), clipped to `clip` if given. Plates convert figure-box coordinates with `box(el) → {x: rect.left + scrollX, y: rect.top + scrollY, w, h}`.

**Plate I behaviour:** beats as v1 (weight → wealth), restyled: stands ellipse inside the figure box; newcomer is madder; wealth reveal grows the blot clipped to the figure box; share bar as hairline SVG. New third beat, button "Draw it on a log scale": blot shrinks to one madder dot at the right end; all dots become a dot histogram of log10(wealth) (bins of 0.1 decade, stacked up from a hairline axis with ticks $100 · $10k · $1M · $100M · $10bn, labelled "net worth, logarithmic scale"). Caption "Fig. 1c. The same 1,001 fortunes on a logarithmic scale. Each step is ten times the last." The swan: one stand dot, black.
**Home:** title plate "Which world are you in?", subtitle "Six plates on where your gut is right, where it fails, and how a better picture fixes it.", stands ellipse on the right with the v1 attract loop as a slowly spreading madder blot.

- [ ] Implement; model test passes; Playwright 1440×900: home, all three stadium beats, screenshot each; scroll check (Review Focus 1) at 1280×720.
- [ ] Commit `which-world: ink engine, atlas look, plate I`.

### Task 4: Plate IV — The Datasaurus

Margin: table (5 rows: name, mean x, mean y, SD x, SD y, r — computed live from `DINO` with `fit`/`sum`, 2 dp); question "Five datasets with the same averages, spreads and correlation. Are they alike?" two buttons "Pretty much" / "Not necessarily" (the guess). Reveal: 142 dots form `dino` on hairline axes (x 0–100, y 0–100); tabs for the five sets morph (`ink.to`, 1,200 ms) from current positions; after reveal, auto-cycle every 3 s until a tab is clicked. Verdict: "Identical numbers, completely different data. Always draw it." Caption "Fig. 4. The Datasaurus Dozen (Matejka & Fitzmaurice, 2017), five of thirteen." Swan: one dino point (the eye region, index nearest (55, 80)).
- [ ] Implement; Playwright: table values identical per column; rapid tab clicks retarget smoothly (Review Focus 3); commit `which-world: plate IV Datasaurus`.

### Task 5: Plate III — The Graveyard

Margin question: "1,024 fund managers pick stocks by flipping coins. After 10 years, how many will have beaten the market every single year?" slider 0–64 (default 10). Beat 1 ("the obvious picture"): a single madder dot rising up ten steps on a small hairline chart titled "Manager 1,024: beat the market 10 years running." Beat 2 "Show everyone": all 1,024 dots appear as a 32×32 block in column 0; then year by year (650 ms each, cancelled on leave via `onRaf`/timer tracked by the plate) survivors move to column y as a centred block (side ⌈√n⌉), losers drop to the graveyard strip along the bottom of the figure (faint ink-2, a = .35, stacked in rows under the column where they fell). Column labels "year 0 … 10" and counts (1,024, 512 … 1). The last survivor is madder. Verdict: "Exactly one. Not skill: 1,024 is every possible run of ten coin flips, so one of them is always perfect. We only ever interview the survivor." Caption "Fig. 3. Silent evidence (Taleb, ch. 8)." Swan: one graveyard dot.
- [ ] Implement; Playwright: counts per column 1024…1; leaving mid-sequence stops it (Review Focus 2); commit `which-world: plate III Graveyard`.

### Task 6: Plate V — League table → funnel

Beat 1: league table: the 380 districts as dots at the end of hairline bars, sorted by rate (top = highest), only the top 12 labelled "District 214 … 31.8 per 100,000". Question "The district at the top has the highest death rate in the country. Should it be investigated?" buttons "Yes, investigate" / "Not yet". Beat 2: dots fly to a funnel plot: x = population (log scale, 20k–1.2M), y = rate; 95% and 99.8% limits (`limit(pop, ±1.96/±3.09)`) as hairline curves, P0 line; top-of-table dot ringed in madder "top of the league table", district 0 ringed "the real outlier". Verdict: "The top of the table is just small: few deaths, so its rate swings. The only district outside the limits ranked Nth." (N computed). Caption "Fig. 5. Funnel plot of 380 districts (simulated from Spiegelhalter's bowel-cancer example, ch. 9)." Swan: a mid-funnel dot.
- [ ] Implement; Playwright: labelled dots match Review Focus 4; commit `which-world: plate V funnel`.

### Task 7: Plate VI — Positive test + framing (last plate)

Port v1 test room onto the ink engine (1,000 grid dots → positives box; prevalence slider; 9/108 = 8%). New beat "Same facts, other words": two small 100-dot arrays side by side in the figure: (a) Bristol — toggle "5% die" / "95% survive" recolours the 5 or the 95 madder (same dots, different emphasis); (b) bacon — "18% higher risk" vs 6 → 7 in 100 (the 7th dot turns madder when "with bacon" is toggled). Closing line: "Which world you're in, and how you draw it, decide half the answer." + "Start again". Caption "Fig. 6. Screening and framing (Spiegelhalter, ch. 1 and 8)."
- [ ] Implement; Playwright: 9/108, prevalence ends finite, toggles; commit `which-world: plate VI test + framing`.

### Task 8: Plate II — Galton and the turkey (port)

Port v1 panels into atlas styling: Galton's 481 pairs drawn by ink dots inside the left figure (hairline axes, y = x dashed, regression solid madder), turkey as an SVG ink line with the madder fall. Same questions, verdicts and numbers as v1.
- [ ] Implement; Playwright both reveals; commit `which-world: plate II port`.

### Task 9: Docs, talk, verification, publish

- [ ] `which-world/README.md` rewritten for six plates (sources, simulated caveats: crowd, turkey, districts; Datasaurus citation; regenerate commands for GALTON and DINO; booth notes). `TALK.md` rewritten: 3 min demoing I, III, IV, V. Root README gallery row text + new screenshot + log line.
- [ ] `python3 which-world/test_data.py && node which-world/test_model.mjs`; Playwright: every plate at 1440×900 and 1280×720, network = 1 request, no console errors, idle + `?talk`.
- [ ] Final whole-branch review (fresh reviewer), fix pass, push `which-world`, update PR #1 description.
