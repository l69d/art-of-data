// Checks the numbers index.html shows against the books. Run: node which-world/test_model.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const src = html.match(/<script id="model">([\s\S]*?)<\/script>/)[1];
const m = new Function(src + "; return {crowd, share, screen, fit, turkey, GALTON, HEAVIEST_KG, RICHEST_USD, survivors, lasted, districts, limit, BACON, DINO};")();

const c = m.crowd();
assert.equal(c.weight.length, 1000);
const w = m.share(m.HEAVIEST_KG, c.weight);
assert.ok(w > 0.004 && w < 0.006, `weight share ${w}`);
assert.equal((m.share(m.RICHEST_USD, c.wealth) * 100).toFixed(1), "99.9");

const s = m.screen(1000, 0.01);
assert.deepEqual([s.ill, s.tp, s.fp, s.pos], [10, 9, 99, 108]);
assert.equal(Math.round(s.ppv * 100), 8);
assert.ok(Number.isFinite(m.screen(1000, 0.001).ppv) && Number.isFinite(m.screen(1000, 0.5).ppv));

const csv = readFileSync(new URL("./derived/galton_sons.csv", import.meta.url), "utf8").trim().split("\n").slice(1);
assert.equal(m.GALTON.length, csv.length, "inlined Galton data out of sync with CSV");
const g = m.fit(m.GALTON.map(p => p[0]), m.GALTON.map(p => p[1]));
assert.ok(Math.abs(g.slope - 0.45) < 0.01 && Math.abs(g.r - 0.39) < 0.01);

const t = m.turkey();
assert.equal(t.confidence.length, 1000);
assert.ok(t.confidence[999] > 0.99 && t.confidence[0] < 0.7);
// Plate III: 1,024 managers, one per possible 10-year record
assert.equal(m.survivors(0).length, 1024);
for (let y = 1; y <= 10; y++) assert.equal(m.survivors(y).length, 1024 >> y);
assert.deepEqual(m.survivors(10), [1023]);
assert.equal(m.lasted(1023), 10); assert.equal(m.lasted(0), 0);

// Plate V: the top of the league table is noise, the real outlier ranked lower
const ds = m.districts(), top = [...ds].sort((a, b) => b.rate - a.rate)[0], out = ds.find(d => d.id === 0);
assert.equal(ds.length, 380);
assert.notEqual(top.id, 0, "top of the table must not be the real outlier");
assert.ok(top.rate < m.limit(top.pop, 3.09), "top of the table inside 99.8%");
assert.ok(out.rate > m.limit(out.pop, 3.09), "outlier outside 99.8%");
assert.equal(ds.filter(d => d.rate > m.limit(d.pop, 3.09)).length, 1, "only one district above 99.8%");

// Plate VI: bacon's 18% headline is 6 -> 7 in 100
assert.equal(Math.round(m.BACON.base * (1 + m.BACON.rel)), 7);

// Plate IV: inlined Datasaurus sets match the CSV and share their means
const dcsv = readFileSync(new URL("./derived/datasaurus.csv", import.meta.url), "utf8").trim().split("\n").slice(1);
assert.equal(Object.values(m.DINO).reduce((n, a) => n + a.length, 0), dcsv.length, "inlined Datasaurus out of sync with CSV");
for (const k of ["dino", "star", "circle", "bullseye", "x_shape"]) {
  const a = m.DINO[k], mx = a.reduce((q, p) => q + p[0], 0) / a.length, my = a.reduce((q, p) => q + p[1], 0) / a.length;
  assert.equal(a.length, 142); assert.ok(Math.abs(mx - 54.26) < .02 && Math.abs(my - 47.83) < .02, k);
}
console.log("model ok");
