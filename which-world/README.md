# Which world are you in?

Five short stories about data, told one card at a time, plus a record of the choices you
make in them. In each story you take the seat: Abraham Wald in 1943, a stadium engineer,
a turkey, an analyst, a GP. The build-up comes a card at a time, each one a new shot in
the 3D scene. You act with your own hands: open the gates, eat breakfast, turn the
damaged bomber around, open the letter. Then you make the big call, watch it play out,
and read the moral of the story.

The stories come from Nassim Taleb's *The Black Swan* and David Spiegelhalter's *The Art
of Statistics*, plus Wald's bombers. The thread through them: Spiegelhalter's statistics
tame one kind of randomness (*Mediocristan*), Taleb shows where that breaks
(*Extremistan*), and a better picture is often half the insight.

It is drawn in three.js as a dreamy, hand-inked atlas, somewhere between art and chart:
- ink on paper, with watercolour washes drifting behind each scene;
- points that glow and float, and gold dust in the air;
- hairlines drawn twice, slightly off, as if by hand;
- paper clouds and paper lanterns;
- madder red for the extreme case, and one black swan hidden in every plate.

A single crowd of 1,024 ink points re-forms into every scene: a murmuration on the title
page, a bomber's bullet holes, a stadium, a tower of days, a dinosaur, a thousand
fireflies. You can drag any scene to look around.

**Open:** `index.html`, straight from disk, no server or network needed.
Live: https://l69d.github.io/art-of-data/which-world/

| plate | your seat | what you do | the decision | what plays out | source |
|---|---|---|---|---|---|
| I. The missing bombers | Abraham Wald, New York, 1943 | watch the planes come home; turn the bomber around | where should the armour go? | the planes that never came back rise as a red ghost formation, hit in the engines, and drift away into the clouds | Wald, 1943 |
| II. The stadium | the engineer, then the fundraiser | open the gates; hold to raise a fortune | reinforce the stand? who to spend the night with? | the heaviest fan adds 0.5%; the richest guest holds 99.9%, a column 18 km tall at this scale; then a log scale | Taleb, ch. 3 |
| III. The turkey | the turkey | eat breakfast; let the days pass | day 1,000: relax, stay alert, run? | 1,000 fed days climb a spiral tower under a rising sun; day 1,001 falls | Taleb, ch. 4 |
| IV. The Datasaurus | an analyst | open five branch reports | agree with the boss? | a cloud lifts off the page and flattens into a dinosaur, a star, a circle, a bullseye, an X | Spiegelhalter, ch. 2 |
| V. The letter | a GP, then a press officer and a headline writer | open Sarah's letter | what do you tell her? which words do you print? | a thousand fireflies take the test: 9 of 108 positives are real (8%), and Sarah is one of the false alarms; "5% die" vs "95% survive"; "+18%" vs 6 → 7 in 100 | Spiegelhalter, ch. 1, 2, 8 |
| VI. Your record | | | | every choice, marked, with its world and a verdict | |

## Wald's bombers, by the bullet count

- **The story:** Abraham Wald's work at the Statistical Research Group in 1943. It is
  not in either book.
- **The simulation:** illustrative (`bombers()`, seed 5). There are 200 sorties, each
  plane takes 1 + Poisson(3) hits, and each hit lands on a part of the airframe in
  proportion to its area. An engine hit brings a plane down 60% of the time; a hit
  anywhere else rarely does.
- **What the page shows:** the average number of bullet holes per plane, part by part
  (`bomberCounts()`).

| holes per plane | came home (139) | never came back (61) |
|---|---|---|
| engines | 0.2 | 1.0 |
| fuel system | 0.4 | 0.4 |
| fuselage | 1.2 | 1.2 |
| wings and tail | 1.8 | 2.0 |

Every part is hit about as often on both groups of planes, except the engines, and that
comparison doesn't depend on how big each part is. `test_model.mjs` checks it: engines
hit more than 3× as often on the lost planes; fuselage and wings within 25%.

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
    centimetre per median fortune. The drawn column is capped; it leaves the frame
    either way.
  - The crowd is simulated with seed 7.
- **The turkey** is simulated. Its confidence is Laplace's rule of succession,
  (d+1)/(d+2) after d fed days.
- **The letter:**
  - The test has 90% sensitivity and 90% specificity, as in the book.
  - Sarah is invented. She is the first false alarm among the 1,000 at 1-in-100
    prevalence, so her story matches the data.
  - Bacon's "18% higher" lifetime risk goes from 6 in 100 to 7 in 100.

## three.js

`three.min.js` is three.js r149's classic build (MIT licence, from npm `three@0.149.0`),
loaded with a plain `<script src>`. It is vendored rather than loaded from the CDN
through an import map, the repo's usual convention, because the booth may be offline
and ES modules don't load from `file://`.

## Rebuild and test

```sh
python3 fetch_datasaurus.py   # re-download derived/datasaurus.csv
python3 test_data.py          # the five Datasaurus sets share their stats
node test_model.mjs           # the key numbers the stories show, and the inlined data = CSV
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

- Open it fullscreen in Chrome or Safari, on a laptop with a real graphics chip. The
  scenes are gentle but continuous, and headless or software rendering will crawl.
- Plates are deep-linkable: `#bombers`, `#stadium`, `#turkey`, `#dino`, `#letter`,
  `#record`.
- Visitors click an option at every "What do you do?". Space presses Continue and the
  "Eat" or "Open the gates" style buttons, and holding Space works the hold buttons. It
  never picks an option for them. ←/→ moves between plates. Dragging any scene turns the
  camera.
- A full visit takes about 12 minutes. Most visitors will play one to three stories;
  "Your record" works with any number.
- After 60 seconds without input the page returns to the title for the next visitor,
  which also clears their record. Add `?talk` to switch that off while presenting.
  `?idle=N` changes the timeout to N seconds.
- The talk script is in `TALK.md`.
