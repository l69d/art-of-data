#!/usr/bin/env python3
"""Emit the age-vs-year scatter points from case_decisions.csv."""
import csv, json, os, datetime, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "derived", "case_decisions.csv")
DST = os.path.join(ROOT, "derived", "plot_points.json")

MON = {m: i + 1 for i, m in enumerate(
    "January February March April May June July August September October November December".split())}
MON.update({m[:3]: i + 1 for i, m in enumerate(MON)})

def to_date(s):
    p = s.split()
    if len(p) != 3 or p[1] not in MON:
        return None
    try:
        return datetime.date(int(p[2]), MON[p[1]], int(p[0]))
    except ValueError:
        return None

pts, skipped = [], collections.Counter()
for r in csv.DictReader(open(SRC)):
    d = to_date(r["date_of_death"])
    if not d:
        skipped["no date"] += 1; continue
    if not r["age_years"] or not r["sex"]:
        skipped["no age" if not r["age_years"] else "no sex"] += 1; continue
    doy = d.timetuple().tm_yday
    pts.append({
        "n": r["name"],
        "s": r["sex"],
        "x": round(d.year + (doy - 0.5) / (366 if d.year % 4 == 0 else 365), 4),
        "y": float(r["age_years"]),
        "at": r["age_text"],
        "d": d.isoformat(),
        "v": r["verdict"] or "unclassified",
        "c": r["certified_cause"],
        "p": r["place_of_death"][:70],
        "t": int(r["convicted_at_trial"]),
    })

pts.sort(key=lambda p: p["x"])
json.dump(pts, open(DST, "w"), separators=(",", ":"))
print(f"{len(pts)} points -> {DST}   skipped {dict(skipped)}")
print("  sex:", dict(collections.Counter(p['s'] for p in pts)))
print("  verdict:", dict(collections.Counter(p['v'] for p in pts)))
print("  convicted at trial:", sum(p['t'] for p in pts))
