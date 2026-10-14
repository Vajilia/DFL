// Scene checks for site/stage.js, run by check_stage.py: node engine/check_stage.js box.json
// Every play of every game builds a scene, and the scene ends where the log says.
const fs = require("fs"), path = require("path");
const ST = require(path.join(__dirname, "..", "site", "stage.js"));
const { box, kinds } = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
let plays = 0, bad = [], byKind = {}, maxDur = 0, minDur = 99, tagBad = 0, frames = 0;
const fail = (gid, i, P, why) => { if (bad.length < 8) bad.push(`${gid}#${i} ${P[6]} ${why}`); };
for (const [gid, b] of Object.entries(box)) {
  const pl = b.p;
  pl.forEach((P, i) => {
    const nx = pl[i + 1], same = nx && nx[13] === P[13] ? nx : null, TRY = r => r && (r[6] === "XP" || r[6] === "2P");
    let j = i; while (pl[j + 1] && pl[j + 1][13] === P[13] && TRY(pl[j + 1])) j++;
    const last = !pl[j + 1] || pl[j + 1][13] !== P[13], hint = nx && nx[13] !== P[13] ? (nx[0] === P[0] ? nx[3] : 100 - nx[3]) : null;
    const names = new Set([P[7], P[8], P[9]].filter(j => j >= 0 && b.pl[j]).map(j => b.pl[j][0]));
    let S;
    try { S = ST.buildScene(P, { nm: j => b.pl[j] || null, hint, dr: last ? b.dr[P[13]] : null, next: same, abbr: ["HOM", "AWY"], pen: "Test" }); } catch (e) { return fail(gid, i, P, "threw " + e.message); }
    plays++; byKind[P[6]] = (byKind[P[6]] || 0) + 1;
    // finite, ordered, on the field
    for (const tr of S.tr) { let pt = -1; for (const k of tr) { if (!isFinite(k[0]) || !isFinite(k[1]) || !isFinite(k[2])) return fail(gid, i, P, "not finite"); if (k[0] < pt) return fail(gid, i, P, "out of order"); if (k[1] < -4.01 || k[1] > 124.01 || k[2] < 0 || k[2] > 53.3) return fail(gid, i, P, "off the field"); pt = k[0]; } }
    if (!(S.dur > .5 && S.dur < 25)) return fail(gid, i, P, "duration " + S.dur);
    maxDur = Math.max(maxDur, S.dur); minDur = Math.min(minDur, S.dur);
    // every figure and the ball can be sampled all along
    for (let t = 0; t <= S.dur; t += S.dur / 12) { const s = ST.sampleScene(S, t); frames++; if (s.act.some(a => !isFinite(a.x) || !isFinite(a.y)) || !isFinite(s.ball.x) || !isFinite(s.ball.y) || !isFinite(s.ball.z)) return fail(gid, i, P, "sample at " + t); }
    // the end of the play is the end the log gives
    const [off, , , pos, yds, to, kind] = P, e = ST.endSpot(S);
    if ((kind === "RU" || kind === "PC" || kind === "SK") && !to) {
      const td = pos + yds >= 100 && kind !== "SK";
      if (td ? e < 100 : Math.abs(e - (pos + yds)) > .8) fail(gid, i, P, `ends at ${e.toFixed(1)}, the log says ${pos + yds}`);
    }
    if (kind === "PN" && Math.abs(e - Math.max(1, Math.min(99, pos + yds))) > .8) fail(gid, i, P, `flag moves the ball to ${e.toFixed(1)}, the log says ${pos + yds}`);
    if (kind === "TO" && Math.abs(e - pos) > .8) fail(gid, i, P, "a timeout moved the ball");
    if (kind === "IJ" && Math.abs(e - pos) > .8) fail(gid, i, P, "an injury moved the ball");
    if (kind === "KN" && Math.abs(e - (pos - 1)) > .8) fail(gid, i, P, `a kneel ends at ${e.toFixed(1)}, the log says ${pos - 1}`);
    if (kind === "SP" && Math.abs(e - pos) > 4) fail(gid, i, P, `a spike ends at ${e.toFixed(1)}`);
    if (kind === "FG") { const eb = ST.endBall(S), through = e >= 110 && Math.abs(eb.y - ST.MID) < 3.1; if (through !== (P[8] === 1)) fail(gid, i, P, `field goal ends at ${e.toFixed(1)}, ${eb.y.toFixed(1)} across, the log says good: ${P[8]}`); }
    const res = last && b.dr[P[13]] ? b.dr[P[13]][6] : "";
    if (kind === "KO") {                                                      // a kickoff ends where the next drive starts (the receivers' start spot in the kicking frame); a return touchdown ends in the kickers' end zone
      const kpos = P[1] === 2 ? 20 : 35, want = (P[5] === 3 || P[5] === 5) ? pos : 100 - pos;
      if (P[5] === 2 ? e > 0 : P[5] === 0 ? e < 90 : Math.abs(e - want) > 1.5) fail(gid, i, P, `a kickoff (outcome ${P[5]}) ends at ${e.toFixed(1)}, the log says ${want}`);
      if (S.off !== ((P[5] === 3 || P[5] === 5) ? off : 1 - off)) fail(gid, i, P, "a kickoff is run from the wrong side");
    }
    if (kind === "XP") { const eb = ST.endBall(S), through = e >= 110 && Math.abs(eb.y - ST.MID) < 3.1; if (through !== (P[8] === 1)) fail(gid, i, P, `extra point ends at ${e.toFixed(1)}, the log says good: ${P[8]}`); }
    if (kind === "2P" && (P[9] === 1 || P[8] < 0) && (P[9] === 1) !== (e >= 100)) fail(gid, i, P, `a two-point try ends at ${e.toFixed(1)}, the log says good: ${P[9]}`);
    if ((kind === "IN" || (to === 2 && kind !== "KO")) && hint != null && !["INT_TD", "FUMBLE_TD"].includes(res) && Math.abs(e - hint) > 1.5) fail(gid, i, P, `turnover ends at ${e.toFixed(1)}, the next possession starts at ${hint}`);
    if ((kind === "IN" || (to === 2 && kind !== "KO")) && ["INT_TD", "FUMBLE_TD"].includes(res) && e > 0) fail(gid, i, P, `a return touchdown ends at ${e.toFixed(1)}, not in the offense's own end zone`);
    if (kind === "PU" && hint != null && pos + yds < 100 && Math.abs(e - hint) > 1.5) fail(gid, i, P, `punt return ends at ${e.toFixed(1)}, the next possession starts at ${hint}`);
    // a name tag names someone in the play
    for (const ev of S.ev) if (ev.k === "tag" && ev.text && !names.has(ev.text)) tagBad++;
    // banner words: a touchdown is announced only when the log scored one
    for (const ev of S.ev) if (ev.k === "banner" && ev.text === "TOUCHDOWN" && !(kind === "RU" || kind === "PC")) fail(gid, i, P, "touchdown banner on a " + kind);
  });
}
console.log(JSON.stringify({ plays, frames, byKind, maxDur: +maxDur.toFixed(1), minDur: +minDur.toFixed(1), tagBad, bad }));
process.exit(bad.length || tagBad ? 1 : 0);
