// Checks the numbers index.html shows against the books. Run: node which-world/test_model.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const src = html.match(/<script id="model">([\s\S]*?)<\/script>/)[1];
const m = new Function(src + "; return {crowd, share, screen, fit, turkey, GALTON, HEAVIEST_KG, RICHEST_USD};")();

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
console.log("model ok");
