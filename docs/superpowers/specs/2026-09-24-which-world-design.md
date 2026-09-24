# Which World Are You In? — design

**Date:** 2026-09-24 · **Deadline:** Claude community event, 2026-09-26

## Intent

A walk-up interactive exhibit for a booth laptop, doubling as the backbone of a short
talk to judges. Each room asks the visitor to **commit a gut guess, then reveals the
data** that breaks the intuition. Theme: Spiegelhalter's statistics tame one kind of
randomness (Mediocristan); Taleb shows where it breaks (Extremistan). Tagline for the
talk: *"Your gut is a statistician trained in the wrong world."*

Success = a stranger gets a "wait, what?" within ~30 s of touching a room, with no one
explaining it; each room also works as a slide when narrated.

## Rooms (build order = priority; each shippable alone)

1. **The Stadium** (flagship) — Taleb, *Black Swan* ch.3. 1,000 people in a stadium.
   - Guess: slider "What share of the stadium's total *weight* is the heaviest person?"
     then the same for *wealth* when the richest person walks in.
   - Reveal: 1,000 figures as bars/dots; weight: the heaviest human barely registers
     (~0.5%, book max 0.6%). Wealth: one bar tears through the top of the screen —
     99.9% of the total. Visitor's guess is marked against the truth.
   - Data: book figures. Weights sampled ~N(80 kg, 15); 999 people's wealth sampled
     log-normal with a total of ≈ $80M so one $80B person = 99.9% (book's numbers,
     cited as 2007 figures).
2. **The Turkey vs Galton** — *Black Swan* ch.4 + *Art of Statistics* ch.5.
   Two panels that look alike and mean opposite things.
   - Galton: visitor drags a father's height to an extreme and predicts the son's
     height; the 481 real father–son pairs appear, the regression line (slope 0.45)
     shows sons pulled back toward average. "In Mediocristan, extremes fade."
   - Turkey: visitor advances days (auto-play), confidence meter rises with each fed
     day; asked "how safe is day 1,001?"; the line collapses. "In Extremistan, calm is
     not evidence of safety."
   - Data: Galton = real (GaltonFamilies via Rdatasets); turkey = simulated.
3. **The Positive Test** — *Art of Statistics* ch.8. "A 90%-accurate test says you
   have cancer. Chance you do?" Visitor guesses; 1,000 dots fall through a sieve:
   10 ill → 9 positive; 990 well → 99 false positives. 9 of 108 = 8%. A prevalence
   slider re-runs it.
4. **Finale: Shipman** — one closing card linking the existing
   `shipman-data/age_by_year.html`: careful counting (Spiegelhalter ch.10) would have
   flagged him years earlier — and why testing 25,000 GPs makes that hard (ties back
   to room 3).

Plus a **landing screen** (title, one-line premise, room picker) and a
**"which world?" recap** after each reveal (Mediocristan / Extremistan badge).

## Structure

- New folder `which-world/` following the repo's one-folder-per-dataset layout:
  - `index.html` — the whole exhibit, one self-contained file, hash-routed rooms
    (`#stadium`, `#turkey`, `#test`, `#shipman`) so the talk can deep-link.
  - `fetch_galton.py` → `derived/galton_sons.csv`; the 481 pairs are also inlined
    in `index.html` (file:// can't fetch CSVs, and the booth may be offline).
  - `test_galton.py` — asserts 481 rows, slope ≈ 0.45, r ≈ 0.39.
  - `README.md` — sources with book page refs, caveats (465 vs 481 pairs; 2007
    wealth figures; simulated turkey), rebuild steps.
  - `TALK.md` — 3-minute judges' talk outline mapped to rooms.
- Root README: Gallery row + Log line.

## Tech & booth constraints

- Plain HTML + SVG/canvas + vanilla JS. **Zero external requests** (event wifi is
  unreliable): system font stack, no CDN.
- Dark, high-contrast gallery look; large touch/click targets; keyboard: ←/→ between
  rooms, space to reveal (for the talk).
- **Attract/reset:** after 60 s idle, return to the landing screen so each visitor
  starts fresh.
- Laptop-first (1280–1920 wide), readable on a projector; degrades to phone width.

## Out of scope (for these 2 days)

Live crowd data / shared guess logging, three.js, extra rooms (silent evidence,
jelly beans, calibration). Add after the event if wanted.

## Verification

- `python3 which-world/test_galton.py` passes.
- Playwright pass over each room: guess → reveal works, no console errors, screenshots
  at 1440×900 and 390×844; idle reset fires; page loads with network disabled.
- Numbers on screen match the book: 0.5% / 99.9%; slope 0.45; 9 of 108 = 8%.
