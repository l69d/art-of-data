# Harold Shipman — public data collection

Everything here is public record: UK Crown Copyright material published by the
Shipman Inquiry (2001–2005) and the Department of Health, plus Wikipedia.
Reusable under the Open Government Licence (Crown material) / CC BY-SA (Wikipedia).

The Inquiry's own website (`the-shipman-inquiry.org.uk`) no longer exists — the domain
is parked. Everything under `raw/` was recovered from the Internet Archive's snapshots
of that site. (The UK Government Web Archive holds the same site but blocks automated
fetching behind a WAF captcha.)

## Layout

```
docs/               official PDFs as published
raw/                mirrored Inquiry site HTML, 3,579 pages (Wayback snapshots, verbatim)
                    — not in git (99 MB); only the fetch lists are. Rebuild: see Reproducing
wikipedia/          article wikitext
derived/            parsed, analysis-ready CSV/JSONL
  case_text/          per-case decision plain text
  report_text/        Fourth/Fifth/Sixth Report prose
  doc_text/           text extracted from the PDFs
age_by_year.html    the age-vs-year scatter — live at
                    https://l69d.github.io/art-of-data/shipman-data/age_by_year.html
shipman-scatter.png screenshot of it
fetch.py            Wayback mirror   (fetch.py <list-file> <out-dir> [workers])
parse.py            case HTML  -> CSV/JSONL
reporttext.py       report HTML -> readable text
pdftext.py          PDF -> text
test_parse.py       invariants for all of the above
plotdata.py         CSV -> plot_points.json for the chart
```

## Analysis-ready tables (`derived/`)

| file | rows | what it is |
|---|---|---|
| `case_decisions.csv` / `.jsonl` | 558 | One row per published individual case decision: name, sex, date of death, age, place, the cause Shipman certified, and the Inquiry's verdict. |
| `case_text/*.txt` | 558 | Full plain text of each decision (narrative, expert evidence, conclusion). |
| `sixth_report_deaths.csv` | 254 | Sixth Report tabular lists (Pontefract years, 1970–74): name, date of death, age, decision. Already tabular in the source. |
| `case_roster.csv` | 639 | Every case the Inquiry considered in Phase 1 + whether oral or written evidence was taken. |
| `plot_points.json` | 531 | The subset with a usable date, age and sex — what the scatter plots. |
| `report_sections.csv` | 931 | Index of the Fourth/Fifth/Sixth Report sections: report, chapter, section, word count. |
| `report_text/*.txt` | 3 | Those reports as readable prose (10 MB total). |
| `doc_text/*.txt` | 5 | Text of the PDFs below. |

### `case_decisions.csv` columns
`case_group` (source letter-group id) · `case_no` · `name` · `title` · `sex` ·
`report` · `date_of_death` · `year_of_death` · `age_years` · `age_text` ·
`place_of_death` · `certified_cause` · `verdict` · `convicted_at_trial` ·
`decision_section` · `conclusion` · `n_words` · `source_file`

`verdict` is normalised to: `unlawful killing`, `natural causes`,
`cause for suspicion`, `insufficient evidence`, `suicide`, `accidental`.

`sex` comes from the honorific the decision uses for the person (Mrs / Miss / Mr) —
resolved for all 558. `age_years` is numeric (infants are fractions of a year);
`age_text` keeps the source wording, e.g. `2 days`, `3 months`.

Current coverage: 15 rows have no parseable date, 14 no age, 55 no verdict,
154 no certified cause.

## Documents (`docs/`)

| file | source |
|---|---|
| `shipman_inquiry_second_report.pdf` | Second Report — the police investigation of March 1998 (Cm 5853), 180pp |
| `shipman_inquiry_third_report.pdf` | Third Report — death certification and investigation of deaths by coroners (Cm 5854), 636pp |
| `baker_clinical_audit_2001.pdf` | Baker, *Harold Shipman's clinical practice 1974–1998: a clinical audit commissioned by the Chief Medical Officer*, 156pp — the statistical comparison against local GPs |
| `govt_response_learning_from_tragedy_2007.pdf` | Government action programme overview (Cm 7014) |
| `govt_response_safeguarding_patients_2007.pdf` | Government response to the Fifth Report + Ayling/Neale/Kerr-Haslam (Cm 7015) |

`wikipedia/*.wikitext` — article source for *Harold Shipman* and *The Shipman Inquiry*.

## What's here vs. what isn't

Present: the First Report's individual case decisions (the core victim-level data),
the Sixth Report's death tables, the Fourth/Fifth/Sixth Reports in full
(`derived/report_text/`), and the
Second/Third Reports as PDFs. The mirror is complete: 3,579 of 3,579 indexed pages.

Not present, deliberately: the First, Fourth and Fifth Reports as official PDFs (never
on gov.uk; the Inquiry only published them as HTML + CD-ROM); the hearing transcripts and
witness-statement calendars (~8,500 pages of hearing metadata); and the per-case evidence
catalogue (`raw/list_caseinfo.txt`, 671 pages) — that one lists evidence document IDs
rather than evidence, and nothing here parses it. Re-fetch any of them with
`python3 fetch.py raw/list_caseinfo.txt raw/caseinfo 3`.

## Caveats for analysis

- `verdict`, `date_of_death`, `age` and `certified_cause` in `case_decisions.csv` are
  **regex-extracted from prose**, not from a structured source. Roughly 5% of verdicts
  stay blank; spot-check against `conclusion` and `case_text/` before relying on them.
  `sixth_report_deaths.csv` *is* from a real source table and needs no such caveat.
- `convicted_at_trial` marks the 15 murders Shipman was convicted of at Preston Crown
  Court on 31 Jan 2000. Those decisions carry a "Comment" section rather than a
  "Conclusion", because the verdict came from the jury, not the Inquiry.
- The Inquiry's totals: 215 deaths found to be unlawful killings, ~45 more with real
  suspicion, out of 887 death certificates examined. Individual decisions were not
  published for every case considered, so this collection is a large subset, not the
  full 887.
- Ages in the Sixth Report tables include infants ("6 hours", "2 weeks") — parse as text,
  not integers.

## Reproducing

```bash
for L in case_decision index background reports; do
  python3 fetch.py raw/list_$L.txt raw/${L/case_decision/case_decisions} 3
done
python3 parse.py && python3 reporttext.py && python3 pdftext.py && python3 plotdata.py
```
`raw/cdx_ok.txt` is the Wayback index the `raw/list_*.txt` fetch lists were built from.
`fetch.py` skips files it already has, so an interrupted run just needs re-running.
Keep workers at 3 or below — archive.org refuses connections above that.

One quirk worth knowing if you re-derive the report text: the site served each report
under two URL schemes, `?ch=N&pa=M` (the whole of chapter N, identical for every `pa`)
and `?ID=n` (one section). `reporttext.py` therefore dedupes at paragraph level rather
than page level; without that the Fifth Report comes out four times its real size.
