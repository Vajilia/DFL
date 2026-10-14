/* The DFL stage: a small 2D animated field for the game page (sprites, camera, banners).

   It shows what the engine's play log says and nothing else. The log gives, for each play, who ran or threw, how many yards, who made the tackle, and the result;
   the stage invents only the choreography between those facts (the route, the exact path of the run, how the pass flies) and it always ends the play on the spot the log gives.
   Nothing here decides a score, a down or a result, and the page does not need the stage: switch it off and the page is the same page.

   Two layers:
     buildScene(play, ctx)   pure: a play record in, a timeline of keyframes out. No page, no canvas; the checks run it over every play of every game.
     Stage                   draws a timeline on a canvas and keeps the camera, the lines and the lineup between plays.

   Units: the world is the field in yards, x 0..120 (the two end zones are 0..10 and 110..120) and y 0..53.3 across; z is height. The away club attacks to the right (see FX in the page).
   A scene is built in the play's own frame, u yards downfield from the line of scrimmage and v across, and turned into world coordinates when a keyframe is added. */
(function (root) {
"use strict";
const FW = 53.3, MID = 26.65;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const sstep = t => { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); };
function rng(seed) { let s = (seed >>> 0) || 1; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const wxOf = (side, p) => side === 0 ? 110 - p : 10 + p;        // world x of the spot p (0..100 from the offense's own goal line) for the club attacking
const dirOf = side => side === 0 ? -1 : 1;
const SPEED = 6.6, RETSPEED = 8.5;                                              // yards a second for a ball carrier

/* The 22 figures are two pools of 11, one a club. In a pool the index is the job: on offense 0 C, 1 LG, 2 RG, 3 LT, 4 RT, 5 TE, 6 W1, 7 W2, 8 W3, 9 QB, 10 RB;
   on defense 0-3 line, 4-6 linebackers, 7-8 corners, 9-10 safeties. When the ball changes sides, each figure simply takes the other job. */
const O = { C: 0, LG: 1, RG: 2, LT: 3, RT: 4, TE: 5, W1: 6, W2: 7, W3: 8, QB: 9, RB: 10 };
const OFF_F = [[-.7, MID], [-.7, 23.25], [-.7, 30.05], [-.7, 19.85], [-.7, 33.45], [-.8, 37.4], [-.7, 5], [-.7, 48.5], [-1.8, 43], [-5, MID], [-5.6, 22.6]];
const DEF_F = [[1.2, 24.8], [1.2, 28.5], [1.2, 20.9], [1.2, 32.4], [4.4, 16.5], [4.8, MID], [4.4, 36.8], [6.5, 7], [6.5, 47], [13, 16], [13, 37.5]];
const OFF_STANCE = ["stance", "stance", "stance", "stance", "stance", "stance", "stand", "stand", "stand", "stand", "stand"];
const DEF_STANCE = ["stance", "stance", "stance", "stance", "stand", "stand", "stand", "stand", "stand", "stand", "stand"];

/* Where the 22 stand before a snap, as [u, v, pose] per job, for a normal play, a field goal or a punt (retU: where the returner waits, in yards from the line). */
function lineup(kind, retU) {
  let o = OFF_F.map((p, i) => [p[0], p[1], OFF_STANCE[i]]), d = DEF_F.map((p, i) => [p[0], p[1], DEF_STANCE[i]]);
  if (kind === "FG") {
    o = [[-.7, MID], [-.7, 23.65], [-.7, 29.65], [-.7, 20.65], [-.7, 32.65], [-.8, 35.65], [-.7, 17.65], [-.7, 38.65], [-.7, 14.65], [-7.2, MID], [-8.9, 24.9]].map((p, i) => [p[0], p[1], i < 9 ? "stance" : i === 9 ? "kneel" : "stand"]);
    d = [[1.2, 24.8], [1.2, 28.5], [1.2, 20.9], [1.2, 32.4], [1.4, 16], [1.4, MID], [1.4, 37], [3, 13], [3, 40], [8, MID], [12, MID]].map((p, i) => [p[0], p[1], i < 7 ? "stance" : "stand"]);
  } else if (kind === "PU") {
    o = [[-.7, MID], [-.7, 23.65], [-.7, 29.65], [-.7, 20.65], [-.7, 32.65], [-.8, 35.65], [-.7, 9], [-.7, 45], [-.7, 38.65], [-4.5, MID], [-14.5, MID]].map((p, i) => [p[0], p[1], i < 6 ? "stance" : "stand"]);
    const r = retU == null ? 40 : retU;
    d = [[1.2, 24.8], [1.2, 28.5], [1.2, 20.9], [1.2, 32.4], [3.4, 18], [3.4, MID], [3.4, 35.3], [1.3, 10.5], [1.3, 43.5], [r, MID], [r - 9, 20]].map((p, i) => [p[0], p[1], i < 4 ? "stance" : "stand"]);
  }
  return { o, d };
}

/* The 22 figures of a formation in world coordinates, indexed team * 11 + job: [x, y, pose, face]. */
function formation(off, pos, kind, retU) {
  const L = lineup(kind, retU), d = dirOf(off), los = wxOf(off, pos), out = new Array(22);
  for (let k = 0; k < 11; k++) {
    out[off * 11 + k] = [los + d * L.o[k][0], L.o[k][1], L.o[k][2], d];
    out[(1 - off) * 11 + k] = [los + d * L.d[k][0], L.d[k][1], L.d[k][2], -d];
  }
  return out;
}

/* ---------- a scene: keyframes for 22 figures and the ball, plus banners ----------
   A figure's keyframe is [t, x, y, pose, face]. The pose names what the figure does from this keyframe to the next (null: runs if he is moving, otherwise stands).
   go(a, t, u, v, pose) walks to the spot, arriving at t, with that pose on the way; hold(a, t, pose) stays put until t, and keeps the pose after. */
function Scene(off, pos, kind, retU) {
  this.off = off; this.pos = pos; this.kind = kind; this.dir = dirOf(off); this.los = wxOf(off, pos);
  this.tr = Array.from({ length: 22 }, () => []);
  this.balls = [];                                       // {t0, t1, k: "carry" | "fly" | "rest", ...}: the last one begun is the one in force
  this.ev = [];                                          // banners, tags and flags
  this.dur = 0; this.endSpot = null;
  this.start = formation(off, pos, kind, retU);
  this.start.forEach((p, i) => this.tr[i].push([0, p[0], p[1], p[2], p[3]]));
  this.brest(0, 0, MID, 0);
}
Scene.prototype = {
  O(k) { return this.off * 11 + k; },
  D(k) { return (1 - this.off) * 11 + k; },
  X(u) { return this.los + this.dir * u; },
  go(a, t, u, v, pose, face) {
    const tr = this.tr[a], last = tr[tr.length - 1], x = clamp(this.X(u), -4, 124), y = clamp(v, 0.4, FW - 0.4);
    if (t < last[0] - 1e-9) throw new Error(`keyframes out of order (${a}: ${t} < ${last[0]})`);
    if (pose) last[3] = pose; else if ((last[3] === "stance" || last[3] === "kneel") && Math.hypot(x - last[1], y - last[2]) > .05) last[3] = null;
    if (t - last[0] < 1e-6) { last[1] = x; last[2] = y; if (face) last[4] = face * this.dir; return this; }
    tr.push([t, x, y, null, face ? face * this.dir : null]); if (t > this.dur) this.dur = t; return this;
  },
  where(a) { const l = this.tr[a][this.tr[a].length - 1]; return [(l[1] - this.los) * this.dir, l[2], l[0]]; },       // the last keyframe as [u, v, t]
  hold(a, t, pose) { const w = this.where(a); this.go(a, Math.max(t, w[2]), w[0], w[1], pose); if (pose) this.tr[a][this.tr[a].length - 1][3] = pose; return this; },
  bfly(t0, t1, from, to, arc) { this.balls.push({ t0, t1, k: "fly", a: [this.X(from[0]), from[1], from[2]], b: [this.X(to[0]), to[1], to[2]], arc: arc || 0 }); if (t1 > this.dur) this.dur = t1; return this; },
  bcarry(t0, a, z) { this.balls.push({ t0, t1: Infinity, k: "carry", who: a, z: z == null ? 1.35 : z }); return this; },
  brest(t0, u, v, z) { this.balls.push({ t0, t1: Infinity, k: "rest", a: [this.X(u), v, z || 0] }); if (t0 > this.dur) this.dur = t0; return this; },
  banner(t0, t1, text, sub, cls) { this.ev.push({ k: "banner", t0, t1, text, sub: sub || "", cls: cls || "" }); if (t1 > this.dur) this.dur = t1; return this; },
  tag(a, t0, t1, text) { if (text) this.ev.push({ k: "tag", t0, t1, a, text }); return this; },
  flag(t, u, v) { this.ev.push({ k: "flag", t0: t, x: this.X(u), y: v }); return this; },
};

/* ---------- sampling a scene at a time ---------- */
function sampleTrack(tr, t, defFace) {
  const n = tr.length, k0 = tr[0];
  if (n === 1 || t <= k0[0]) return { x: k0[1], y: k0[2], pose: k0[3] || "stand", face: k0[4] || defFace, sp: 0 };
  const kl = tr[n - 1];
  if (t >= kl[0]) { const pv = tr[n - 2]; return { x: kl[1], y: kl[2], pose: kl[3] || "stand", face: kl[4] || (Math.abs(kl[1] - pv[1]) > .05 ? Math.sign(kl[1] - pv[1]) : pv[4] || defFace), sp: 0 }; }
  let i = 0; while (i < n - 2 && tr[i + 1][0] <= t) i++;
  const a = tr[i], b = tr[i + 1], dt = b[0] - a[0], u = (t - a[0]) / dt, dx = b[1] - a[1], dy = b[2] - a[2], sp = Math.hypot(dx, dy) / dt;
  return { x: a[1] + dx * u, y: a[2] + dy * u, pose: a[3] || (sp > .9 ? "run" : "stand"), face: a[4] || (Math.abs(dx) > .05 ? Math.sign(dx) : (i > 0 && tr[i - 1][4]) || defFace), sp };
}
function sampleBall(sc, t, act) {
  let s = sc.balls[0]; for (const b of sc.balls) if (b.t0 <= t && b.t0 >= s.t0) s = b;
  if (s.k === "rest") return { x: s.a[0], y: s.a[1], z: s.a[2], spin: 0, held: false };
  if (s.k === "carry") { const p = act[s.who], z = p.pose === "down" ? .3 : p.pose === "cele" || p.pose === "catch" ? 2.5 : p.pose === "throw" ? 2.5 : p.pose === "kneel" ? .5 : s.z; return { x: p.x + p.face * .42, y: p.y, z, spin: 0, held: true, who: s.who }; }
  const u = clamp((t - s.t0) / Math.max(1e-6, s.t1 - s.t0), 0, 1), z = lerp(s.a[2], s.b[2], u) + 4 * s.arc * u * (1 - u);
  return { x: lerp(s.a[0], s.b[0], u), y: lerp(s.a[1], s.b[1], u), z: Math.max(0, z), spin: u < 1 ? t * 22 : 0, held: false, flying: u < 1 };
}
function sampleScene(sc, t) {
  const act = sc.tr.map((tr, i) => sampleTrack(tr, t, Math.floor(i / 11) === sc.off ? sc.dir : -sc.dir));
  return { act, ball: sampleBall(sc, t, act) };
}
const endBall = sc => sampleScene(sc, sc.dur + 1).ball;

/* ---------- choreography ---------- */
const DKEY = { DL: [0, 4], LB: [4, 3], CB: [7, 2], S: [9, 2] }, OKEY = { WR: [6, 3], TE: [5, 1], RB: [10, 1], QB: [9, 1] };
const slotOf = (table, label, idx, fallback) => { const r = table[label]; return r ? r[0] + ((Math.abs(idx) % r[1])) : fallback; };
const TD_SUB = d => d ? (d[7] === 7 ? "Extra point good" : d[7] === 6 ? "Extra point no good" : d[7] === 8 ? "Two-point try good" : "") : "";

/* buildScene(play, ctx)
   ctx.nm(i)    the roster entry [name, position, side, id] for index i, or null
   ctx.hint     where the next possession begins, as a spot in this play's offense frame (0..100), when the log says; null if it does not
   ctx.dr       the drive record, when this is the last play of the drive
   ctx.abbr     [home, away] club codes;  ctx.pen  the penalty's name;  ctx.seed  any number: it only varies the choreography */
function buildScene(P, ctx) {
  const [off, down, toGo, pos, yds, to, kind, a, bb, c, , , , , gt] = P;
  ctx = ctx || {};
  const nmf = i => (ctx.nm && i >= 0 && ctx.nm(i)) || null, name = i => { const r = nmf(i); return r ? r[0] : ""; }, lab = i => { const r = nmf(i); return r ? r[1] : ""; };
  const R = rng(((pos + 1) * 131 + (yds + 60) * 17 + ((gt | 0) % 9973) * 7 + (a + 3) * 3 + (bb + 5) * 11 + (ctx.seed | 0)) >>> 0);
  const goal = 100 - pos, res = ctx.dr ? ctx.dr[6] : "", hu = ctx.hint == null ? null : ctx.hint - pos;
  const retU = kind === "PU" ? clamp(Math.min(yds, goal) + 3 + R() * 2, 12, goal + 6) : null;
  const S = new Scene(off, pos, kind === "FG" || kind === "PU" ? kind : "N", retU);
  S.kind = kind; S.retU = retU;
  const H = { P, ctx, R, S, tS: .55, goal, res, hu, name, lab, ab: ctx.abbr || ["HOME", "AWAY"], used: new Set() };
  H.defFor = (i, rest) => { let k = slotOf(DKEY, lab(i), i, -1); if (k < 0 || H.used.has(k)) k = rest.find(f => !H.used.has(f)); H.used.add(k); return k; };
  H.converge = (k, tStart, tArrive, u, v, pose) => {             // a figure goes from where he is to a spot, arriving at tArrive
    const l = S.where(k), t0 = Math.max(l[2], tStart); S.hold(k, t0); S.go(k, Math.max(tArrive, t0 + .25), u, clamp(v, 2, 51), pose || "run");
  };
  H.blockers = (mode, tEnd, u1) => {                               // the five linemen: they drive forward on a run, they give ground in the pocket on a pass
    for (let k = 0; k < 5; k++) {
      const [u0, v0] = OFF_F[k], t1 = H.tS + .38, uTo = mode === "run" ? .4 : -.8;
      S.hold(S.O(k), H.tS + .1, "stance").go(S.O(k), t1, uTo, v0 + (v0 < MID ? -.2 : .2), "block");
      S.go(S.O(k), Math.max(tEnd - .1, t1 + .3), mode === "run" ? u1 : -1.5 - R() * .3, v0, "block").hold(S.O(k), Math.max(tEnd + .3, t1 + .6), "stand");
    }
  };
  if (kind === "RU") runScene(H);
  else if (kind === "PC" || kind === "PI" || kind === "IN") passScene(H);
  else if (kind === "SK") sackScene(H);
  else if (kind === "FG") kickScene(H);
  else if (kind === "PU") puntScene(H);
  else if (kind === "PN") penaltyScene(H);
  else if (kind === "SP") spikeScene(H);
  else if (kind === "KN") kneelScene(H);
  else if (kind === "TO") { S.banner(.1, 1.7, "TIMEOUT", H.ab[a] || "", "plain"); S.endSpot = { off, u: 0 }; S.dur = Math.max(S.dur, 1.9); }
  else if (kind === "IJ") { S.banner(.1, 2.6, "INJURY", name(a) ? `${name(a)} leaves the game${name(bb) ? ` · ${name(bb)} comes in` : ""}` : "", "plain"); S.endSpot = { off, u: 0 }; S.dur = Math.max(S.dur, 2.8); }      // rules version 4: a player is hurt and a backup takes her place
  else throw new Error("unknown play kind " + kind);
  S.dur += .3;
  S.balls.sort((x, y) => x.t0 - y.t0);
  return S;
}

/* the tackle, the touchdown, the fumble, the stop on the line to gain: how a run, a catch or a sack ends */
function finishPlay(H, who, tk, tE, uEnd, vEnd, td) {
  const { S, P, ctx, R, goal, res, hu, name, ab } = H, [off, down, toGo, pos, yds, to, kind] = P;
  if (td) {
    S.hold(who, tE + 2.3, "cele"); S.endSpot = { off, u: uEnd };
    S.banner(tE + .1, tE + 2.5, "TOUCHDOWN", TD_SUB(ctx.dr) || ab[off], "good");
    S.dur = Math.max(S.dur, tE + 2.4); return;
  }
  if (to === 2) {                                                        // the ball pops loose and the defense falls on it
    const rec = tk, uB = uEnd + 1.3, vB = clamp(vEnd + (R() - .5) * 3, 2, 51), td2 = res === "FUMBLE_TD", uR = td2 ? -pos - 1.4 : hu != null ? hu : uB;
    S.hold(who, tE + .15, "down");
    S.balls.push({ t0: tE, t1: tE + .5, k: "fly", a: [S.X(uEnd), vEnd, 1.2], b: [S.X(uB), vB, 0], arc: 1.6 });
    S.brest(tE + .5, uB, vB, 0);
    S.hold(rec, tE + .15, "tackle").go(rec, tE + .62, uB, vB, "run").bcarry(tE + .62, rec, .7);
    if (td2) { const d = Math.abs(uB - uR) / RETSPEED + .2, vR = clamp(vB + (R() - .5) * 8, 4, 49); S.go(rec, tE + .62 + d, uR, vR, "run").hold(rec, tE + 1.9 + d, "cele"); S.banner(tE + .1, tE + 3 + d, "FUMBLE", "Returned for a touchdown", "bad"); S.endSpot = { off, u: uR }; S.dur = Math.max(S.dur, tE + 2.2 + d); }
    else { const d = Math.abs(uB - uR) / SPEED; S.go(rec, tE + .62 + d, uR, vB, "run").hold(rec, tE + 1.6 + d, "down"); S.banner(tE + .1, tE + 2.4 + d, "FUMBLE", "Recovered by the defense", "bad"); S.endSpot = { off, u: uR }; S.dur = Math.max(S.dur, tE + 1.8 + d); }
    S.tag(rec, tE + .5, tE + 2, "");
    return;
  }
  S.hold(who, tE + .1, "down");
  S.hold(tk, tE + .9, "tackle");
  S.brest(tE + .3, uEnd + .3, vEnd + .35, 0);
  S.endSpot = { off, u: uEnd };
  const fd = yds >= toGo && yds > 0 && kind !== "SK";
  if (res === "SAFETY") S.banner(tE + .1, tE + 2.4, "SAFETY", "Two points for the defense", "bad");
  else if (res === "DOWNS") S.banner(tE + .1, tE + 2, "TURNOVER ON DOWNS", "", "bad");
  else if (fd) S.banner(tE + .15, tE + 1.6, "FIRST DOWN", "", "small");
  S.dur = Math.max(S.dur, tE + 1.5);
}

function runScene(H) {
  const { S, P, R, tS, goal, name } = H, [off, down, toGo, pos, yds, to, kind, a, bb] = P, rb = S.O(10), qb = S.O(9), td = pos + yds >= 100 && to !== 1;
  const uEnd = td ? goal + 1.4 : yds, vEnd = clamp(MID + (R() - .5) * 15, 5, 47), vMid = lerp(25.4, vEnd, .35);
  const tH = tS + .72, tHole = tH + .38, run = Math.abs(uEnd - .8) + Math.abs(vEnd - vMid) * .3, tE = yds <= 0 ? tH + .55 : tHole + Math.max(.55, run / SPEED);
  S.bfly(tS, tS + .26, [-.7, MID, .8], [-4.9, MID, 1.2], .5).bcarry(tS + .26, qb).bcarry(tH, rb);
  S.hold(qb, tS + .26, "stand").go(qb, tH, -4.6, 25.8, "stand", 1).hold(qb, tE + .5, "stand");
  S.hold(rb, tS).go(rb, tH, -3.7, 25.4, "run");
  if (yds > 0) S.go(rb, tHole, Math.min(.8, uEnd), vMid, "run");
  S.go(rb, tE, uEnd, vEnd, "run");
  H.blockers("run", tE, clamp(.5 + Math.max(0, uEnd) * .35, .5, 3.4));
  const tk = td ? -1 : H.defFor(bb, [4, 5, 6, 9, 10, 7, 8, 0, 1, 2, 3]);
  for (let k = 0; k < 11; k++) {
    const d0 = DEF_F[k], D = S.D(k);
    if (k === tk) { S.hold(D, tS + .15).go(D, tE - .1, uEnd + .5, vEnd + (R() - .5) * .8, "run").go(D, tE + .2, uEnd + .35, vEnd, "tackle"); continue; }
    if (k < 4) S.hold(D, tS + .1, "stance").go(D, tS + .36, d0[0] - .25, d0[1], "block").go(D, Math.max(tE - .05, tS + .7), d0[0] + Math.max(0, uEnd) * .3 + R() * .8, lerp(d0[1], vEnd, .4) + (R() - .5) * 2.2, "run");
    else H.converge(D, tS + .2 + R() * .2, tE + R() * .25, uEnd + (td ? -1 - R() * 5 : .5 + R() * 3.2 + (k > 8 ? 1.5 : 0)), vEnd + (R() - .5) * 5);
  }
  for (const k of [5, 6, 7, 8]) { const f = OFF_F[k], dU = clamp(Math.max(3, uEnd * .8) + 2 + R() * 4, 4, td ? goal + 1 : 18), vv = clamp(f[1] + (vEnd - f[1]) * .25, 2, 51); S.hold(S.O(k), tS + .1).go(S.O(k), Math.max(tE - .05, tS + .8), dU, vv, "run").hold(S.O(k), tE + .4, "block"); }
  S.tag(rb, tH, tE + 1, name(a)); if (tk >= 0) S.tag(S.D(tk), tE - .1, tE + 1, name(bb));
  finishPlay(H, rb, tk >= 0 ? S.D(tk) : -1, tE, uEnd, vEnd, td);
}

function sackScene(H) {
  const { S, P, R, tS, name } = H, [off, down, toGo, pos, yds, to, kind, a, bb] = P, qb = S.O(9), rbk = S.O(10);
  const sk = H.defFor(bb, [0, 1, 2, 3, 4, 5, 6]), uQ = yds, tK = tS + 1.25 + R() * .4, vQ = clamp(MID + (R() - .5) * 2.5, 20, 33), D = S.D(sk);
  S.bfly(tS, tS + .26, [-.7, MID, .8], [-4.9, MID, 1.2], .5).bcarry(tS + .26, qb);
  S.hold(qb, tS + .26, "stand").go(qb, tS + .95, Math.min(-5.5, uQ + 1), vQ, "run", 1).go(qb, tK, uQ, vQ + (R() - .5) * 2, "run", 1);
  H.blockers("pass", tK + .3, 0);
  for (let k = 0; k < 11; k++) {
    const d0 = DEF_F[k], Dk = S.D(k);
    if (k === sk) { S.hold(Dk, tS + .1, "stance").go(Dk, tK - .15, uQ + .5, vQ + 1.1, "run").go(Dk, tK + .15, uQ + .2, vQ + .6, "tackle"); continue; }
    if (k < 4) S.hold(Dk, tS + .1, "stance").go(Dk, tS + .4, d0[0] - .1, d0[1], "block").go(Dk, tK + .2, -.3 - R() * 1.2, lerp(d0[1], vQ, .35) + (R() - .5) * 3, "block");
    else if (k < 7) S.hold(Dk, tS + .1).go(Dk, tK + .3, 7 + R() * 2, d0[1] + (R() - .5) * 4, "run");
    else S.hold(Dk, tS + .1).go(Dk, tK + .3, d0[0] + 3 + R() * 6, d0[1] + (R() - .5) * 3, "run");
  }
  for (const k of [5, 6, 7, 8]) { const f = OFF_F[k]; S.hold(S.O(k), tS + .1).go(S.O(k), tK + .3, 7 + R() * 7, clamp(f[1] + (R() - .5) * 8, 3, 50), "run"); }
  S.hold(rbk, tS).go(rbk, tS + .5, -4.2, 25.6, "block").hold(rbk, tK + .4, "block");
  S.hold(qb, tK + .2, "down").hold(qb, tK + 3, "down");
  S.hold(D, tK + .9, "tackle");
  S.tag(qb, tS + .3, tK + 1.2, name(a)); S.tag(D, tK - .2, tK + 1.2, name(bb));
  if (to === 2) {                                                        // sacked and stripped
    const rk = 4 + (sk + 1 + (R() * 3 | 0)) % 7, rec = S.D(rk === sk ? 4 + (rk - 3) % 7 : rk), uB = uQ - 1.6, uR = H.hu != null ? H.hu : uB;
    S.bfly(tK, tK + .45, [uQ, vQ, 1.5], [uB, vQ + 1.5, 0], 1.2).brest(tK + .45, uB, vQ + 1.5, 0);
    H.converge(rec, tK - .3, tK + .5, uB, vQ + 1.5, "run"); S.bcarry(tK + .55, rec, .7);
    if (H.res === "FUMBLE_TD") {
      const uT = -pos - 1.4, d = Math.abs(uB - uT) / RETSPEED;
      S.go(rec, tK + .6 + d, uT, clamp(vQ + (R() - .5) * 10, 4, 49), "run").hold(rec, tK + 1.9 + d, "cele");
      S.banner(tK + .1, tK + 3 + d, "SACK AND FUMBLE", "Returned for a touchdown", "bad"); S.endSpot = { off, u: uT }; S.dur = Math.max(S.dur, tK + 2.2 + d);
    } else {
      S.go(rec, tK + .6 + Math.abs(uB - uR) / SPEED, uR, vQ + 1.5, "run").hold(rec, tK + 1.8 + Math.abs(uB - uR) / SPEED, "down");
      S.banner(tK + .1, tK + 2.3, "SACK AND FUMBLE", "Recovered by the defense", "bad"); S.endSpot = { off, u: uR }; S.dur = Math.max(S.dur, tK + 2);
    }
  } else {
    S.brest(tK + .2, uQ - .3, vQ + .4, 0); S.endSpot = { off, u: uQ };
    if (H.res === "SAFETY") S.banner(tK + .1, tK + 2.4, "SAFETY", "Two points for the defense", "bad"); else if (H.res === "DOWNS") S.banner(tK + .1, tK + 2, "TURNOVER ON DOWNS", "", "bad"); else S.banner(tK + .1, tK + 1.7, "SACK", name(bb), "small");
    S.dur = Math.max(S.dur, tK + 1.6);
  }
}

function passScene(H) {
  const { S, P, R, tS, goal, res, name, lab } = H, [off, down, toGo, pos, yds, to, kind, a, bb, c] = P, qb = S.O(9), rbk = S.O(10);
  const tgtSlot = slotOf(OKEY, lab(bb), bb, 6 + Math.abs(bb) % 3), tgt = S.O(tgtSlot), td = kind === "PC" && pos + yds >= 100 && to !== 1;
  const air = kind === "PC" ? (yds <= 3 ? yds : Math.round(yds * (.5 + R() * .3))) : kind === "IN" ? clamp(Math.round(6 + R() * 18), 4, Math.max(4, goal - 1)) : clamp(Math.round(5 + R() * 14), 3, Math.max(3, goal - 1));
  const uC = td ? Math.min(air, goal - .5) : air, f0 = OFF_F[tgtSlot];
  const vT = clamp(f0[1] + (f0[1] < MID ? 1 : -1) * (3 + R() * 6) * (tgtSlot === 5 || tgtSlot === 10 ? .4 : 1), 3, 50);
  const tT = tS + 1.15 + clamp(uC * .018, 0, .5), qU = -7.2, qV = clamp(MID + (R() - .5) * 2.5, 21, 32);
  const tC = tT + .12 + .5 + .03 * Math.hypot(uC - qU, vT - qV), stemEnd = tS + .25 + (tC - tS - .25) * .72;
  S.bfly(tS, tS + .26, [-.7, MID, .8], [-4.9, MID, 1.2], .5).bcarry(tS + .26, qb);
  S.hold(qb, tS + .26, "stand").go(qb, tS + .95, qU, qV, "run", 1).hold(qb, tT).hold(qb, tT + .4, "throw").hold(qb, tC + .5, "stand");
  H.blockers("pass", tC + .2, 0);
  // the receivers run their routes; the one the log names goes to the spot
  for (const k of [5, 6, 7, 8]) {
    const f = OFF_F[k], O_ = S.O(k);
    if (k === tgtSlot) { S.hold(O_, tS + .1, "stance").go(O_, stemEnd, Math.max(1, uC * .85 - .5), lerp(f[1], vT, .35), "run").go(O_, tC, uC, vT, "run"); continue; }
    const dU = clamp(5 + R() * 11, 4, Math.max(4, goal + 3));
    S.hold(O_, tS + .1, "stance").go(O_, tS + .9, dU * .8, f[1] + (R() - .5) * 5, "run").go(O_, tC, dU, clamp(f[1] + (R() - .5) * 9, 3, 50), "run");
  }
  if (tgtSlot === 10) S.hold(rbk, tS).go(rbk, stemEnd, 1, lerp(OFF_F[10][1], vT, .35), "run").go(rbk, tC, uC, vT, "run");
  else S.hold(rbk, tS).go(rbk, tS + .5, -4.2, 25.6, "block").hold(rbk, tC, "block");
  const cov = kind === "PI" ? H.defFor(-9, [7, 8, 9, 10]) : kind === "IN" ? H.defFor(c, [7, 8, 9, 10, 4, 5, 6]) : H.defFor(c, [4, 5, 6, 7, 8, 9, 10]), Dc = S.D(cov);
  for (let k = 0; k < 4; k++) { if (k === cov) continue; const d0 = DEF_F[k], D = S.D(k); S.hold(D, tS + .1, "stance").go(D, tS + .42, d0[0] - .2, d0[1], "block").go(D, tT + .5, -.9 - R() * .8, lerp(d0[1], qV, .3), "run").hold(D, tC + 1, "block"); }
  S.tag(qb, tT - .4, tC, name(a));
  const throwFrom = [qU, qV, 2.1], arc = d => 1.4 + .09 * d;
  if (kind === "IN") {
    const pick = [uC + .2, vT + .4], pickTd = res === "INT_TD", uR = pickTd ? -pos - 1.4 : hintOr(H, uC - Math.max(0, yds)), tR = tC + .3 + Math.max(.3, Math.abs(pick[0] - uR) / RETSPEED), vR = clamp(pick[1] + (R() - .5) * 10, 4, 49);
    S.bfly(tT + .12, tC, throwFrom, [pick[0], pick[1], 1.8], arc(Math.abs(uC - qU)));
    S.hold(Dc, tS + .2).go(Dc, tC - .08, pick[0], pick[1], "run").hold(Dc, tC + .22, "catch").bcarry(tC, Dc);
    S.go(Dc, tR, uR, vR, "run").hold(Dc, tR + (pickTd ? 1.8 : .9), pickTd ? "cele" : "down");
    H.converge(tgt, tC - .1, tC + .5, uC - 1, vT - .2, "run");
    const chase = [9, 6, 7, 8, 5, 10];
    chase.forEach((k, n) => { if (k === tgtSlot) return; H.converge(S.O(k), tC + .1, tR + (n === 0 ? 0 : .15 * n), uR + (n === 0 ? -.4 : (R() - .5) * 4 + 2), vR + (R() - .5) * 5, "run"); });
    for (const k of [0, 1, 2, 3, 4]) { const l = S.where(S.O(k)); H.converge(S.O(k), tC + .2, tR + .1, clamp(l[0] + (uR - l[0]) * .3, -20, 40), l[1], "run"); }
    for (let k = 4; k < 11; k++) if (k !== cov) H.converge(S.D(k), tC - .3, tR, uR + ((k * 3) % 10) - 3, vR + (R() - .5) * 8);
    S.brest(tR + .35, uR + (pickTd ? 0 : .3), vR, 0);
    S.tag(Dc, tC, tR + .8, name(c));
    S.banner(tC + .1, tR + 1.2, pickTd ? "PICK SIX" : "INTERCEPTED", pickTd ? name(c) : "", "bad");
    S.endSpot = { off, u: uR }; S.dur = Math.max(S.dur, tR + 1.6);
    return;
  }
  if (kind === "PI") {
    const short = R() < .5, uL = uC + (short ? -1.8 : 2.6), vL = vT + (R() - .5) * 2, uF = uL + (short ? -.8 : 1.6);
    S.bfly(tT + .12, tC + .1, throwFrom, [uL, vL, 0], arc(Math.abs(uC - qU))).bfly(tC + .1, tC + .5, [uL, vL, 0], [uF, vL + 1, 0], .5).brest(tC + .5, uF, vL + 1, 0);
    S.hold(Dc, tS + .2).go(Dc, tC, uC + .8, vT + .8, "run").go(Dc, tC + .45, uC + 1, vT + 1.6, "stand");
    S.hold(tgt, tC, "catch").go(tgt, tC + .5, uL - 1, vT, "stand");
    for (let k = 4; k < 11; k++) if (k !== cov) H.converge(S.D(k), tS + .3, tC + .3, uC + (R() - .3) * 4 + (k > 8 ? 2 : 0), vT + (R() - .5) * 12);
    S.tag(tgt, tC - .5, tC + 1, name(bb));
    S.banner(tC + .25, tC + 1.7, "INCOMPLETE", "", "small");
    S.endSpot = { off, u: 0 }; S.dur = Math.max(S.dur, tC + 1.5);
    return;
  }
  // a completion: the catch, then the run after the catch to the spot of the tackle
  const uEnd = td ? goal + 1.4 : yds, vEnd = clamp(vT + (R() - .5) * 6, 3, 50), yac = Math.abs(uEnd - uC) + Math.abs(vEnd - vT) * .35, tE = tC + (yac < .8 ? .45 : .22 + yac / SPEED);
  S.bfly(tT + .12, tC, throwFrom, [uC, vT, 1.8], arc(Math.abs(uC - qU))).bcarry(tC, tgt);
  S.hold(tgt, tC + .22, "catch");
  if (yac >= .8) S.go(tgt, tE, uEnd, vEnd, "run"); else S.go(tgt, tE, uEnd, vEnd, "stand");
  S.hold(Dc, tS + .2).go(Dc, tC - .1, uC + 1, vT + (R() < .5 ? -1 : 1) * 1.2, "run").go(Dc, tE - .06, uEnd + .5, vEnd + (R() - .5) * .8, "run").go(Dc, tE + .2, uEnd + .35, vEnd, "tackle");
  for (let k = 4; k < 11; k++) if (k !== cov) H.converge(S.D(k), tS + .3, tE + R() * .25, uEnd + (td ? -1 - R() * 5 : .8 + R() * 3.5), vEnd + (R() - .5) * 6);
  S.tag(tgt, tC - .4, tE + 1, name(bb)); if (!td) S.tag(Dc, tE - .1, tE + 1, name(c));
  for (const k of [5, 6, 7, 8]) if (k !== tgtSlot) S.hold(S.O(k), Math.max(S.where(S.O(k))[2], tE + .2), "stand");
  finishPlay(H, tgt, td ? -1 : Dc, tE, uEnd, vEnd, td);
}
const hintOr = (H, dflt) => H.hu != null ? H.hu : dflt;

function kickScene(H) {
  const { S, P, R, tS, goal, name } = H, [off, down, toGo, pos, yds, to, kind, a, bb, c] = P, holder = S.O(9), kicker = S.O(10);
  const tK = tS + .85, good = bb === 1, endU = goal + 10, hU = -7.2, dist = endU - hU, fl = .9 + dist * .02;          // the goal posts stand at the back of the end zone
  S.bfly(tS, tS + .42, [-.7, MID, .8], [hU, MID, .9], .3).brest(tS + .42, hU, MID, .35);
  S.hold(holder, tS + .42, "kneel").hold(holder, tK + 1, "kneel");
  S.hold(kicker, tS).go(kicker, tK - .28, -9.4, 25.2, "stand").go(kicker, tK, -7.9, 26.1, "kick").hold(kicker, tK + .6, "stand");
  const line = lineup("FG");
  for (let k = 0; k < 9; k++) S.hold(S.O(k), tS).go(S.O(k), tS + .3, line.o[k][0] + .15, line.o[k][1], "block").hold(S.O(k), tK + .8, "block");
  for (let k = 0; k < 7; k++) { const f = line.d[k]; S.hold(S.D(k), tS + .1, "stance").go(S.D(k), tK + .3, f[0] + .9 + R() * 1.4, f[1] + (R() < .5 ? -.8 : .8) * R(), "run").hold(S.D(k), tK + .9, "stand"); }
  S.tag(kicker, tK - .5, tK + 1.4, name(a));
  if (good) {
    const v = MID + (R() - .5) * 1.6;
    S.bfly(tK, tK + fl, [hU, MID, .4], [endU + 1, v, 6], 3.2 + dist * .02).bfly(tK + fl, tK + fl + .5, [endU + 1, v, 6], [endU + 3.5, v, 0], .8).brest(tK + fl + .5, endU + 3.5, v, 0);
    S.banner(tK + fl - .2, tK + fl + 2.2, "FIELD GOAL", `${c} yards · it is good`, "good"); S.endSpot = { off, u: endU + 3.5 };
  } else {
    const post = R() < .22, short = !post && R() < .3, side = R() < .5 ? -1 : 1, vW = MID + side * (4 + R() * 2);
    const uHit = short ? goal - 2 - R() * 6 : endU + .5, vHit = post ? MID + 3.1 : short ? MID + (R() - .5) * 3 : vW, zHit = short ? .6 : 4.8, t1 = tK + fl * (short ? .72 : 1);
    const uF = short ? uHit - .8 : post ? endU - 1.5 : endU + 1.8, vF = post ? MID + 4 : short ? vHit : vW + side * 1.8;
    S.bfly(tK, t1, [hU, MID, .4], [uHit, vHit, zHit], 3 + dist * .02).bfly(t1, t1 + .45, [uHit, vHit, zHit], [uF, vF, 0], .5).brest(t1 + .45, uF, vF, 0);
    S.banner(t1 - .1, t1 + 2.1, "NO GOOD", `${c} yards · ${post ? "off the upright" : short ? "short" : side > 0 ? "wide right" : "wide left"}`, "bad"); S.endSpot = { off, u: 0 };
  }
  S.dur = Math.max(S.dur, tK + fl + 1.8);
}

function puntScene(H) {
  const { S, P, R, tS, goal, name } = H, [off, down, toGo, pos, yds, to, kind, a] = P, punter = S.O(10), line = lineup("PU", S.retU), retU = S.retU;
  const tK = tS + .95, touchback = pos + yds >= 100, uL = touchback ? goal + 1.5 + R() * 3 : yds, vL = MID + (R() - .5) * 3, fl = 1.5 + Math.abs(uL + 13) * .028;
  S.bfly(tS, tS + .5, [-.7, MID, .8], [-14.2, MID, 1], .6).bcarry(tS + .5, punter, 1);
  S.hold(punter, tS + .5, "stand").go(punter, tK - .22, -13.4, MID, "run").go(punter, tK, -12.6, MID, "kick").hold(punter, tK + .6, "stand");
  S.bfly(tK, tK + fl, [-13, MID, .6], [uL, vL, touchback ? 0 : 1.6], 6 + Math.abs(uL + 13) * .1);
  for (let k = 0; k < 9; k++) {
    const f = line.o[k], O_ = S.O(k); S.hold(O_, tS);
    if (k < 6) S.go(O_, tS + .4, f[0] + .2, f[1], "block").hold(O_, tK + .6, "block");
    else S.hold(O_, tS + .25, "stance").go(O_, tK + fl, Math.max(uL - 3 - R() * 6, 10), f[1] + (MID - f[1]) * .55, "run");
  }
  S.hold(S.O(9), tS).go(S.O(9), tS + .4, -4.3, MID, "block").hold(S.O(9), tK + .8, "block");
  for (let k = 0; k < 4; k++) { const f = line.d[k], D = S.D(k); S.hold(D, tS + .1, "stance").go(D, tK + .4, f[0] + .8, f[1], "block").go(D, tK + fl, f[0] + 5 + R() * 4, f[1] + (R() - .5) * 8, "run"); }
  const ret = S.D(9), wing = S.D(10), vR0 = S.where(ret)[1];
  S.hold(ret, tK + .1).go(ret, tK + fl - .3, uL - .3, vL + (vR0 - MID) * .3, "run");
  const uR = touchback ? uL : hintOr(H, uL), vR = clamp(MID + (R() - .5) * 16, 6, 47);
  if (touchback) {
    S.hold(ret, tK + fl + .2, "stand");
    S.bfly(tK + fl, tK + fl + .6, [uL, vL, 0], [uL + 3, vL + 1, 0], .6).brest(tK + fl + .6, uL + 3, vL + 1, 0);
    S.banner(tK + fl, tK + fl + 1.8, "TOUCHBACK", "", "small"); S.endSpot = { off, u: uL + 3 }; S.dur = Math.max(S.dur, tK + fl + 1.7);
  } else {
    const d = Math.abs(uL - uR) + Math.abs(vR - vL) * .3, tR = tK + fl + .2 + (d < .6 ? .3 : d / SPEED);
    S.hold(ret, tK + fl).bcarry(tK + fl, ret, 1.35).hold(ret, tK + fl + .2, "catch");
    S.go(ret, tR, uR, vR, d < .6 ? "stand" : "run").hold(ret, tR + .5, "down").hold(ret, tR + 3, "down");
    const g = S.O(6 + (Math.abs(a) % 2)); S.hold(g, Math.max(S.where(g)[2], tK + fl - .3)); S.go(g, Math.max(tR - .05, S.where(g)[2] + .1), uR + .6, vR + .3, "tackle").hold(g, tR + .9, "tackle");
    S.brest(tR + .3, uR - .3, vR + .4, 0); S.endSpot = { off, u: uR }; S.dur = Math.max(S.dur, tR + 1.4);
    S.tag(ret, tK + fl, tR + .9, "");
    if (Math.abs(uL - uR) > 14) S.banner(tR, tR + 1.5, "BIG RETURN", "", "small");
  }
  S.tag(punter, tK - .5, tK + 1.4, name(a));
  for (let k = 4; k < 9; k++) { const f = line.d[k]; H.converge(S.D(k), tS, tK + fl + .4, f[0] + 2 + R() * 4, f[1] + (R() - .5) * 8, "run"); }
  H.converge(wing, tK + .3, tK + fl, retU - 9, 20, "stand");
}

/* the clock plays (rules version 3): the quarterback takes the snap and throws the ball into the turf; or he takes it and kneels */
function spikeScene(H) {
  const { S, P, R, tS, name } = H, [off, , , pos, , , , a] = P, qb = S.O(9), v = clamp(MID + (R() - .5) * 2, 22, 31), tT = tS + .55;
  S.bfly(tS, tS + .26, [-.7, MID, .8], [-4.9, MID, 1.2], .5).bcarry(tS + .26, qb);
  for (let k = 0; k < 11; k++) { S.hold(S.O(k), tS + .3); S.hold(S.D(k), tS + .3); }
  S.hold(qb, tT, "stand").hold(qb, tT + .35, "throw").hold(qb, tT + 1.6, "stand");
  S.bfly(tT + .12, tT + .42, [-5, v, 2.4], [-3.4, v, 0], .3).bfly(tT + .42, tT + .8, [-3.4, v, 0], [-2.4, v, 0], 1.1).brest(tT + .8, -2.4, v, 0);
  S.tag(qb, tS + .2, tT + 1.4, name(a));
  S.banner(tT + .35, tT + 1.9, "SPIKE", "", "small");
  S.endSpot = { off, u: -2.4 }; S.dur = Math.max(S.dur, tT + 1.8);
}
function kneelScene(H) {
  const { S, P, tS, name } = H, [off, , , pos, , , , a] = P, qb = S.O(9);
  S.bfly(tS, tS + .26, [-.7, MID, .8], [-4.9, MID, 1.2], .5).bcarry(tS + .26, qb);
  for (let k = 0; k < 11; k++) { if (k !== 9) S.hold(S.O(k), tS + .3); S.hold(S.D(k), tS + .3); }
  S.hold(qb, tS + .26).go(qb, tS + .85, -1.3, MID, "run", 1).hold(qb, tS + 2.3, "kneel");
  S.brest(tS + 1.3, -1, MID, 0);
  S.tag(qb, tS + .2, tS + 2.1, name(a));
  S.banner(tS + 1.0, tS + 2.3, "KNEEL", "", "small");
  S.endSpot = { off, u: -1 }; S.dur = Math.max(S.dur, tS + 2.2);
}

function penaltyScene(H) {
  const { S, P, R } = H, [off, down, toGo, pos, yds, to, kind, a, bb] = P, tF = .9, np = clamp(pos + yds, 1, 99), du = np - pos;
  S.flag(tF, 1.5 + R() * 2, bb === 1 ? 5 : 48);
  for (let k = 0; k < 11; k++) { S.hold(S.O(k), tF + 2.4); S.hold(S.D(k), tF + 2.4); }
  S.banner(tF + .1, tF + 2.5, "FLAG", H.ctx.pen || "Penalty", "flag");
  S.brest(tF + 1.4, du, MID, 0);
  S.endSpot = { off, u: du }; S.dur = tF + 2.5;
}


/* ======================= the drawing: Stage ======================= */
const SKIN = ["#F1C9A0", "#D9A06B", "#B5784A", "#8A5530", "#5E3A22"];
const hexRgb = h => { const n = parseInt(String(h).slice(1), 16); return [n >> 16, (n >> 8) & 255, n & 255]; };
const lumOf = h => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }, [r, g, b] = hexRgb(h); return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
const rgbDist = (a, b) => { const p = hexRgb(a), q = hexRgb(b); return Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]); };
const shade = (h, k) => { const [r, g, b] = hexRgb(h), f = v => Math.max(0, Math.min(255, Math.round(v * k))); return `rgb(${f(r)},${f(g)},${f(b)})`; };
const inkOn = h => lumOf(h) > .4 ? "#101418" : "#FFFFFF";
const FONT = "'Barlow Condensed', 'Arial Narrow', 'Helvetica Neue', sans-serif";

