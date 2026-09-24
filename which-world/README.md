# Which world are you in?

Six short stories about data, and a record of the choices you make in them. In each one
you take a seat, as an engineer, a turkey, Abraham Wald, a health minister or a GP, and
make a call. Then you watch it play out and read the moral of the story. The stories
come from Nassim Taleb's *The Black Swan* and David Spiegelhalter's *The Art of
Statistics*. The thread through them: Spiegelhalter's statistics tame one kind of
randomness (*Mediocristan*), Taleb shows where that breaks (*Extremistan*), and a
better picture is often half the insight.

It is drawn in three.js as an engraved atlas: ink on paper, madder red for the extreme
case, and one black swan hidden in every plate. A single crowd of 1,024 ink dots re-forms
into each story's scene: a stadium, a bomber, a tower of days, a funnel plot.

**Open:** `index.html`, straight from disk, no server or network needed.
Live: https://l69d.github.io/art-of-data/which-world/

| plate | your seat | your choice | what plays out | source |
|---|---|---|---|---|
| I. The stadium | the engineer, then the fundraiser | reinforce the stand? who to talk to? | the heaviest fan adds 0.5%; the richest guest holds 99.9%, a column 18 km tall at this scale; then the same fortunes on a log scale | Taleb, ch. 3 |
| II. The turkey | the turkey, on day 1,000 | relax, stay alert, run? | 1,000 fed days climb a spiral tower; confidence 99.9%; day 1,001 falls | Taleb, ch. 4 |
| III. The graveyard | Abraham Wald, 1943; then a pension fund | where to armour the bombers? hire the 10-year genius? | the missing planes rise as ghosts, hit in the engines; 1 of 1,024 coin-flippers keeps a perfect record | Wald via Ellenberg; Taleb, ch. 8 |
| IV. The Datasaurus | an analyst whose boss reads only tables | agree the branches are the same? | a cloud collapses flat into a dinosaur, a star, a circle, a bullseye, an X | Spiegelhalter, ch. 2 |
| V. The league table | the health minister, facing the front page | inspect, sack, or ask for a funnel plot? | the skyline of 380 districts flies into a funnel: the "worst" is small, and the outlier ranked 6th | Spiegelhalter, ch. 9 |
| VI. The positive test | a GP; then a press officer and a headline writer | what do you tell the patient? which words do you print? | 9 of 108 positives are real (8%); "5% die" vs "95% survive"; "+18%" vs 6 → 7 in 100 | Spiegelhalter, ch. 1, 2, 8 |
| VII. Your record | | | every choice, marked, with its world and a verdict | |

## Data and what's simulated

- **The Datasaurus Dozen** (Matejka & Fitzmaurice, *Same Stats, Different Graphs*,
  CHI 2017), via the [datasauRus](https://github.com/jumpingrivers/datasauRus) R package.
  `fetch_datasaurus.py` keeps five of the thirteen sets in `derived/datasaurus.csv`.
  The table shows one decimal place, where all five are identical.
- **The stadium** (*The Black Swan*, ch. 3, 2007 edition):
  - Taleb's figures: a person at "three times the average, between four hundred and
    five hundred pounds" is "about a half of a percent"; the "heaviest biologically
    possible human" is "not more than, say, 0.6 percent"; Bill Gates at "close to $80
    billion", with "the total capital of the others around a few million", is 99.9%.
  - Our choices, within those bounds: the heaviest person is 400 kg, which gives 0.5%.
    The other 1,000 hold $80M together, which gives exactly 99.9%.
  - The "18 km" line is the richest fortune divided by the median guest's, at one
    centimetre per median fortune.
  - The crowd is simulated with seed 7.
- **The turkey** is simulated. Its confidence is Laplace's rule of succession,
  (d+1)/(d+2) after d fed days.
- **Wald's bombers**:
  - The story is Abraham Wald's work at the Statistical Research Group in 1943. It is
    not in either book.
  - The holes-per-square-foot table (engines 1.11, fuselage 1.73, fuel system 1.55,
    rest 1.80) is as popularised by Jordan Ellenberg, *How Not to Be Wrong* (2014).
  - The ink simulation is illustrative: `bombers()`, seed 5, 200 sorties, with engine
    hits the most lethal.
  - `test_model.mjs` checks that the planes that came home show far fewer engine hits
    than all the planes did.
- **The fund managers** are exact, not simulated. Manager *i*'s ten yearly results are
  the bits of *i*, so the 1,024 managers are every possible run of ten coin flips.
- **The league table** is simulated from Spiegelhalter's bowel-cancer example:
  - 380 districts share a rate of 17 per 100,000, except one large district at 1.6×.
  - Seed 1 is the first seed where the top of the table sits inside the 99.8% limits
    and that district is the only one outside them. `test_model.mjs` checks both.
- **The positive test** uses 90% sensitivity and 90% specificity, as in the book.
  Bacon's "18% higher" lifetime risk goes from 6 in 100 to 7 in 100.

## three.js

`three.min.js` is three.js r149's classic build (MIT licence, from npm `three@0.149.0`),
loaded with a plain `<script src>`. It is vendored rather than loaded from the CDN
through an import map, the repo's usual convention, because the booth may be offline
and ES modules don't load from `file://`.

## Rebuild and test

```sh
python3 fetch_datasaurus.py   # re-download derived/datasaurus.csv
python3 test_data.py          # the five Datasaurus sets share their stats
node test_model.mjs           # every number the stories show, and the inlined data = CSV
```

The Datasaurus sets are inlined in `index.html`, because a page opened from `file://`
can't fetch a CSV. To re-inline after a fetch, run this from the repo root and paste the
output over the `const DINO = …;` line:

```sh
python3 -c "import csv,collections as c;d=c.OrderedDict()
for r in csv.DictReader(open('which-world/derived/datasaurus.csv')): d.setdefault(r['dataset'],[]).append([round(float(r['x']),4),round(float(r['y']),4)])
print('const DINO = {'+','.join(k+':'+str(d[k]).replace(' ','') for k in ['dino','star','circle','bullseye','x_shape'])+'};')"
```

## At the booth

- Open it fullscreen in Chrome or Safari. Plates are deep-linkable: `#stadium`,
  `#turkey`, `#graveyard`, `#dino`, `#funnel`, `#test`, `#record`.
- Visitors click an option at every "What do you do?". Space presses the Continue
  button but never picks an option for them. ←/→ moves between plates.
- After 60 seconds without input the page returns to the title for the next visitor,
  which also clears their record. Add `?talk` to switch that off while presenting.
  `?idle=N` changes the timeout to N seconds.
- The talk script is in `TALK.md`.
