/* The DFL play calls: for each play of the log, the call each coordinator most likely made, and what each of the 22 players was told to do (site/playcalls.js).

   This is a reconstruction. The engine decides every result first (who ran or threw, how far, how it ended); nothing here changes one, and the engine, the media and the
   coordinators' own records never read it. Given what happened, this module picks the most likely call that fits it, weighting each call in the playbook (data/playbook.json) by the
   situation (down, distance, field position, score, time, timeouts) and by the coordinator's temperament, then writes out the 22 players' assignments for the call.
   Pure and repeatable: the same play with the same context gives the same call, on every machine (a seeded generator, no clock, no page).

     DFLCalls.use(playbook)                     give it the playbook (the page embeds data/playbook.json)
     DFLCalls.situation(plays, drives, i)       the score, clock and timeouts as play i begins
     DFLCalls.choose(P, sit, info)              the call for play P: {off, def, at, plan, why, ...} or null for plays that have no call (kicks, flags, timeouts)
   info: { oc, dc: {name, arch} the two coordinators; tj: the figure job the log's receiver stood in; sj: the defender job that made the sack, the interception or the tackle;
           ij: the job that intercepted; seed; rate(side, job): the player's rating or null }                                                                                          */
(function (root) {
"use strict";
const FW = 53.3, MID = 26.65;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
function rng(seed) { let s = (seed >>> 0) || 1; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
let PB = null;
const use = pb => { PB = pb; };
const OJ = ["C", "LG", "RG", "LT", "RT", "TE", "W1", "W2", "W3", "QB", "RB"], DJ = ["DT1", "DT2", "DEL", "DER", "LB1", "LB2", "NB", "CB1", "CB2", "S1", "S2"];
const OLG = { C: "OL", LG: "OL", RG: "OL", LT: "OL", RT: "OL" };
const RUSHERS = new Set(["rush", "blitz", "attack"]), COVERS = new Set(["zone", "deep", "man", "spy", "drop"]);

/* ---------- the situation as a play begins ---------- */
/* plays: the game's rows; drives: its drive records [side, quarter, start, plays, yards, secs, result, pts, def_pts]. Points are counted when a drive ends, so a try is given the touchdown's six. */
function situation(plays, drives, i) {
  const P = plays[i], off = P[0], di = P[13];
  const sc = [0, 0];
  for (let d = 0; d < di && d < drives.length; d++) { const r = drives[d]; sc[r[0]] += r[7]; sc[1 - r[0]] += r[8]; }
  if (P[6] === "XP" || P[6] === "2P") sc[off] += 6;
  const half2 = P[10] >= 3 || P[12];
  return { diff: sc[off] - sc[1 - off], score: sc, q: P[10], left: P[11], ot: P[12], to: P.length > 16 ? [P[15 + off], P[15 + 1 - off]] : null, half2 };
}

function tagsFor(P, sit) {
  const [off, down, toGo, pos, , , kind] = P, t = new Set();
  t.add(["first", "second", "third", "fourth"][clamp(down, 1, 4) - 1]);
  t.add(toGo <= 3 ? "short" : toGo <= 7 || down === 1 ? "medium" : "long");        // first and ten is the ordinary distance, not a long one
  if (pos <= 10) t.add("backed_up"); if (pos >= 80) t.add("redzone"); if (pos >= 95) t.add("goal");
  if (kind === "2P") t.add("try");
  if (sit) {
    const late = (sit.q === 4 && sit.left <= 300) || (sit.q === 2 && sit.left <= 120) || (sit.q >= 5);
    if (sit.diff < 0) t.add("trailing"); if (sit.diff > 0) t.add("leading");
    if (late) { t.add("late"); if (sit.diff < 0) { t.add("trailing_late"); t.add("off_trailing_late"); } if (sit.diff > 0) { t.add("leading_late"); t.add("off_leading_late"); } }
    if (sit.half2 && sit.diff >= 17) t.add("blowout");
    if (sit.half2 && sit.diff <= -17) t.add("trailing_big");
    if (sit.to && sit.to[0] === 0) t.add("no_timeouts");
  }
  return t;
}

/* ---------- picking a call ---------- */
function weight(call, tags, temper, sharp) {
  const f = call.fit || {};
  if (call.off) return 0;
  if (call.only && !call.only.some(x => tags.has(x))) return 0;
  let w = f.base == null ? 1 : f.base;
  for (const k in f) if (k !== "base" && tags.has(k)) w *= Math.pow(f[k], sharp);
  const m = temper && temper[call.style]; if (m) w *= m;
  return w;
}
function pick(R, items) {                                           // items: [[value, weight]]
  const tot = items.reduce((s, x) => s + x[1], 0); if (tot <= 0) return null;
  let r = R() * tot; for (const [v, w] of items) { r -= w; if (r <= 0) return v; }
  return items[items.length - 1][0];
}

/* how the result the engine logged tilts which call it was (the posterior: a call that would not have produced this is unlikely) */
function offOutcome(id, call, P) {
  const [, , toGo, , yds, to, kind] = P; let m = 1;
  const big = yds >= 20, short = yds <= 4;
  if (kind === "RU") {
    if (yds >= 12) m *= { outside_zone: 1.4, counter: 1.6, toss: 1.3, power: 1.2 }[id] || 1;
    if (yds <= 0) m *= { toss: 0.7, counter: 0.7, inside_zone: 1.1 }[id] || 1;
    if (toGo <= 2 && yds >= 0) m *= { power: 1.2, inside_zone: 1.2 }[id] || 1;
  } else if (kind === "SK") {
    m *= { quick: 0.15, screen: 0.1, curl_flat: 0.6, verticals: 1.8, play_action: 1.4, dig: 1.4, rollout: 0.9 }[id] || 1;
  } else if (kind === "IN") {
    m *= { quick: 0.6, screen: 0.3, verticals: 1.5, dig: 1.4, play_action: 1.2 }[id] || 1;
  } else if (kind === "PC") {
    if (big) m *= { verticals: 2.2, play_action: 1.7, dig: 1.3, screen: 1.2, quick: 0.6, curl_flat: 0.5 }[id] || 1;
    if (short) m *= { quick: 1.4, curl_flat: 1.3, screen: 1.3, verticals: 0.25, play_action: 0.8 }[id] || 1;
  } else if (kind === "PI") {
    m *= { verticals: 1.2, dig: 1.1, screen: 0.5 }[id] || 1;
  }
  return m;
}
function defOutcome(id, call, P, info) {
  const [, , toGo, , yds, to, kind] = P; let m = 1;
  if (kind === "RU") {
    if (yds >= 15) m *= { goal_line: 0.1, run_blitz: 0.4, cover0_blitz: 1.4, prevent: 1.3, cover4: 1.3 }[id] || 1;
    if (yds <= 0) m *= { goal_line: 1.6, run_blitz: 1.8, cover2: 0.8, prevent: 0.3 }[id] || 1;
  } else if (kind === "PC") {
    if (yds >= 20) m *= { cover0_blitz: 1.3, cover1_man: 1.1, prevent: 0.3, run_blitz: 0.2, goal_line: 0.1 }[id] || 1;
    if (yds <= 6) m *= { prevent: 1.7, cover2: 1.2, run_blitz: 0.5 }[id] || 1;
  } else if (kind === "SK") {
    m *= { cover0_blitz: 1.6, zone_blitz: 1.5, run_blitz: 0.3, goal_line: 0.1 }[id] || 1;
  }
  const plan = call.plan, jn = info.sj != null && info.sj >= 0 ? DJ[info.sj] : null;
  if (jn && plan[jn]) {
    const act = plan[jn].act;
    if (kind === "SK" && !RUSHERS.has(act)) m = 0;                                            // the sack came from a rusher
    if (kind === "IN" && !COVERS.has(act)) m = 0;                                             // the pick came from a defender in coverage
    if (kind === "PC" && RUSHERS.has(act)) m *= 0.15;                                         // a rusher rarely makes the tackle on a catch
  }
  return m;
}

function choose(P, sit, info) {
  if (!PB) throw new Error("DFLCalls.use(playbook) first");
  info = info || {};
  let [off, down, toGo, pos, yds, to, kind, a, bb, c] = P;
  if (kind === "2P") kind = bb >= 0 ? (c === 1 ? "PC" : "PI") : "RU";
  const isRun = kind === "RU", isPass = kind === "PC" || kind === "PI" || kind === "IN" || kind === "SK";
  if (!isRun && !isPass) return null;
  const P2 = [off, down, toGo, pos, yds, to, kind, a, bb, c];
  const R = rng(((info.seed | 0) * 2654435761 + ((P[14] | 0) + 1) * 40503 + (pos + 1) * 131 + (yds + 80) * 17) >>> 0);
  const tags = tagsFor(P, sit);
  const ot = PB.temperament[(info.oc || {}).arch] || {}, dt = PB.temperament[(info.dc || {}).arch] || {};
  const O = PB.offense, D = PB.defense;
  // offense
  const tj = info.tj != null ? info.tj : -1;
  const oc = [];
  for (const id in O.calls) {
    const call = O.calls[id]; if (call.type !== (isRun ? "run" : "pass")) continue;
    let w = weight(call, tags, ot, ot.sharp || 1); if (w <= 0) continue;
    if (isPass && tj >= 0) {
      const asg = call.plan[OJ[tj]] || call.plan[OLG[OJ[tj]]]; if (!asg || asg.act !== "route") continue;     // the log's receiver has a route in the call
      if (id === "screen" && tj !== 10) continue;
    }
    w *= offOutcome(id, call, P2);
    if (w > 0) oc.push([id, w]);
  }
  const oid = pick(R, oc); if (!oid) return null;
  const ocall = O.calls[oid];
  const oal = pick(R, ocall.align.map(x => [x, 1]));
  // defense
  const dcs = [];
  for (const id in D.calls) {
    const call = D.calls[id];
    let w = weight(call, tags, dt, dt.sharp || 1); if (w <= 0) continue;
    w *= defOutcome(id, call, P2, info);
    if (w > 0) dcs.push([id, w]);
  }
  const did = pick(R, dcs) || "cover3";
  const dcall = D.calls[did];
  const dal = pick(R, dcall.align.map(x => [x, 1]));
  const flip = R() < 0.5;
  const at = { o: O.alignments[oal].at.map(p => [p[0], flip ? FW - p[1] : p[1]]), d: D.alignments[dal].at.map(p => [p[0], flip ? FW - p[1] : p[1]]) };
  at.o = at.o.map(p => [Math.max(p[0], 1 - pos), p[1]]); at.d = at.d.map(p => [Math.min(p[0], 99 - pos), p[1]]);        // the ball near a goal line: the spots stay on the field
  apart(at.o.concat(at.d));
  const plan = { o: OJ.map((j, k) => resolve(ocall.plan[j] || ocall.plan[OLG[j]], at.o[k], flip, null)), d: [] };
  const qb = at.o[9];
  plan.d = DJ.map((j, k) => resolve(dcall.plan[j], at.d[k], flip, { qb, plan, at, dcall }));
  const uMax = 100 - pos + 8.5, uMin = -pos - 8.5;                      // nobody is sent past the back of an end zone
  for (const side of [plan.o, plan.d]) for (const asg of side) { asg.pts = asg.pts.map(p => [clamp(p[0], uMin, uMax), clamp(p[1], .8, FW - .8)]); if (asg.at) asg.at = asg.pts[0]; }
  const why = [];
  const bits = [];
  if (tags.has("goal")) bits.push("at the goal line"); else if (tags.has("redzone")) bits.push("in the red zone");
  bits.push(`${["first", "second", "third", "fourth"].find(x => tags.has(x))} and ${tags.has("short") ? "short" : tags.has("long") ? "long" : "medium"}`);
  if (tags.has("trailing_late")) bits.push("trailing late"); if (tags.has("leading_late")) bits.push("leading late"); if (tags.has("blowout")) bits.push("well ahead"); if (tags.has("trailing_big")) bits.push("well behind");
  if (tags.has("no_timeouts")) bits.push("no timeouts"); if (tags.has("try")) bits.push("a two-point try");
  return {
    off: { id: oid, name: ocall.name, type: ocall.type, style: ocall.style, fake: !!ocall.fake, align: oal, alignName: O.alignments[oal].name, odds: oc.length ? Math.round(100 * (oc.find(x => x[0] === oid)[1] / oc.reduce((s, x) => s + x[1], 0))) : 0 },
    def: { id: did, name: dcall.name, kind: dcall.kind, style: dcall.style, align: dal, alignName: D.alignments[dal].name, odds: Math.round(100 * (dcs.find(x => x[0] === did)[1] / dcs.reduce((s, x) => s + x[1], 0))) },
    flip, at, plan, situation: bits.join(", "), tags: [...tags],
    coord: { o: info.oc || null, d: info.dc || null },
    res: outcomeFlags(P2, plan, info, R),
  };
}

/* two dots never stand on one spot: a player pushed against the end line is moved sideways off his neighbour (the lists are changed in place) */
function apart(pts) {
  for (let pass = 0; pass < 6; pass++) { let moved = false;
    for (let a = 0; a < pts.length; a++) for (let b = a + 1; b < pts.length; b++) {
      const dx = pts[a][0] - pts[b][0], dy = pts[a][1] - pts[b][1];
      if (Math.hypot(dx, dy) < 1.0) { const s = dy >= 0 ? 1 : -1; pts[a][1] = clamp(pts[a][1] + .6 * s, .8, FW - .8); pts[b][1] = clamp(pts[b][1] - .6 * s, .8, FW - .8); moved = true; }
    }
    if (!moved) break; }
}

/* one assignment in field coordinates: {act, name, pts: [[u, v]...]} (the points after the player's starting spot) */
function resolve(asg, start, flip, X) {
  if (!asg) return { act: "stand", pts: [] };
  const out = { act: asg.act, name: asg.name || "", pts: [] };
  const [u0, v0] = start, sgn = v0 < MID ? 1 : -1;
  if (asg.path) {
    for (const [du, dv] of asg.path) {
      if (asg.rel === "abs") out.pts.push([du, flip ? FW - dv : dv]);
      else if (asg.rel === "in") out.pts.push([u0 + du, v0 + sgn * dv]);
      else out.pts.push([u0 + du, v0 + (flip ? -dv : dv)]);
    }
  } else if (asg.at) {
    out.pts.push([asg.at[0], flip ? FW - asg.at[1] : asg.at[1]]); out.at = out.pts[0];
  } else if (asg.to === "qb") {
    const q = X.at.o[9], lane = asg.lane || 0, tgt = [q[0] - 0.6, q[1] + lane * 0.5];
    out.pts.push([lerp(u0, tgt[0], .5), lerp(v0, tgt[1], .5) + lane * .4], tgt);
  } else if (Array.isArray(asg.to)) {
    out.pts.push([asg.to[0], flip ? FW - asg.to[1] : asg.to[1]]);
  } else if (asg.on) {
    const k = OJ.indexOf(asg.on), tp = X.plan.o[k], tstart = X.at.o[k];
    if (tp && tp.pts.length && (tp.act === "route" || tp.act === "fake_route")) out.pts = tp.pts.map(p => [p[0] + 1.6, p[1]]);
    else out.pts.push([tstart[0] + 4, tstart[1]]);                  // his man blocks or stays: he stays with him
    out.on = asg.on;
  }
  return out;
}

/* who won the matchups the log decided: cues shown after the play (a rating decides which of several linemen, when the page knows ratings) */
function outcomeFlags(P, plan, info, R) {
  const [off, down, toGo, pos, yds, to, kind] = P, o = new Array(11).fill(""), d = new Array(11).fill("");
  const rate = (side, j) => info.rate ? info.rate(side, j) : null;
  const OL = [0, 1, 2, 3, 4];
  const lowest = (arr, side) => arr.slice().sort((x, y) => ((rate(side, x) == null ? 60 : rate(side, x)) - (rate(side, y) == null ? 60 : rate(side, y))) || (x - y))[0];
  const highest = (arr, side) => arr.slice().sort((x, y) => ((rate(side, y) == null ? 60 : rate(side, y)) - (rate(side, x) == null ? 60 : rate(side, x))) || (x - y))[0];
  const sj = info.sj != null ? info.sj : -1;
  if (kind === "SK") { if (sj >= 0) d[sj] = "win"; o[lowest(OL, 0)] = "lose"; }
  else if (kind === "IN") { if (sj >= 0) d[sj] = "win"; o[9] = "lose"; }
  else if (kind === "PC") { if (info.tj >= 0) o[info.tj] = "win"; if (sj >= 0 && yds >= 8) d[sj] = "lose"; else if (sj >= 0 && yds <= 3) d[sj] = "win"; }
  else if (kind === "RU") {
    if (yds >= 8) { o[highest(OL, 0)] = "win"; const e = highest(OL.filter(x => o[x] === ""), 0); o[e] = "win"; d[R() < .5 ? 0 : 1] = "lose"; }
    else if (yds <= 0) { d[[0, 1, 2, 3][(R() * 4) | 0]] = "win"; o[lowest(OL, 0)] = "lose"; }
  }
  return { o, d };
}

root.DFLCalls = { use, situation, tagsFor, choose, OJ, DJ, rng };
if (typeof module !== "undefined" && module.exports) module.exports = root.DFLCalls;
})(typeof window !== "undefined" ? window : globalThis);
