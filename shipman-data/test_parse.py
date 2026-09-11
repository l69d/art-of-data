#!/usr/bin/env python3
"""Invariants for the parsers. Run after parse.py / reporttext.py / plotdata.py."""
import csv, json, glob, collections

cases = list(csv.DictReader(open("derived/case_decisions.csv")))
assert len(cases) == 558, len(cases)
assert sum(int(c["convicted_at_trial"]) for c in cases) == 15   # Preston Crown Court, 2000
assert all(c["sex"] in ("F", "M") for c in cases)                # honorific resolved every case

pts = json.load(open("derived/plot_points.json"))
assert len(pts) == 531, len(pts)
assert all(1970 <= p["x"] <= 1999 and 0 < p["y"] <= 110 for p in pts)

for f in glob.glob("derived/report_text/*.txt"):                 # ch=/ID= views overlap heavily
    L = [l for l in open(f) if len(l.split()) > 8]
    assert len(set(L)) / len(L) > 0.98, (f, len(set(L)), len(L))  # no wholesale re-emission

print("ok", len(cases), "cases,", len(pts), "points,", len(glob.glob("derived/report_text/*.txt")), "reports")