/* The two kits: a club plays in its primary colour; when the two would look alike under the lights, the away club turns its colours round. */
function kitsFor(H, A) {
  const mk = c => ({ jersey: c.colors[0], pants: c.colors[1] || "#D8D8D8", helmet: c.colors[1] || "#D8D8D8", trim: c.colors[2] || "#FFFFFF" });
  const kh = mk(H), ka = mk(A);
  if (rgbDist(kh.jersey, ka.jersey) < 110 || Math.abs(lumOf(kh.jersey) - lumOf(ka.jersey)) < .06) { const t = ka.jersey; ka.jersey = ka.pants; ka.pants = t; ka.helmet = t; }
  if (rgbDist(kh.jersey, ka.jersey) < 110) { ka.jersey = "#F1F1F1"; ka.trim = A.colors[0]; }
  return [kh, ka];
}

function Stage(cv, o) {
  this.cv = cv; this.g = cv.getContext("2d"); this.club = [o.H, o.A]; this.kit = kitsFor(o.H, o.A); this.abbr = [o.H.abbr, o.A.abbr];
  this.rest = null; this.ball = { x: 60, y: MID, z: 0, spin: 0, held: false };
  this.scene = null; this.t = 0; this.L = 0; this.from = null; this.rate = 1; this.tw = null; this.pend = null;
  this.cam = 60; this.sit = null; this.lineLos = null; this.lineFd = null; this.tLos = null; this.tFd = null;
  this.raf = 0; this.last = 0; this.clock = 0; this.layer = null; this.layerKey = ""; this.prevBall = null; this.ballAng = 0;
  this.dead = false; this.stats = { animated: 0, snapped: 0 };
  this.onResize = () => { this.size(); this.draw(); };
  window.addEventListener("resize", this.onResize);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { this.layerKey = ""; if (!this.dead) this.draw(); });
  this.size();
}
Stage.prototype = {
  size() {
    const cv = this.cv, w = Math.max(200, cv.clientWidth || 600), h = Math.max(100, cv.clientHeight || Math.round(w / 3.1)), dpr = Math.min(2, window.devicePixelRatio || 1);
    this.W = w; this.Hh = h; this.dpr = dpr; cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
    this.vis = w < 560 ? 30 : 44; this.PX = w / this.vis;
    this.yB = h * .19; this.yF0 = h * .265; this.yF1 = h * .92; this.hF = this.yF1 - this.yF0;
  },
  /* the screen position and scale of a world point */
  sx(x) { return (x - (this.cam - this.vis / 2)) * this.PX; },
  sy(v, z) { return this.yF0 + (v / FW) * this.hF - (z || 0) * this.PX * .62; },
  sc(v) { return this.PX * (.7 + .26 * (v / FW)); },

  show(sit, o) {
    o = o || {};
    if (this.scene && !o.snap) { this.pend = [sit, o]; return; }
    this.pend = null;
    if (!sit) { this.tLos = this.tFd = null; if (o.snap) { this.lineLos = this.lineFd = null; } this.kick(); return; }
    const kind = o.kind === "FG" || o.kind === "PU" ? o.kind : "N", los = wxOf(sit.off, sit.pos), toGoal = sit.pos + sit.toGo >= 100;
    this.sit = sit; this.tLos = o.dim ? null : los; this.tFd = toGoal || o.dim ? null : wxOf(sit.off, sit.pos + sit.toGo);
    const to = formation(sit.off, sit.pos, kind, kind === "PU" ? clamp(o.retU == null ? 40 : o.retU, 12, 100 - sit.pos + 6) : null).map(p => ({ x: p[0], y: p[1], pose: p[2], face: p[3] }));
    const bx = wxOf(sit.off, sit.pos);
    if (o.snap || !this.rest || this.far(this.rest, to) > 32) {
      this.scene = null; this.tw = null; this.rest = to; this.ball = { x: bx, y: MID, z: 0, spin: 0, held: false };
      this.cam = los; this.lineLos = this.tLos; this.lineFd = this.tFd; this.draw(); this.fire();
    } else {
      this.tw = { from: this.rest, to, t: 0, L: clamp(this.far(this.rest, to) / 7, .5, 2.2), bx };
      this.kick();
    }
  },
  /* onsettle: one function the page sets to be called when the play on the field is over (or shown as its result); used to move the page's own panels on after the play */
  fire() { const f = this.onsettle; this.onsettle = null; if (f) f(); },
  far(a, b) { let m = 0; for (let i = 0; i < 22; i++) m = Math.max(m, Math.hypot(a[i].x - b[i].x, a[i].y - b[i].y)); return m; },
  settle() {
    if (this.scene) { const e = sampleScene(this.scene, this.scene.dur + 1); this.rest = e.act; this.ball = e.ball; this.scene = null; this.fire(); }
    if (this.tw) { this.rest = this.tw.to; this.ball = { x: this.tw.bx, y: MID, z: 0, spin: 0, held: false }; this.tw = null; }
  },
  /* play(scene, avail): animate a scene; avail is the real time in seconds before the next play is due (null: take the time it needs). Returns false when it was shown as the result only. */
  play(sc, avail) {
    this.settle(); this.pend = null;
    const start = sc.start.map(p => ({ x: p[0], y: p[1], pose: p[2], face: p[3] }));
    let L = 0;
    if (!this.rest || this.far(this.rest, start) > 32) { this.rest = start; this.ball = sampleBall(sc, 0, start); }
    else { const f = this.far(this.rest, start); L = f < .6 ? 0 : clamp(f / 7, .4, 2.2); }
    const need = L + sc.dur; this.rate = avail != null ? Math.max(1, need / Math.max(.3, avail * .96)) : 1;
    if (this.rate > 3.5) { const e = sampleScene(sc, sc.dur + 1); this.rest = e.act; this.ball = e.ball; this.cam = clamp(e.ball.x, this.vis / 2 - 3, 123 - this.vis / 2); this.rate = 1; this.stats.snapped++; this.draw(); return false; }
    this.scene = sc; this.t = -L; this.L = L; this.from = this.rest; this.stats.animated++;
    this.kick(); return true;
  },
  kick() { if (!this.raf && !this.dead) { this.last = 0; this.raf = requestAnimationFrame(ts => this.tick(ts)); } },
  tick(ts) {
    this.raf = 0; if (this.dead) return;
    const dt = this.last ? Math.min(.05, (ts - this.last) / 1000) : .016; this.last = ts; this.clock += dt;
    let busy = false;
    if (this.scene) {
      this.t += dt * this.rate; busy = true;
      if (this.t >= this.scene.dur) { this.settle(); busy = false; if (this.pend) { const [s, o] = this.pend; this.pend = null; this.show(s, o); busy = !!this.tw; } }
    } else if (this.tw) {
      this.tw.t += dt; busy = true; if (this.tw.t >= this.tw.L) { this.settle(); busy = false; }
    }
    // the camera follows the ball while a play runs and the line of scrimmage between plays
    const target = this.scene && this.t > 0 ? (this.cur || this.current()).ball.x + this.scene.dir * 2 : this.sit ? wxOf(this.sit.off, this.sit.pos) : this.cam;
    const k = Math.min(1, dt * (this.scene && this.t > 0 ? 5 : 3.2)); const half = this.vis / 2;
    const cx = clamp(target, half - 3, 120 - half + 3); this.cam += (cx - this.cam) * k; if (Math.abs(cx - this.cam) > .03) busy = true;
    for (const nm of ["Los", "Fd"]) { const tg = this["t" + nm], cu = this["line" + nm]; if (tg == null) this["line" + nm] = null; else if (cu == null) this["line" + nm] = tg; else { this["line" + nm] += (tg - cu) * Math.min(1, dt * 7); if (Math.abs(tg - this["line" + nm]) > .02) busy = true; } }
    this.draw();
    if (busy) this.kick();
  },
  /* the state to draw now: figures, ball, banners, tags */
  current() {
    if (this.scene) {
      const t = this.t;
      if (t < 0) {                                       // the lineup before the snap: from where they stood to the formation
        const u = sstep((t + this.L) / this.L), sc = this.scene, act = sc.start.map((p, i) => { const f = this.from[i]; return { x: lerp(f.x, p[0], u), y: lerp(f.y, p[1], u), pose: u < 1 ? "run" : p[2], face: p[0] - f.x > .05 ? 1 : p[0] - f.x < -.05 ? -1 : p[3], sp: 1 }; });
        if (u >= 1) act.forEach((a, i) => { a.pose = sc.start[i][2]; a.face = sc.start[i][3]; });
        return { act, ball: sampleBall(sc, 0, act), ev: [], t };
      }
      const s = sampleScene(this.scene, t); return { act: s.act, ball: s.ball, ev: this.scene.ev, t };
    }
    if (this.tw) {
      const u = sstep(this.tw.t / this.tw.L), act = this.tw.to.map((p, i) => { const f = this.tw.from[i]; return { x: lerp(f.x, p.x, u), y: lerp(f.y, p.y, u), pose: u < 1 ? "run" : p.pose, face: p.x - f.x > .05 ? 1 : p.x - f.x < -.05 ? -1 : p.face, sp: 1 }; });
      return { act, ball: { x: this.tw.bx, y: MID, z: 0, spin: 0, held: false }, ev: [], t: 0 };
    }
    return { act: this.rest || [], ball: this.ball, ev: [], t: 0 };
  },
  /* draw one instant of a scene without running it (screenshots and checks) */
  showAt(sc, t) { this.settle(); this.scene = sc; this.t = t; this.L = 0; this.from = sc.start.map(p => ({ x: p[0], y: p[1] })); const s = sampleScene(sc, t); this.cur = { ball: s.ball }; this.cam = clamp(s.ball.x + sc.dir * 2, this.vis / 2 - 3, 123 - this.vis / 2); this.tLos = sc.los; this.lineLos = sc.los; this.draw(); },
  destroy() { this.dead = true; if (this.raf) cancelAnimationFrame(this.raf); this.raf = 0; window.removeEventListener("resize", this.onResize); },

  draw() {
    if (this.dead) return;
    const g = this.g, cur = this.current(); this.cur = cur;
    g.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.drawField(g);
    this.drawLines(g);
    // figures and the ball, far side first
    const items = [], PXs = this.PX;
    (cur.act || []).forEach((a, i) => { const team = i < 11 ? 0 : 1; items.push({ y: a.y, f: () => this.drawPlayer(g, a, Math.floor(i / 11), i) }); });
    const b = cur.ball;
    if (b) {
      if (b.held) { const who = cur.act[b.who]; items.push({ y: (who ? who.y : b.y) + .02, f: () => this.drawBall(g, b) }); }
      else items.push({ y: b.y, f: () => this.drawBall(g, b) });
    }
    if (cur.ev) cur.ev.forEach(e => { if (e.k === "flag" && cur.t >= e.t0) items.push({ y: e.y, f: () => this.drawFlag(g, e, cur.t - e.t0) }); });
    items.sort((p, q) => p.y - q.y).forEach(it => it.f());
    this.drawGoalposts(g, true);
    if (cur.ev) { this.drawTags(g, cur); this.drawBanners(g, cur); }
  },

  /* ---- the static field, drawn once per size and reused as the camera moves ---- */
  drawField(g) {
    const key = [this.W, this.Hh, this.dpr, this.abbr.join(), this.club[0].colors[0], this.club[1].colors[0]].join("|");
    if (key !== this.layerKey) { this.layer = this.buildLayer(); this.layerKey = key; }
    const left = this.cam - this.vis / 2 + 4, d = this.dpr, PXd = this.PX * d;       // the layer starts four yards outside the end line, so that the goal posts can be seen
    g.drawImage(this.layer, left * PXd, 0, this.W * d, this.Hh * d, 0, 0, this.W, this.Hh);
  },
  buildLayer() {
    const d = this.dpr, PXd = this.PX * d, w = Math.ceil(128 * PXd), h = Math.ceil(this.Hh * d), cv = document.createElement("canvas"); cv.width = w; cv.height = h;
    const g = cv.getContext("2d"); g.scale(d, d); g.translate(4 * this.PX, 0); const PX = this.PX, W = 120 * PX, X0 = -4 * PX, WW = 128 * PX, yB = this.yB, yF0 = this.yF0, yF1 = this.yF1, hF = this.hF, H = this.Hh;
    // the stands under the lights
    let gr = g.createLinearGradient(0, 0, 0, yB); gr.addColorStop(0, "#05070B"); gr.addColorStop(1, "#141B27"); g.fillStyle = gr; g.fillRect(X0, 0, WW, yB + 1);
    const r = rng(77);
    for (let i = 0; i < WW / 4.2; i++) { const x = X0 + r() * WW, y = r() * (yB - 6) + 2, c = ["#2A3550", "#3A2F3F", "#1E2A3E", "#46405A", "#5A4A3A", "#2B3B4A"][(r() * 6) | 0]; g.fillStyle = c; g.globalAlpha = .55 + r() * .4; g.fillRect(x, y, 2.4, 3.2); }
    g.globalAlpha = 1;
    for (const lx of [W * .12, W * .38, W * .64, W * .9]) { const rg = g.createRadialGradient(lx, 0, 2, lx, 0, yB * 1.5); rg.addColorStop(0, "rgba(255,247,214,.55)"); rg.addColorStop(1, "rgba(255,247,214,0)"); g.fillStyle = rg; g.fillRect(lx - yB * 1.6, 0, yB * 3.2, yB * 1.6); }
    // the boards along the near wall
    g.fillStyle = "#0C1118"; g.fillRect(X0, yB, WW, yF0 - yB);
    const bw = 6 * PX; for (let i = 0; i < 20; i++) { const c = i % 3 === 0 ? this.club[1].colors[0] : i % 3 === 1 ? this.club[0].colors[0] : "#1B2330"; g.fillStyle = c; g.fillRect(i * bw + 2, yB + 3, bw - 4, yF0 - yB - 5); g.fillStyle = inkOn(c); const fsz = Math.max(9, (yF0 - yB) * .6); g.font = `italic 800 ${fsz}px ${FONT}`; g.textAlign = "center"; g.textBaseline = "middle"; const tx = i % 3 === 2 ? "DIAMOND FOOTBALL LEAGUE" : "DFL", tw = g.measureText(tx).width; if (tw > bw - 14) g.font = `italic 800 ${fsz * (bw - 14) / tw}px ${FONT}`; g.fillText(tx, i * bw + bw / 2, yB + (yF0 - yB) / 2 + 1); }
    // the turf, five-yard stripes
    g.fillStyle = "#16572F"; g.fillRect(X0, yF0, WW, hF);
    for (let i = 0; i < 20; i++) { g.fillStyle = i % 2 ? "#207745" : "#1B6B3C"; g.fillRect((10 + i * 5) * PX, yF0, 5 * PX, hF); }
    gr = g.createLinearGradient(0, yF0, 0, yF1); gr.addColorStop(0, "rgba(0,0,0,.34)"); gr.addColorStop(.4, "rgba(0,0,0,0)"); gr.addColorStop(1, "rgba(0,0,0,.2)"); g.fillStyle = gr; g.fillRect(X0, yF0, WW, hF);
    // the end zones, in the clubs' colours: the away club defends the left one
    [[0, this.club[1]], [110, this.club[0]]].forEach(([x0, c]) => {
      g.fillStyle = c.colors[0]; g.fillRect(x0 * PX, yF0, 10 * PX, hF); g.fillStyle = "rgba(0,0,0,.28)"; g.fillRect(x0 * PX, yF0, 10 * PX, hF);
      g.save(); g.translate((x0 + 5) * PX, yF0 + hF / 2); g.rotate(x0 ? Math.PI / 2 : -Math.PI / 2); g.fillStyle = inkOn(c.colors[0]); g.globalAlpha = .92; let fz = Math.min(10 * PX * .8, hF * .5); g.font = `italic 800 ${fz}px ${FONT}`; const tw = g.measureText(c.abbr).width; if (tw > hF * .8) { fz *= hF * .8 / tw; g.font = `italic 800 ${fz}px ${FONT}`; } g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(c.abbr, 0, 2); g.restore();
    });
    // the lines
    g.strokeStyle = "rgba(255,255,255,.8)"; g.lineWidth = 1.5;
    for (let i = 0; i <= 20; i++) { const x = (10 + i * 5) * PX, big = i % 2 === 0; g.globalAlpha = i === 0 || i === 20 ? 1 : big ? .85 : .5; g.lineWidth = i === 0 || i === 20 ? 3 : 1.5; g.beginPath(); g.moveTo(x, yF0); g.lineTo(x, yF1); g.stroke(); }
    g.globalAlpha = 1; g.lineWidth = 3; g.strokeStyle = "rgba(255,255,255,.9)"; for (const v of [0, FW]) { const y = yF0 + (v / FW) * hF; g.beginPath(); g.moveTo(X0, y); g.lineTo(W - X0, y); g.stroke(); }
    g.strokeStyle = "rgba(255,255,255,.55)"; g.lineWidth = 1.2;       // hash marks every yard
    for (const v of [23.4, 29.9]) { const y = yF0 + (v / FW) * hF; for (let x = 11; x < 110; x++) { g.beginPath(); g.moveTo(x * PX, y - 2); g.lineTo(x * PX, y + 2); g.stroke(); } }
    g.fillStyle = "rgba(255,255,255,.62)"; g.textAlign = "center"; g.textBaseline = "middle";
    for (let i = 1; i < 10; i++) { const num = i <= 5 ? i * 10 : (10 - i) * 10, x = (10 + i * 10) * PX; g.font = `italic 800 ${hF * .15}px ${FONT}`; g.fillText(String(num), x, yF0 + hF * .14); g.fillText(String(num), x, yF0 + hF * .86); }
    // the diamond at midfield
    g.save(); g.translate(60 * PX, yF0 + hF / 2); g.rotate(Math.PI / 4); g.fillStyle = "rgba(255,255,255,.2)"; const ds = Math.min(hF * .22, 7 * PX); g.fillRect(-ds / 2, -ds / 2, ds, ds); g.restore();
    // the sideline below the field
    gr = g.createLinearGradient(0, yF1, 0, H); gr.addColorStop(0, "#0E1912"); gr.addColorStop(1, "#05080A"); g.fillStyle = gr; g.fillRect(X0, yF1, WW, H - yF1);
    for (let i = 0; i < 22; i++) { const x = (10 + r() * 100) * PX, hh = (H - yF1) * (.5 + r() * .35); g.fillStyle = ["#0B0F14", "#10161E", "#171E28"][(r() * 3) | 0]; g.fillRect(x, H - hh, 5 + r() * 4, hh); g.beginPath(); g.arc(x + 3, H - hh - 2, 3, 0, 7); g.fill(); }
    return cv;
  },
  /* the goal posts stand at the back of each end zone; the near one is drawn over the players */
  drawGoalposts(g, front) {
    for (const x of [0, 120]) {
      const px = this.sx(x); if (px < -30 || px > this.W + 30) continue;
      const yb = this.sy(MID, 0), yc = this.sy(MID, 3.3), ya = this.sy(MID - 3.1, 3.3), yz = this.sy(MID + 3.1, 3.3), top = this.sy(MID, 9);
      g.strokeStyle = "#FFD21F"; g.lineWidth = Math.max(2, this.PX * .16); g.lineCap = "round";
      g.beginPath(); g.moveTo(px, yb); g.lineTo(px, yc); g.stroke();
      g.beginPath(); g.moveTo(px, ya); g.lineTo(px, yz); g.stroke();
      g.lineWidth = Math.max(1.6, this.PX * .12);
      g.beginPath(); g.moveTo(px, ya); g.lineTo(px, this.sy(MID - 3.1, 9.5)); g.moveTo(px, yz); g.lineTo(px, this.sy(MID + 3.1, 9.5)); g.stroke();
    }
  },
  drawLines(g) {
    const yTop = this.yF0, yBot = this.yF1;
    const line = (x, col, w) => { if (x == null) return; const px = this.sx(x); if (px < -10 || px > this.W + 10) return; g.save(); g.shadowColor = col; g.shadowBlur = 10; g.strokeStyle = col; g.lineWidth = w; g.globalAlpha = .95; g.beginPath(); g.moveTo(px, yTop); g.lineTo(px, yBot); g.stroke(); g.restore(); };
    line(this.lineFd, "#FFD21F", 3); line(this.lineLos, "#3D8BFF", 3);
  },

  /* ---- a figure ---- */
  drawPlayer(g, a, team, idx) {
    const PX = this.PX, s = this.sc(a.y), sx = this.sx(a.x), sy = this.sy(a.y, 0), kit = this.kit[team], f = a.face >= 0 ? 1 : -1;
    if (sx < -60 || sx > this.W + 60) return;
    let pose = a.pose === "back" ? "run" : a.pose || "stand";
    const ph = (a.x + a.y * .6) * 3.7, moving = pose === "run", sw = Math.sin(ph), skin = SKIN[idx % SKIN.length];
    // shadow
    g.fillStyle = "rgba(0,0,0,.34)"; g.beginPath(); g.ellipse(sx, sy + 1, s * (pose === "down" ? 1.5 : .62), s * .17, 0, 0, 7); g.fill();
    g.save(); g.translate(sx, sy); g.scale(f, 1);
    const LEG = .56 * s, hipY = -1.06 * s;
    let lean = 0, th1 = .08, th2 = -.1, fl1 = .1, fl2 = .1, hy = hipY, arm1 = .15, arm2 = -.1, el1 = .35, el2 = .35, bob = 0;
    if (moving) { th1 = .95 * sw; th2 = -.95 * sw; fl1 = .3 + .75 * (1 + Math.sin(ph - 1.3)) / 2; fl2 = .3 + .75 * (1 + Math.sin(ph + Math.PI - 1.3)) / 2; lean = .22; arm1 = -.95 * sw; arm2 = .95 * sw; el1 = el2 = 1.25; bob = Math.abs(sw) * .09 * s; }
    else if (pose === "stance") { lean = .85; th1 = .75; th2 = -.35; fl1 = 1.0; fl2 = .4; hy = -.82 * s; arm1 = 1.5; el1 = .1; arm2 = -.5; el2 = .6; }
    else if (pose === "kneel") { lean = .35; th1 = 1.2; th2 = -.3; fl1 = 1.5; fl2 = 1.2; hy = -.62 * s; arm1 = 1.0; el1 = .6; arm2 = .8; el2 = .6; }
    else if (pose === "block") { lean = .38; th1 = .55; th2 = -.4; fl1 = .55; fl2 = .35; hy = -.98 * s; arm1 = 1.35; el1 = .8; arm2 = 1.2; el2 = .9; }
    else if (pose === "tackle") { lean = .95; th1 = .9; th2 = -.7; fl1 = .5; fl2 = .6; hy = -.9 * s; arm1 = 1.55; el1 = .15; arm2 = 1.3; el2 = .2; }
    else if (pose === "throw") { lean = -.08; th1 = .35; th2 = -.35; fl1 = .25; fl2 = .15; arm1 = -2.5; el1 = .9; arm2 = 1.0; el2 = .3; }
    else if (pose === "catch") { lean = -.05; th1 = .15; th2 = -.15; arm1 = -2.85; el1 = .1; arm2 = -2.55; el2 = .15; bob = Math.abs(Math.sin(this.clock * 9)) * .05 * s; }
    else if (pose === "cele") { th1 = .2; th2 = -.2; arm1 = -3.0; el1 = .1; arm2 = -2.7; el2 = .1; bob = Math.abs(Math.sin(this.clock * 8)) * .35 * s; }
    else if (pose === "kick") { lean = -.22; th1 = 1.55; th2 = -.2; fl1 = .1; fl2 = .15; arm1 = -.9; el1 = .4; arm2 = 1.0; el2 = .4; }
    else if (pose === "down") { g.rotate(1.5); g.translate(0, -.05 * s); lean = 0.1; th1 = .3; th2 = -.2; fl1 = .5; fl2 = .3; arm1 = 1.2; el1 = .5; arm2 = .3; el2 = .3; }
    hy -= bob;
    const leg = (th, fl, col, far) => {
      const hx = far ? -.05 * s : .05 * s, kx = hx + Math.sin(th) * LEG, ky = hy + Math.cos(th) * LEG, ax = kx + Math.sin(th - fl) * LEG * 1.02, ay = ky + Math.cos(th - fl) * LEG * 1.02;
      g.strokeStyle = far ? shade(kit.pants, .72) : kit.pants; g.lineWidth = .3 * s; g.lineCap = "round"; g.lineJoin = "round";
      g.beginPath(); g.moveTo(hx, hy); g.lineTo(kx, ky); g.stroke(); g.lineWidth = .24 * s; g.strokeStyle = far ? shade(kit.pants, .6) : shade(kit.pants, .9); g.beginPath(); g.moveTo(kx, ky); g.lineTo(ax, ay); g.stroke();
      g.fillStyle = "#0B0D10"; g.beginPath(); g.ellipse(ax + .08 * s, ay + .02 * s, .17 * s, .08 * s, 0, 0, 7); g.fill();
    };
    leg(th2, fl2, kit.pants, true); leg(th1, fl1, kit.pants, false);
    // torso, head and arms turn together about the hips
    g.save(); g.translate(0, hy); g.rotate(lean);
    const arm = (al, el, far) => {
      const sxo = (far ? -.06 : .06) * s, syo = -.86 * s, ex = sxo + Math.sin(al) * .46 * s, ey = syo + Math.cos(al) * .46 * s, hx = ex + Math.sin(al + el) * .42 * s, hyy = ey + Math.cos(al + el) * .42 * s;
      g.strokeStyle = far ? shade(kit.jersey, .7) : kit.jersey; g.lineWidth = .21 * s; g.lineCap = "round"; g.beginPath(); g.moveTo(sxo, syo); g.lineTo(ex, ey); g.stroke();
      g.strokeStyle = far ? shade(skin, .75) : skin; g.lineWidth = .15 * s; g.beginPath(); g.moveTo(ex, ey); g.lineTo(hx, hyy); g.stroke();
    };
    arm(arm2, el2, true);
    g.fillStyle = kit.jersey; g.beginPath(); g.moveTo(-.2 * s, 0); g.lineTo(.2 * s, 0); g.lineTo(.3 * s, -.78 * s); g.quadraticCurveTo(0, -.98 * s, -.3 * s, -.78 * s); g.closePath(); g.fill();
    g.fillStyle = kit.trim; g.globalAlpha = .9; g.fillRect(-.22 * s, -.16 * s, .44 * s, .06 * s); g.globalAlpha = 1;
    g.fillStyle = kit.pants; g.fillRect(-.21 * s, -.02 * s, .42 * s, .1 * s);
    // the helmet
    const hr = .34 * s, hcx = .08 * s, hcy = -1.22 * s;
    g.fillStyle = shade(skin, .9); g.fillRect(-.05 * s, -1.0 * s, .18 * s, .16 * s);
    g.fillStyle = kit.helmet; g.beginPath(); g.arc(hcx, hcy, hr, 0, 7); g.fill();
    g.strokeStyle = kit.jersey === kit.helmet ? kit.trim : kit.jersey; g.lineWidth = .08 * s; g.beginPath(); g.arc(hcx, hcy, hr * .98, Math.PI * 1.1, Math.PI * 1.9); g.stroke();
    g.strokeStyle = "#D8DDE3"; g.lineWidth = .06 * s; g.beginPath(); g.moveTo(hcx + hr * .6, hcy - hr * .15); g.lineTo(hcx + hr * 1.12, hcy + hr * .2); g.lineTo(hcx + hr * .55, hcy + hr * .72); g.stroke();
    g.fillStyle = "rgba(255,255,255,.28)"; g.beginPath(); g.ellipse(hcx - hr * .25, hcy - hr * .45, hr * .3, hr * .16, -.5, 0, 7); g.fill();
    arm(arm1, el1, false);
    g.restore();
    g.restore();
  },
  drawBall(g, b) {
    const PX = this.PX, sx = this.sx(b.x), sy = this.sy(b.y, b.z);
    if (sx < -20 || sx > this.W + 20) return;
    const gy = this.sy(b.y, 0), s = this.sc(b.y);
    if (b.z > .15) { g.fillStyle = "rgba(0,0,0,.3)"; g.beginPath(); g.ellipse(sx, gy + 1, s * .3, s * .09, 0, 0, 7); g.fill(); }
    // a ball in the air points along its flight
    if (this.prevBall) { const dx = sx - this.prevBall[0], dy = sy - this.prevBall[1]; if (!b.held && b.flying && Math.hypot(dx, dy) > .5) this.ballAng = Math.atan2(dy, dx); else if (b.held || !b.flying) this.ballAng = this.ballAng * .8; }
    this.prevBall = [sx, sy];
    g.save(); g.translate(sx, sy - (b.held ? 0 : s * .1)); g.rotate(this.ballAng + (b.flying ? Math.sin(b.spin) * .15 : 0));
    const L = s * .5, Hh = s * .29;
    g.fillStyle = "#9A5F2B"; g.strokeStyle = "#1A0F06"; g.lineWidth = Math.max(1, s * .04); g.beginPath(); g.ellipse(0, 0, L, Hh, 0, 0, 7); g.fill(); g.stroke();
    g.strokeStyle = "#fff"; g.lineWidth = Math.max(1, s * .035); g.beginPath(); g.moveTo(-L * .35, 0); g.lineTo(L * .35, 0); g.stroke();
    g.restore();
  },
  drawFlag(g, e, age) {
    const sx = this.sx(e.x), z = Math.max(0, 3 * (1 - Math.min(1, age / .5))), sy = this.sy(e.y, z), s = this.sc(e.y);
    if (sx < -20 || sx > this.W + 20) return;
    g.fillStyle = "rgba(0,0,0,.3)"; g.beginPath(); g.ellipse(sx, this.sy(e.y, 0) + 1, s * .25, s * .07, 0, 0, 7); g.fill();
    g.save(); g.translate(sx, sy - s * .12); g.rotate(age < .5 ? age * 12 : Math.sin(this.clock * 6) * .1); g.fillStyle = "#FFD21F"; g.strokeStyle = "#7A5C00"; g.lineWidth = 1; g.fillRect(-s * .22, -s * .12, s * .44, s * .24); g.strokeRect(-s * .22, -s * .12, s * .44, s * .24); g.restore();
  },
  drawTags(g, cur) {
    for (const e of cur.ev) {
      if (e.k !== "tag" || cur.t < e.t0 || cur.t > e.t1) continue;
      const a = cur.act[e.a]; if (!a) continue;
      const team = Math.floor(e.a / 11), kit = this.kit[team], s = this.sc(a.y), sx = this.sx(a.x), sy = this.sy(a.y, 0) - 3.25 * s, fs = Math.max(11, Math.min(15, this.PX * .55));
      g.font = `italic 800 ${fs}px ${FONT}`; const w = g.measureText(e.text.toUpperCase()).width + 24, x = clamp(sx - w / 2, 4, this.W - w - 4), y = clamp(sy, 4, this.Hh - 20);
      g.fillStyle = "rgba(8,12,16,.86)"; g.beginPath(); g.moveTo(x + 5, y); g.lineTo(x + w, y); g.lineTo(x + w - 5, y + fs + 6); g.lineTo(x, y + fs + 6); g.closePath(); g.fill();
      g.fillStyle = kit.jersey; g.fillRect(x + 1, y, 3, fs + 6);
      g.fillStyle = "#fff"; g.textAlign = "left"; g.textBaseline = "middle"; g.fillText(e.text.toUpperCase(), x + 9, y + (fs + 6) / 2 + 1);
    }
  },
  drawBanners(g, cur) {
    const W = this.W, k = W / 960;
    for (const e of cur.ev) {
      if (e.k !== "banner" || cur.t < e.t0 || cur.t > e.t1) continue;
      const age = cur.t - e.t0, left = e.t1 - cur.t, slide = 1 - Math.pow(1 - Math.min(1, age / .24), 3), alpha = Math.min(1, left / .3);
      const small = e.cls === "small", h = (small ? 38 : e.sub ? 74 : 60) * Math.max(.7, k), y = small ? this.Hh * .29 : this.Hh * .11, w = W * (small ? .42 : .78), x = (W - w) / 2 - (1 - slide) * W * .5;
      const col = e.cls === "good" ? "#FFD21F" : e.cls === "bad" ? "#C93434" : e.cls === "flag" ? "#FFD21F" : e.cls === "plain" ? "#274A8C" : "rgba(8,12,16,.88)";
      const ink = e.cls === "good" || e.cls === "flag" ? "#14190A" : "#fff";
      g.save(); g.globalAlpha = alpha; g.fillStyle = col; g.beginPath(); const sk = h * .3; g.moveTo(x + sk, y); g.lineTo(x + w, y); g.lineTo(x + w - sk, y + h); g.lineTo(x, y + h); g.closePath(); g.fill();
      if (!small) { g.fillStyle = "rgba(0,0,0,.18)"; g.fillRect(x + sk, y + h - 5, w - sk * 2, 5); }
      g.fillStyle = ink; g.textAlign = "center"; g.textBaseline = "middle";
      const fs = (small ? 24 : 42) * Math.max(.7, k); g.font = `italic 800 ${fs}px ${FONT}`;
      g.fillText(e.text, x + w / 2, y + (e.sub && !small ? h * .38 : h / 2) + 1);
      if (e.sub && !small) { g.font = `italic 700 ${20 * Math.max(.7, k)}px ${FONT}`; g.globalAlpha = alpha * .85; g.fillText(e.sub.toUpperCase(), x + w / 2, y + h * .76); }
      else if (e.sub && small) { g.font = `italic 700 ${15 * Math.max(.7, k)}px ${FONT}`; g.globalAlpha = alpha * .8; }
      g.restore();
    }
  },
};


/* where the ball is when the scene ends, as a spot in the offense's frame (the checks compare it with the log) */
const endSpot = S => { const b = endBall(S); return (b.x - S.los) * S.dir + S.pos; };

root.DFLStage = { buildScene, sampleScene, sampleTrack, sampleBall, endBall, endSpot, formation, lineup, wxOf, dirOf, rng, clamp, lerp, sstep, Scene, Stage, kitsFor, OFF_F, DEF_F, FW, MID };
if (typeof module !== "undefined" && module.exports) module.exports = root.DFLStage;
})(typeof window !== "undefined" ? window : globalThis);
