// Chalkboard checks (site/playcalls.js and the call wrapper of site/stage.js), run by check_calls.py: node engine/check_calls.js box.json
// For every run, pass, sack and try of every game: a call is made, it fits the logged result, it is the same every time, the formation is on the field with no two dots on one spot,
// all 22 players have an assignment, and the scene built with the call ends where the log says, with the same banners and name tags as the scene without it.
const fs = require("fs"), path = require("path");
const ST = require(path.join(__dirname, "..", "site", "stage.js")), CALLS = require(path.join(__dirname, "..", "site", "playcalls.js"));
global.window = global; global.DFLCalls = CALLS;                 // stage.js looks for the calls on its root
const PB = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "playbook.json"), "utf8")); CALLS.use(PB);
const { box } = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const ARCH = ["Gambler", "Innovator", "Disciplinarian", "Steady Hand", "Survivor", "Tactician", "Developer", "Players' Coach"];
const COVER = new Set(["zone", "deep", "man", "spy", "drop"]), RUSH = new Set(["rush", "blitz", "attack"]);
let plays = 0, called = 0, bad = [], byCall = {}, byDef = {}, nulls = 0, minGap = 99;
const fail = (gid, i, P, why) => { if (bad.length < 10) bad.push(`${gid}#${i} ${P[6]} ${why}`); };
const textOf = S => JSON.stringify(S.ev.map(e => [e.k, e.text || "", e.sub || "", e.a == null ? "" : e.a]).sort());
for (const [gid, b] of Object.entries(box)) {
  const pl = b.p, n = pl.length;
  let gh = 0; for (const ch of gid) gh = (Math.imul(gh, 31) + ch.charCodeAt(0)) | 0;
  pl.forEach((P, i) => {
    const kind = P[6]; if (!["RU", "PC", "PI", "IN", "SK", "2P"].includes(kind)) return;
    plays++;
    const nx = pl[i + 1], same = nx && nx[13] === P[13] ? nx : null, TRY = r => r && (r[6] === "XP" || r[6] === "2P");
    let j = i; while (pl[j + 1] && pl[j + 1][13] === P[13] && TRY(pl[j + 1])) j++;
    const last = !pl[j + 1] || pl[j + 1][13] !== P[13], hint = nx && nx[13] !== P[13] ? (nx[0] === P[0] ? nx[3] : 100 - nx[3]) : null;
    const base = { nm: k => b.pl[k] || null, hint, dr: last ? b.dr[P[13]] : null, next: same, abbr: ["HOM", "AWY"], pen: "Test" };
    const mk = () => ({ sit: CALLS.situation(pl, b.dr, i), oc: { name: "Oc", arch: ARCH[(gh + P[0]) & 7] }, dc: { name: "Dc", arch: ARCH[(gh >> 3) & 7] }, seed: gh, rate: null });
    let S0, S1, S2;
    try { S0 = ST.buildScene(P, base); S1 = ST.buildScene(P, { ...base, chalk: mk() }); S2 = ST.buildScene(P, { ...base, chalk: mk() }); } catch (e) { return fail(gid, i, P, "threw " + e.message); }
    const c = S1.call; if (!c) { nulls++; return fail(gid, i, P, "no call"); }
    called++; byCall[c.off.id] = (byCall[c.off.id] || 0) + 1; byDef[c.def.id] = (byDef[c.def.id] || 0) + 1;
    if (JSON.stringify(c) !== JSON.stringify(S2.call)) return fail(gid, i, P, "the call is not repeatable");
    // the call fits the result
    const k2 = kind === "2P" ? (P[8] >= 0 ? "PC" : "RU") : kind;
    if ((k2 === "RU") !== (c.off.type === "run")) fail(gid, i, P, `a ${c.off.type} call (${c.off.id}) for a ${kind}`);
    const OJ = CALLS.OJ, DJ = CALLS.DJ;
    const S0used = [...S0.H.used], sj = S0used.length ? S0used[0] : -1;
    if (k2 === "SK" && sj >= 0 && !RUSH.has(c.plan.d[sj].act)) fail(gid, i, P, `a sack by a defender whose call (${c.def.id}) has him ${c.plan.d[sj].act}`);
    if (kind === "IN" && sj >= 0 && !COVER.has(c.plan.d[sj].act)) fail(gid, i, P, `an interception by a defender whose call (${c.def.id}) has him ${c.plan.d[sj].act}`);
    const named = S0.ev.filter(e => e.k === "tag").map(e => e.a), tgt = named.find(f => Math.floor(f / 11) === S0.off && f !== S0.O(9));
    if ((k2 === "PC" || kind === "PI" || kind === "IN") && tgt != null) { const a = c.plan.o[tgt - S0.off * 11]; if (!a || !["route", "fake_route"].includes(a.act) || !a.pts.length) fail(gid, i, P, `the receiver has no route in ${c.off.id}`); }
    // the formation is on the field, nobody on another's spot
    const all = [...c.at.o.map((p, k) => ["o" + k, p]), ...c.at.d.map((p, k) => ["d" + k, p])];
    if (c.plan.o.length !== 11 || c.plan.d.length !== 11 || c.at.o.length !== 11 || c.at.d.length !== 11) return fail(gid, i, P, "not 22 assignments");
    for (const [nm, p] of all) if (!(p[0] >= -14 && p[0] <= 20 && p[1] >= .5 && p[1] <= 52.8)) fail(gid, i, P, `${nm} lines up off the field at ${p}`);
    for (let a = 0; a < 22; a++) for (let d = a + 1; d < 22; d++) { const g = Math.hypot(all[a][1][0] - all[d][1][0], all[a][1][1] - all[d][1][1]); if (g < minGap) minGap = g; if (g < .45) { fail(gid, i, P, `${all[a][0]} and ${all[d][0]} stand ${g.toFixed(2)} yd apart (${c.off.align}/${c.def.align})`); a = 99; break; } }
    for (const side of [c.plan.o, c.plan.d]) for (const a of side) for (const p of a.pts) if (!isFinite(p[0]) || !isFinite(p[1])) fail(gid, i, P, "a non-finite assignment point");
    // the scene with the call ends where the scene without it does, and says the same words
    if (Math.abs(ST.endSpot(S1) - ST.endSpot(S0)) > .05) fail(gid, i, P, `the call moved the end of the play: ${ST.endSpot(S1).toFixed(2)} against ${ST.endSpot(S0).toFixed(2)}`);
    if (textOf(S0) !== textOf(S1)) fail(gid, i, P, "the banners or name tags changed with the call");
    for (const tr of S1.tr) { let pt = -1; for (const kf of tr) { if (!isFinite(kf[0]) || !isFinite(kf[1]) || !isFinite(kf[2])) return fail(gid, i, P, "not finite"); if (kf[0] < pt) return fail(gid, i, P, "keyframes out of order"); pt = kf[0]; if (kf[1] < -6 || kf[1] > 126 || kf[2] < 0 || kf[2] > 53.4) return fail(gid, i, P, `off the field: ${kf.map(x => typeof x === "number" ? +x.toFixed(1) : x)} fig ${S1.tr.indexOf(tr)} ${c.off.id}/${c.def.id}`); } }
    for (let t = 0; t <= S1.dur; t += S1.dur / 12) { const s = ST.sampleScene(S1, t); if (s.act.some(a => !isFinite(a.x) || !isFinite(a.y)) || !isFinite(s.ball.x)) return fail(gid, i, P, "cannot be sampled"); }
    if (Math.abs(S1.dur - S0.dur) > .6) fail(gid, i, P, `duration ${S1.dur.toFixed(1)} against ${S0.dur.toFixed(1)}`);
    if (S1.tAct == null) fail(gid, i, P, "no moment for the cues");
  });
}
console.log(JSON.stringify({ plays, called, nulls, byCall, byDef, minGap: +minGap.toFixed(2), bad }));
process.exit(bad.length ? 1 : 0);
