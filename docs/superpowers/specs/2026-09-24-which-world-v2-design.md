# Which World Are You In? v2 — Atlas design

**Date:** 2026-09-24 · **Deadline:** Claude community event, 2026-09-26 · Supersedes the
room list and visual system of `2026-09-24-which-world-design.md`; everything not
changed here (booth behaviour, offline, keys, tests, repo conventions) still holds.

## Intent

Awe-inspiring, subtly artistic, more concepts, and one new idea woven through: **seeing
is half the insight**: the same data, drawn better, answers the question for you.
Walk-up booth (hands-on) plus a talk to judges.

## Concept

Seven **plates**, numbered like an atlas because they are a sequence, in two parts:
*I. Which world are you in?* (the gut fails) and *II. See it better* (the picture fixes
it). Each plate has up to three beats: **guess → the obvious picture → the same data
drawn better**. One persistent **crowd of 1,024 ink dots** lives across the whole
exhibit and re-forms into each plate's figure; dots a plate doesn't need fade out. Every
plate hides one **black swan** (a pure black dot; hover says so).

## Plates

| # | plate | guess | obvious picture | drawn better | source |
|---|---|---|---|---|---|
| I | The stadium | heaviest person's share of weight; richest person's share of wealth | stands of 1,000 dots; weight newcomer 0.5%; wealth newcomer spreads as a red ink blot, 99.9% | the same 1,001 fortunes as a dot histogram on a log axis: the 999 reappear across six orders of magnitude | Black Swan ch. 3 |
| II | Galton's sons and the turkey | son of a 199 cm father; turkey's confidence on day 1,001 | (as v1) | 481 real pairs regress to 186 cm; the turkey line falls | AoS ch. 5; BS ch. 4 |
| III | The graveyard | how many of 1,024 coin-flipping fund managers end with a perfect 10-year record? | one manager's "beat the market 10 years running" record | pull back: all 1,024, one for every possible 10-flip sequence; each year the losers fall to a graveyard; exactly one perfect record | BS ch. 8 |
| IV | The Datasaurus | five datasets, identical mean, SD and correlation: similar? | the summary table | plot them: the dots morph dino → star → circle → bullseye → X | AoS ch. 2 (Datasaurus Dozen, Matejka & Fitzmaurice 2017) |
| V | League table → funnel | investigate the district at the top of the league table? | 380 districts ranked by death rate | the same districts as a funnel plot: the "worst" is small and inside chance limits; the real outlier ranked lower | AoS ch. 9 (simulated from the book's setup) |
| VI | The positive test + framing | chance a positive is real | 1,000 people → positives box: 9 of 108 = 8% | framing: "5% die" vs "95% survive" (Bristol) on one 100-dot array; bacon "+18%" vs 6 → 7 in 100 | AoS ch. 8, ch. 1 |
| VII | Shipman | — | book figures | by 1984, 105 deaths drawn as dots against 59.2 expected; ~1,300 false alarms if you test 25,000 GPs naively | AoS intro, ch. 10 |

Shipman ruling: `shipman-data/derived/case_decisions.csv` verdicts are regex-extracted
and count 281 "unlawful killing" against the Inquiry's 215, so no per-year curve from it.

## Visual system (direction B, "Atlas plate")

- Paper `#e7e9ea` with a faint 45° hatch; ink `#1d2a44` (Mediocristan, default dots);
  madder `#b3261e` (Extremistan, extremes, the answer); secondary ink `#46506a`;
  hairlines ink at 35%; the swan `#000`.
- Type: Iowan Old Style (Charter, Georgia fallback) throughout: roman titles, italic
  "Plate I" labels and "Fig. 1." captions; Avenir Next only for buttons and slider
  values. No web fonts.
- Layout per plate: margin column (plate label, title, question, guess, verdict,
  caption) + figure field. Hairline axes with small tick marks, engraved-plate feel.
- Motion: dots settle like ink (eased tweens); one big moment per plate; nothing
  moves for decoration. Reduced motion jumps to end states.

## Architecture

- Still one self-contained `which-world/index.html`, offline, no dependencies.
- **Ink engine:** one full-page canvas behind the plates holding 1,024 dots
  `{x, y, r, c, a}` in document coordinates; `ink.to(targets, ms)` tweens; plates
  compute targets from their figure's bounding box; hover hit-testing returns a dot
  index and the plate supplies its label.
- **Model block** (pure, tested from Node): existing functions plus `datasaurus sets`,
  `managers()` (1,024 = all 10-flip sequences), `districts(seed)` + funnel limits,
  `framing` numbers.
- Data: `fetch_datasaurus.py` → `derived/datasaurus.csv` (5 sets × 142), inlined.

## Scope & order

Build order (each step leaves a shippable page; v1 is on the branch history):
engine + reskin + home + Stadium → Datasaurus → Graveyard → Funnel → Test + framing →
Galton/turkey port → Shipman → docs/TALK. The talk demos I, III, IV, V.

## Verification

- `python3 which-world/test_data.py`, `node which-world/test_model.mjs` pass: Galton
  (481, 0.45, 0.39), Datasaurus stats equal across sets, 1,024 → 1 perfect record,
  funnel top-ranked inside 99.8% limits and outlier outside, 9/108, 6→7 in 100.
- Playwright: every plate's beats at 1440×900 and 1280×720; one network request; no
  console errors; idle reset; `?talk`; resize redraws crisp.
