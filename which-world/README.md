# Which world are you in?

An atlas in six plates, built for a walk-up booth. Each plate asks you to commit a gut
guess, shows you the data, and then, where it can, **draws the same data better**,
because seeing it properly is half the insight. The thread comes from two books:
Spiegelhalter's statistics tame one kind of randomness (Taleb's *Mediocristan*), and
Taleb shows where that breaks (*Extremistan*).

One crowd of 1,024 ink dots lives across the whole page and re-forms into each plate's
figure. Every plate hides one black swan.

**Open:** `index.html`, straight from disk, no server or network needed.
Live: https://l69d.github.io/art-of-data/which-world/

| plate | the gut says | the data says | drawn better | source |
|---|---|---|---|---|
| I. The stadium | the heaviest or richest person is a bit above the rest | weight 0.5% of the total; wealth 99.9% | the same fortunes on a log axis: the 1,000 reappear, and the richest sits alone at 1.8 million times the typical fortune | Taleb, *The Black Swan*, ch. 3 |
| II. Galton's sons and the turkey | a long run of data predicts tomorrow | sons of 199 cm fathers average 186 cm; the turkey is 99.9% sure the day before Thanksgiving | | Spiegelhalter, *The Art of Statistics*, ch. 5; Taleb ch. 4 |
| III. The graveyard | a perfect 10-year record means skill | exactly 1 of 1,024 coin-flipping managers has one | the 1,023 fired managers, drawn as ghosts | Taleb ch. 8 |
| IV. The Datasaurus | same mean, SD and correlation means similar data | a dinosaur, a star, a circle, a bullseye, an X | plot them | Spiegelhalter ch. 2 |
| V. The league table | investigate the district at the top | it's small; its rate swings by chance | a funnel plot: the only real outlier ranked 6th | Spiegelhalter ch. 9 |
| VI. The positive test | a 90%-accurate positive means ~90% | 9 of 108 = 8% at 1-in-100 | framing: "5% die" vs "95% survive"; "+18%" vs 6 → 7 in 100 | Spiegelhalter ch. 1, 2, 8 |

## Data and what's simulated

- **Galton's family heights (1886)**: `HistData::GaltonFamilies` from
  [Rdatasets](https://vincentarelbundock.github.io/Rdatasets/), fetched by
  `fetch_galton.py` into `derived/galton_sons.csv` (481 sons, `father,son` in inches).
  Slope 0.45 and r = 0.39 match the book. The book quotes 465 pairs; this copy has
  481 sons.
- **The Datasaurus Dozen** (Matejka & Fitzmaurice, *Same Stats, Different Graphs*,
  CHI 2017), via the [datasauRus](https://github.com/jumpingrivers/datasauRus) R package.
  `fetch_datasaurus.py` keeps five of the thirteen sets in `derived/datasaurus.csv`.
- **The stadium** (*The Black Swan*, ch. 3, 2007 edition):
  - Taleb's figures: a person at "three times the average, between four hundred and
    five hundred pounds" is "about a half of a percent"; the "heaviest biologically
    possible human" is "not more than, say, 0.6 percent"; Bill Gates at "close to $80
    billion", with "the total capital of the others around a few million", is 99.9%.
  - Our choices, within those bounds: the heaviest person is 400 kg, which gives 0.5%.
    The other 1,000 hold $80M together, which gives exactly 99.9%. Taleb's "few million"
    would push the share past 99.99%.
  - The crowd is simulated with seed 7: weights ~ N(80 kg, 15), wealth log-normal.
  - The wealth ink drop is capped at the size of the figure. The share bar and the
    number carry the exact 99.9%.
- **The turkey** is simulated. Its confidence is Laplace's rule of succession,
  (d+1)/(d+2) after d fed days.
- **The graveyard** is exact, not simulated: manager *i*'s ten yearly results are the
  bits of *i*, so the 1,024 managers are every possible run of ten coin flips, and
  exactly one is perfect. Seats in the grid are shuffled (seed 21).
- **The league table** is simulated from Spiegelhalter's bowel-cancer example
  (380 districts, a national rate of 17 per 100,000). Every district shares that rate
  except one large district at 1.6×. Seed 1 is the first seed where the top of the
  table sits inside the 99.8% limits and that district is the only one outside;
  `test_model.mjs` checks both.
- **The positive test** uses 90% sensitivity and 90% specificity, as in the book. The
  Bristol framing uses the book's 5%/95% example. Bacon's "18% higher" lifetime risk
  goes from 6 in 100 to 7 in 100.

## Rebuild and test

```sh
python3 fetch_galton.py && python3 fetch_datasaurus.py   # re-download derived/
python3 test_data.py         # Galton 481 / 0.45 / 0.39; five Datasaurus sets share their stats
node test_model.mjs          # every number the page shows, and inlined data = CSVs
```

The data is inlined in `index.html`, because a page opened from `file://` can't fetch a
CSV. To re-inline after a fetch, run these from the repo root and paste each output
over its `const … = …;` line:

```sh
python3 -c "import csv;print('const GALTON = '+str([[float(r['father']),float(r['son'])] for r in csv.DictReader(open('which-world/derived/galton_sons.csv'))]).replace(' ','')+';')"
python3 -c "import csv,collections as c;d=c.OrderedDict()
for r in csv.DictReader(open('which-world/derived/datasaurus.csv')): d.setdefault(r['dataset'],[]).append([round(float(r['x']),4),round(float(r['y']),4)])
print('const DINO = {'+','.join(k+':'+str(d[k]).replace(' ','') for k in ['dino','star','circle','bullseye','x_shape'])+'};')"
```

`test_model.mjs` fails if either copy drifts from its CSV.

## At the booth

- Open it fullscreen in Chrome or Safari. Plates are deep-linkable: `#stadium`,
  `#turkey`, `#graveyard`, `#dino`, `#funnel`, `#test`.
- ←/→ moves between plates. Space presses the plate's main button.
- After 60 seconds without input the page returns to the title for the next visitor.
  Add `?talk` to switch that off while presenting (`index.html?talk#stadium`).
  `?idle=N` changes the timeout to N seconds.
- The talk script is in `TALK.md`.
