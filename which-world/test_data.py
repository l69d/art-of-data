import csv, statistics as s
from pathlib import Path
from collections import defaultdict

D = Path(__file__).parent / "derived"
rows = list(csv.DictReader(open(D / "galton_sons.csv")))
f, c = [float(r["father"]) for r in rows], [float(r["son"]) for r in rows]
assert len(rows) == 481
assert abs(s.linear_regression(f, c).slope - 0.45) < 0.01 and abs(s.correlation(f, c) - 0.39) < 0.01

sets = defaultdict(list)
for r in csv.DictReader(open(D / "datasaurus.csv")):
    sets[r["dataset"]].append((float(r["x"]), float(r["y"])))
assert sorted(sets) == ["bullseye", "circle", "dino", "star", "x_shape"], sorted(sets)
for k, v in sets.items():
    x, y = [p[0] for p in v], [p[1] for p in v]
    assert len(v) == 142
    assert abs(s.mean(x) - 54.26) < .02 and abs(s.mean(y) - 47.83) < .02, k
    assert abs(s.stdev(x) - 16.77) < .02 and abs(s.stdev(y) - 26.94) < .02, k
    assert abs(s.correlation(x, y) + .065) < .01, k
print("ok", len(rows), {k: len(v) for k, v in sets.items()})
