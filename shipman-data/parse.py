#!/usr/bin/env python3
"""Turn the mirrored Shipman Inquiry HTML into analysable CSV/JSONL.

Outputs (in derived/):
  case_decisions.csv / .jsonl  one row per published individual case decision
  case_text/*.txt              plain text of each decision
  sixth_report_deaths.csv      Sixth Report tabular death lists (name/date/age/decision)
  case_roster.csv              every case the Inquiry considered + evidence type
"""
import re, os, csv, glob, json, html, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW, OUT = os.path.join(ROOT, "raw"), os.path.join(ROOT, "derived")
TXT = os.path.join(OUT, "case_text")
for d in (OUT, TXT):
    os.makedirs(d, exist_ok=True)

MONTH = ("January|February|March|April|May|June|July|August|September|"
         "October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec")


def lines_of(path):
    b = open(path, "rb").read()
    try:
        t = b.decode("utf-8")
    except UnicodeDecodeError:
        t = b.decode("cp1252", errors="replace")
    t = re.sub(r"(?s)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", "\n", t)
    t = html.unescape(t).replace("\xa0", " ").replace("�", " ")
    out = []
    for l in (re.sub(r"\s+", " ", x).strip() for x in t.split("\n")):
        if not l:
            continue
        if l in ("st", "nd", "rd", "th") and out and out[-1][-1:].isdigit():
            out[-1] += l          # <sup>th</sup> split "12" and "th" onto separate lines
        else:
            out.append(l)
    return out


# --------------------------------------------------------------- tabular lists
def parse_tables(pattern, out_name):
    """6r_caseindex / 6r_casesbyyear render one flat table: N header cells then N-cell rows."""
    rows, seen = [], set()
    for f in sorted(glob.glob(pattern)):
        L = lines_of(f)
        if "Decision" not in L:
            continue
        i = L.index("Decision")
        cols = L[i - 3:i + 1]
        if len(cols) != 4:
            continue
        body = L[i + 1:]
        stop = next((j for j, l in enumerate(body)
                     if re.fullmatch(r"[A-Z]", l) or l.startswith("Year:")), len(body))
        body = body[:stop]
        j = 0
        while j + 4 <= len(body):
            rec = dict(zip(cols, body[j:j + 4]))
            j += 4
            # a free-text caveat sometimes follows a row; it is not a date/name pair
            while j < len(body) and len(body[j].split()) > 6:
                rec["note"] = body[j]
                j += 1
            key = (rec.get("Name"), rec.get("Date of Death"))
            if not rec.get("Name") or key in seen:
                continue
            seen.add(key)
            rec["source_file"] = os.path.basename(f)
            rows.append(rec)
    if rows:
        cols = list(dict.fromkeys([c for r in rows for c in r]))
        with open(os.path.join(OUT, out_name), "w", newline="") as fh:
            w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(rows)
    return rows


