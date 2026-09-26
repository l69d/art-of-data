"""Datasaurus Dozen (Matejka & Fitzmaurice 2017) via the datasauRus R package -> 5 sets."""
import csv, io, urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/jumpingrivers/datasauRus/HEAD/inst/extdata/DatasaurusDozen-Long.tsv"
KEEP = {"dino", "star", "circle", "bullseye", "x_shape"}
out = Path(__file__).parent / "derived/datasaurus.csv"
rows = csv.DictReader(io.StringIO(urllib.request.urlopen(URL).read().decode()), delimiter="\t")
with open(out, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["dataset", "x", "y"])
    for r in rows:
        if r["dataset"] in KEEP:
            w.writerow([r["dataset"], r["x"], r["y"]])
print("wrote", out)
