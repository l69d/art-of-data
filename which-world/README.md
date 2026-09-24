# Which world are you in?

A walk-up exhibit in four rooms. Each room asks you to commit a gut guess, then shows
the data. The thread running through them comes from two books: Spiegelhalter's
statistics tame one kind of randomness (Taleb's *Mediocristan*), and Taleb shows
where that breaks (*Extremistan*).

**Open:** `index.html`, straight from disk, no server or network needed.
Live: https://l69d.github.io/art-of-data/which-world/

| room | the gut says | the data says | source |
|---|---|---|---|
| 1. The stadium | the heaviest or richest person is a bit above the rest | weight: 0.5% of the stadium's total. Wealth: 99.9% | Taleb, *The Black Swan*, ch. 3 |
| 2. Galton's sons and the turkey | a long run of data predicts tomorrow | sons of 199 cm fathers average 186 cm (extremes fade); the turkey is 99.9% sure the day before Thanksgiving | Spiegelhalter, *The Art of Statistics*, ch. 5; Taleb ch. 4 |
| 3. The positive test | a 90%-accurate positive means about 90% | 9 of 108 positives = 8% at 1-in-100 prevalence | Spiegelhalter ch. 8 |
| 4. Shipman | — | ~1,300 innocent GPs flagged at p < 0.05; Bonferroni would have caught him in 1984 (105 vs 59.2 expected) | Spiegelhalter intro and ch. 10 |

## Data

- **Galton's family heights (1886)**: `HistData::GaltonFamilies`, fetched from
  [Rdatasets](https://vincentarelbundock.github.io/Rdatasets/) by `fetch_galton.py`
  into `derived/galton_sons.csv` (481 sons, columns `father,son` in inches).
  Slope 0.45, r = 0.39, matching the book. The book quotes 465 father–son pairs;
  this copy of the dataset has 481 sons. The numbers are also inlined in `index.html`,
  because a page opened from `file://` can't fetch a CSV.
- **The stadium** (*The Black Swan*, ch. 3, 2007 edition). Taleb has a person at
  "three times the average, between four hundred and five hundred pounds", at
  "about a half of a percent", and "the heaviest biologically possible human" at "not
  more than, say, 0.6 percent". For wealth he has Bill Gates at "close to $80 billion",
  with "the total capital of the others around a few million", making 99.9%.
  Our choices, both within Taleb's bounds:
  - The heaviest person is 400 kg, which gives 0.5%, under his 0.6% ceiling.
  - The other 1,000 hold $80M together ($80k each). That's more realistic than "a few
    million", and it gives exactly his 99.9%. A few million would push the share past
    99.99%, so ours understates his point.

  The crowd is simulated with seed 7: weights ~ N(80 kg, 15), and wealth log-normal.
- **The turkey**: simulated. Its "confidence" is Laplace's rule of succession,
  (d+1)/(d+2) after d fed days.
- **The positive test**: 90% sensitivity, 90% specificity, as in the book.

## Rebuild and test

```sh
python3 fetch_galton.py     # re-download derived/galton_sons.csv
python3 test_galton.py      # 481 rows, slope 0.45, r 0.39
node test_model.mjs         # every number the page shows, checked against the books
```

After re-fetching, re-inline the data (from the repo root):

```sh
python3 -c "import csv;print('const GALTON = '+str([[float(r['father']),float(r['son'])] for r in csv.DictReader(open('which-world/derived/galton_sons.csv'))]).replace(' ','')+';')"
```

and paste the result over the `const GALTON = …;` line in `index.html`.
`test_model.mjs` fails if the two get out of sync.

## At the booth

- Open fullscreen in Chrome or Safari. Rooms are deep-linkable: `#stadium`, `#turkey`,
  `#test`, `#shipman`.
- ←/→ moves between rooms; Space presses the room's main button.
- After 60 seconds without input the page returns to the start screen for the next
  visitor. Add `?talk` to the URL to switch that off while presenting
  (`index.html?talk#stadium`). `?idle=N` changes the timeout to N seconds.
- The finale's "See the Shipman data" link only appears with `?talk`. That page has no
  idle reset, so booth visitors never leave the exhibit.
- The talk outline is in `TALK.md`.