def parse_roster():
    """caseindex.asp?letter=X -> 'Surname, Forenames' | evidence type."""
    rows, seen = [], set()
    for f in sorted(glob.glob(f"{RAW}/index/caseindex.asp*")):
        L = lines_of(f)
        for a, b in zip(L, L[1:]):
            if "," in a and re.match(r"^[A-Z][A-Za-z'\- ]+, [A-Z]", a) \
               and re.match(r"^(Written|Oral|No) evidence", b):
                if a in seen:
                    continue
                seen.add(a)
                surname, forenames = [x.strip() for x in a.split(",", 1)]
                rows.append({"surname": surname, "forenames": forenames,
                             "name": f"{forenames} {surname}", "evidence": b,
                             "source_file": os.path.basename(f)})
    if rows:
        with open(os.path.join(OUT, "case_roster.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    return rows


# ------------------------------------------------------------- case decisions
SECTIONS = ("Introduction", "Personal Background", "Background",
            "The Circumstances of the Death", "The Events of the Days Leading up to Death")

DIED = re.compile(
    r"\b(?:died|was found dead|death (?:occurred|took place))\b(?P<where>[^.]{0,220}?)"
    r"\bon\s+(?:\w+day,?\s+)?(?P<date>\d{1,2}\s*(?:st|nd|rd|th)?\s+(?:%s)\s+\d{4})"
    r"(?P<tail>(?:[^.]{0,160}?\bat the age of\s+(?P<age>\d{1,3}))?)" % MONTH, re.I)
WORDNUM = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen twenty".split())}
UNIT_YEARS = {"hour": 1 / 8760, "minute": 1 / 525600, "day": 1 / 365.25,
              "week": 7 / 365.25, "month": 1 / 12, "year": 1.0}
AGE_PATS = [
    re.compile(r"\bat the age of\s+(?:almost |about |nearly |just )?"
               r"(?P<a>\d{1,3}|[a-z]+)\s*(?P<u>hours?|minutes?|days?|weeks?|months?|years?)?", re.I),
    re.compile(r"\bwas aged\s+(?P<a>\d{1,3})\b", re.I),
    re.compile(r"\bwas\s+(?P<a>\d{1,3})\s+years? old\b", re.I),
    re.compile(r"\baged\s+(?P<a>\d{1,3})\b", re.I),
]


def age_of(flat):
    """-> (age_in_years_float_or_'', verbatim_age_text). Infants are given in days/months."""
    for pat in AGE_PATS:
        m = pat.search(flat)
        if not m:
            continue
        raw = m.group("a").lower()
        n = int(raw) if raw.isdigit() else WORDNUM.get(raw)
        if n is None:
            continue
        unit = (m.groupdict().get("u") or "year").rstrip("s").lower()
        txt = f"{raw} {unit}" + ("" if n == 1 else "s")
        return round(n * UNIT_YEARS.get(unit, 1.0), 4), txt
    return "", ""
CERT = re.compile(r"(?:certif\w+|gave|recorded|stated)[^.]{0,140}?cause of (?:her|his|the) death "
                  r"(?:was|as|to be)\s+(?P<cause>[^.]{3,180})\.", re.I)
# The 15 murders Shipman was convicted of at Preston Crown Court, 31 Jan 2000 (public record).
TRIAL_15 = {"marie west", "irene turner", "lizzie adams", "jean lilley", "ivy lomas",
            "muriel grimshaw", "marie quinn", "kathleen wagstaff", "bianka pomfret",
            "norah nuttall", "pamela hillier", "maureen ward", "winifred mellor",
            "joan melia", "kathleen grundy"}

TITLE = re.compile(r"\b(Mrs|Miss|Ms|Mr|Master|Dame|Lady)\s+")
SEX = {"Mrs": "F", "Miss": "F", "Ms": "F", "Dame": "F", "Lady": "F", "Mr": "M", "Master": "M"}


def sex_of(name, flat):
    """The decisions always style the victim 'Mrs/Miss/Mr <name>'. Prefer the full-name
    match; fall back to the surname (relatives can share it, so take the commonest)."""
    m = re.search(r"\b(Mrs|Miss|Ms|Mr|Master)\s+" + re.escape(name) + r"\b", flat)
    if m:
        return m.group(1)
    c = collections.Counter(re.findall(
        r"\b(Mrs|Miss|Ms|Mr|Master)\s+" + re.escape(name.split()[-1]) + r"\b", flat))
    return c.most_common(1)[0][0] if c else ""


CONVICTED = re.compile(r"(?i)(?:was |been )convicted[^.]{0,120}?(?:murder|killing)|convicted (?:of|at (?:his )?trial)[^.]{0,90}?(?:murder|killing)|(?:count|charge)s? of murder[^.]{0,80}?(?:indictment|convicted)")

VERDICTS = [
    ("unlawful killing",
     r"unlawful(?:ly)? kill|"
     r"\bi (?:am (?:satisfied|sure|quite sure|certain)|have no doubt|am in no doubt|have concluded|"
     r"have come to the conclusion)[^.]{0,200}?(?:killed|murdered|lethal (?:injection|dose)|"
     r"responsible for (?:the|her|his) death)|"
     r"shipman (?:probably |deliberately |must have |had )?(?:killed|murdered)\b|"
     r"killed by shipman|(?:killed|murdered) (?:her|him|mrs|mr|miss|ms)[^.]{0,60}?by shipman|"
     r"responsible for the death of|"
     r"(?:gave|administered)[^.]{0,60}?lethal (?:injection|dose)|"
     r"lethal (?:injection|dose)[^.]{0,80}?(?:administered|given) by shipman|"
     r"she was killed|he was killed|was killed by a lethal|result of a lethal injection|lethal injection by shipman"),
    ("natural causes",
     r"\b(?:died|death (?:was|occurred))[^.]{0,60}?(?:of|from|due to) natural causes|"
     r"\bi (?:am satisfied|conclude|find|am sure)[^.]{0,150}?natural (?:causes|death)|"
     r"\bthis was a natural death|died a natural death|death was (?:a )?natural"),
    ("suicide", r"\bsuicide\b|took (?:her|his) own life"),
    ("accidental", r"\baccidental (?:death|overdose)\b"),
    ("cause for suspicion",
     r"cause for (?:some |real |grave |considerable )?suspicion|suspicion (?:remains|attaches)|"
     r"i (?:am|remain) suspicious|suspicion in my mind|might have deliberately|cannot (?:absolutely )?rule out the possibility"),
    ("insufficient evidence",
     r"insufficient evidence|unable to (?:reach|form|express|come to)[^.]{0,50}?(?:conclusion|view|opinion)|"
     r"cannot (?:reach|come to) a (?:firm )?conclusion|no (?:firm )?conclusion (?:is|can be)"),
]


WEEKDAY = re.compile(r"(?i)^(?:on\s+)?(?:Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day\b")


def place_of(d):
    """The 'where' capture occasionally runs into a date clause instead of a place."""
    if not d:
        return ""
    p = re.sub(r"^(at|in)\s+", "", d.group("where").strip(" ,"))
    return "" if WEEKDAY.match(p) else p


def parse_case(f):
    L = lines_of(f)
    start = next((j for j, l in enumerate(L) if l in SECTIONS and j), None)
    if start is None:
        return None
    name = L[start - 1]
    if not re.match(r"^[A-Z][A-Za-z'\-. ]{2,60}$", name):
        return None
    report = next((l for l in L[:start] if re.match(r"^The (First|Second|Third|Fourth|Fifth|Sixth) Report$", l)), "")
    body = "\n".join(L[start:])
    flat = " ".join(L[start:])

    section = ""
    concl = ""
    for head in ("Conclusion", "Conclusions", "Comment", "Decision", "Summary"):
        m = re.search(r"(?s)\n%s\n(.*?)(?:\nClick here\n|\nPrevious\n|\Z)" % head, body)
        if m:
            section, concl = head, m.group(1).strip()
            break

    d = DIED.search(flat[:5000])
    age_years, age_text = age_of(flat[:6000])
    c = CERT.search(flat[:8000])
    # The 15 trial cases are the only decisions written up under "Comment" rather than
    # "Conclusion" — the verdict came from the jury, so the Inquiry only commented.
    convicted = section == "Comment" or name.lower() in TRIAL_15

    hay = re.sub(r"\s+", " ", concl or " ".join(L[-25:])).lower()
    verdict = ""
    for label, pat in VERDICTS:
        if re.search(pat, hay):
            verdict = label
            break
    if convicted:
        verdict = "unlawful killing"

    title = sex_of(name, flat)
    year = int(dt_year.group()) if (dt_year := re.search(r"\b(?:19|20)\d{2}\b",
                                    d.group("date") if d else "")) else ""

    q = os.path.basename(f)
    gid = re.search(r"(?i)id=(D[A-Z])", q)
    fn = re.search(r"(?i)fn=(\d+)", q)
    dt = re.sub(r"(\d)\s*(st|nd|rd|th)\b", r"\1", d.group("date"), flags=re.I).strip() if d else ""
    return {
        "case_group": gid.group(1).upper() if gid else "",
        "case_no": fn.group(1) if fn else "",
        "name": name,
        "title": title,
        "sex": SEX.get(title, ""),
        "report": report,
        "date_of_death": re.sub(r"\s+", " ", dt),
        "year_of_death": year,
        "age_years": age_years,
        "age_text": age_text,
        "place_of_death": place_of(d),
        "certified_cause": (c.group("cause").strip(" '‘’") if c else ""),
        "verdict": verdict,
        "convicted_at_trial": int(convicted),
        "decision_section": section,
        "conclusion": concl,
        "n_words": len(flat.split()),
        "source_file": q,
    }


def main():
    six = parse_tables(f"{RAW}/index/6r_*.html", "sixth_report_deaths.csv")
    print(f"sixth_report_deaths.csv   {len(six)} rows")
    roster = parse_roster()
    print(f"case_roster.csv           {len(roster)} rows")

    cases, seen = [], set()
    for f in sorted(glob.glob(f"{RAW}/case_decisions/*.html")):
        r = parse_case(f)
        if not r:
            continue
        key = (r["case_group"], r["case_no"])
        if key in seen:
            continue
        seen.add(key)
        cases.append(r)
        fn = f"{r['case_group']}{r['case_no']}_{re.sub(r'[^A-Za-z]+', '_', r['name']).strip('_')}.txt"
        open(os.path.join(TXT, fn), "w").write("\n".join(lines_of(f)))
    if cases:
        cols = list(cases[0])
        with open(os.path.join(OUT, "case_decisions.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(cases)
        with open(os.path.join(OUT, "case_decisions.jsonl"), "w") as fh:
            for r in cases:
                fh.write(json.dumps(r) + "\n")
    print(f"case_decisions.csv        {len(cases)} rows")
    miss = {k: sum(1 for r in cases if not r[k]) for k in ("date_of_death", "age_years", "verdict", "certified_cause")}
    print("  blank fields:", miss)
    print("  verdicts:", dict(collections.Counter(r["verdict"] for r in cases)))


if __name__ == "__main__":
    main()
