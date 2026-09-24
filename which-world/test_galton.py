import csv, statistics as s
from pathlib import Path

rows = list(csv.DictReader(open(Path(__file__).parent / "derived/galton_sons.csv")))
f = [float(r["father"]) for r in rows]
c = [float(r["son"]) for r in rows]
assert len(rows) == 481, len(rows)
assert abs(s.linear_regression(f, c).slope - 0.45) < 0.01
assert abs(s.correlation(f, c) - 0.39) < 0.01
print("ok", len(rows))
