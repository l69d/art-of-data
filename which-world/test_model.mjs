// Checks the numbers index.html shows against the books. Run: node which-world/test_model.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const src = html.match(/<script id="model">([\s\S]*?)<\/script>/)[1];
const m = new Function(src + "; return {crowd, share, screen, fit, turkey, bombers, bomberCounts, HEAVIEST_KG, RICHEST_USD, BACON, DINO, dinoRow};")();

const c = m.crowd();
assert.equal(c.weight.length, 1000);
const w = m.share(m.HEAVIEST_KG, c.weight);
assert.ok(w > 0.004 && w < 0.006, `weight share ${w}`);
assert.equal((m.share(m.RICHEST_USD, c.wealth) * 100).toFixed(1), "99.9");

const s = m.screen(1000, 0.01);
assert.deepEqual([s.ill, s.tp, s.fp, s.pos], [10, 9, 99, 108]);
assert.equal(Math.round(s.ppv * 100), 8);
assert.ok(Number.isFinite(m.screen(1000, 0.001).ppv) && Number.isFinite(m.screen(1000, 0.5).ppv));

const t = m.turkey();
assert.equal(t.confidence.length, 1000);
assert.ok(t.confidence[999] > 0.99 && t.confidence[0] < 0.7);
// Plate V: bacon's 18% headline is 6 -> 7 in 100
assert.equal(Math.round(m.BACON.base * (1 + m.BACON.rel)), 7);

// Plate IV: inlined Datasaurus sets match the CSV and share their means
const dcsv = readFileSync(new URL("./derived/datasaurus.csv", import.meta.url), "utf8").trim().split("\n").slice(1);
assert.equal(Object.values(m.DINO).reduce((n, a) => n + a.length, 0), dcsv.length, "inlined Datasaurus out of sync with CSV");
for (const k of ["dino", "star", "circle", "bullseye", "x_shape"]) {
  const a = m.DINO[k], mx = a.reduce((q, p) => q + p[0], 0) / a.length, my = a.reduce((q, p) => q + p[1], 0) / a.length;
  assert.equal(a.length, 142); assert.ok(Math.abs(mx - 54.26) < .02 && Math.abs(my - 47.83) < .02, k);
}
// Plate IV's table must show identical figures in every row, as the plate claims
const rows = ["dino", "star", "circle", "bullseye", "x_shape"].map(k => m.dinoRow(k).join(" "));
assert.ok(rows.every(r => r === rows[0]), "Datasaurus table rows differ: " + rows.join(" | "));
// Plate I: Wald's bombers. Returning planes hide the engine hits that brought the others down
const B = m.bombers(), share = hs => hs.filter(h => h.zone === "engines").length / hs.length;
assert.equal(B.returned + B.lost, 200);
const back = B.hits.filter(h => !h.lost), gone = B.hits.filter(h => h.lost);
assert.ok(share(back) < .6 * share(B.hits), `engine share on returners ${share(back)} vs all ${share(B.hits)}`);
assert.ok(share(gone) > share(back));
// the bullet count: per plane, engines are hit far more on the planes that never came back; elsewhere the two groups match
const K = m.bomberCounts(m.bombers());
assert.ok(K.engines.lost > 3 * K.engines.back, `engines ${K.engines.back} vs ${K.engines.lost}`);
for (const z of ["fuselage", "rest"]) assert.ok(K[z].lost / K[z].back > .8 && K[z].lost / K[z].back < 1.25, z);
assert.equal(K.engines.back.toFixed(1), "0.2"); assert.equal(K.engines.lost.toFixed(1), "1.0");
console.log("model ok");
