"""Galton's 1886 family heights (HistData::GaltonFamilies via Rdatasets) -> sons only."""
import csv, io, urllib.request
from pathlib import Path

URL = "https://vincentarelbundock.github.io/Rdatasets/csv/HistData/GaltonFamilies.csv"
out = Path(__file__).parent / "derived/galton_sons.csv"
out.parent.mkdir(exist_ok=True)
rows = csv.DictReader(io.StringIO(urllib.request.urlopen(URL).read().decode()))
with open(out, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["father", "son"])
    for r in rows:
        if r["gender"] == "male":
            w.writerow([r["father"], r["childHeight"]])
print("wrote", out)
