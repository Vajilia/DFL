/* The DFL chalkboard: a flat, top-down view of the field (site/chalk.js). Same scenes as the sprite field; only the drawing is new.

   The 22 players are dots (a number and the club's colours). While a play runs the dots move as the scene says; when it is over, the call the coordinators most likely made is drawn
   on the board after the fact, like the blue and yellow lines: where each player was supposed to go and what he was to do, with a mark on the ones who won or lost their matchup.
   The call is a reconstruction (site/playcalls.js); the log decides everything that happened and this file only draws.

   Stage (site/stage.js) calls  DFLChalk.layout(stage)  when the view is chosen or the window changes, and  DFLChalk.draw(stage, g, cur)  for every frame.                       */
(function (root) {
"use strict";
const FW = 53.3, MID = 26.65, PAD = 2.4;
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const FONT = "'Barlow Condensed', 'Arial Narrow', 'Helvetica Neue', sans-serif";
const lumOf = h => { const m = /^#?([0-9a-f]{6})$/i.exec(h || ""); if (!m) return .3; const n = parseInt(m[1], 16); return (.299 * (n >> 16) + .587 * ((n >> 8) & 255) + .114 * (n & 255)) / 255; };
const inkOn = h => lumOf(h) > .45 ? "#101418" : "#FFFFFF";

function layout(S) {
  const w = Math.max(240, S.cv.clientWidth || 600);
  S.vis = w < 560 ? 46 : 76;
  S.cPX = w / S.vis;
  const h = Math.round((FW + 2 * PAD) * S.cPX);
  S.cv.style.height = h + "px";
  S.W = w; S.Hh = h; S.dpr = Math.min(2, window.devicePixelRatio || 1);
  S.cv.width = Math.round(w * S.dpr); S.cv.height = Math.round(h * S.dpr);
}
const leave = S => { S.cv.style.height = ""; };

function map(S) { const px = S.cPX, x0 = S.cam - S.vis / 2; return { px, X: x => (x - x0) * px, Y: y => (PAD + y) * px }; }

function drawField(S, g, M) {
  const { px, X, Y } = M, W = S.W, H = S.Hh, x0 = S.cam - S.vis / 2, x1 = S.cam + S.vis / 2;
  g.fillStyle = "#0B1A12"; g.fillRect(0, 0, W, H);
  // the turf, mown in five-yard stripes
  for (let x = Math.floor(x0 / 5) * 5; x < x1; x += 5) {
    if (x < 10 || x >= 110) continue;
    g.fillStyle = ((x - 10) / 5) % 2 === 0 ? "#1C4A2E" : "#1F5233"; g.fillRect(X(x), Y(0), 5 * px, FW * px);
  }
  // the end zones, in each club's colour
  const ez = (xa, xb, club, label, flip) => {
    if (xb < x0 || xa > x1) return;
    g.fillStyle = club.colors[0]; g.globalAlpha = .82; g.fillRect(X(xa), Y(0), (xb - xa) * px, FW * px); g.globalAlpha = 1;
    g.save(); g.translate(X((xa + xb) / 2), Y(MID)); g.rotate(flip ? Math.PI / 2 : -Math.PI / 2);
    g.fillStyle = inkOn(club.colors[0]); g.globalAlpha = .8; g.font = `800 ${Math.round(px * 3.6)}px ${FONT}`; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(label.toUpperCase(), 0, 0); g.restore(); g.globalAlpha = 1;
  };
  ez(0, 10, S.club[0], S.club[0].name.split(" ").pop(), false);
  ez(110, 120, S.club[1], S.club[1].name.split(" ").pop(), true);
  // the boundary and the yard lines
  g.strokeStyle = "rgba(255,255,255,.9)"; g.lineWidth = 2; g.strokeRect(X(0), Y(0), 120 * px, FW * px);
  g.lineWidth = 1;
  for (let x = Math.ceil(x0); x <= x1; x++) {
    if (x < 10 || x > 110) { if (x === 0 || x === 120) continue; continue; }
    const five = (x - 10) % 5 === 0, ten = (x - 10) % 10 === 0;
    g.strokeStyle = five ? "rgba(255,255,255,.75)" : "rgba(255,255,255,.28)"; g.lineWidth = ten ? 1.6 : 1;
    if (five) { g.beginPath(); g.moveTo(X(x), Y(0)); g.lineTo(X(x), Y(FW)); g.stroke(); }
    else { for (const yy of [0, 1, 22.9, 29.5, FW - 1]) { g.beginPath(); g.moveTo(X(x), Y(yy)); g.lineTo(X(x), Y(yy + 1)); g.stroke(); } }
  }
  g.fillStyle = "rgba(255,255,255,.55)"; g.font = `700 ${Math.round(px * 2.6)}px ${FONT}`; g.textAlign = "center"; g.textBaseline = "middle";
  for (let x = 20; x <= 100; x += 10) { if (x < x0 - 3 || x > x1 + 3) continue; const n = x <= 60 ? x - 10 : 110 - x; g.fillText(String(n), X(x), Y(8)); g.save(); g.translate(X(x), Y(FW - 8)); g.rotate(Math.PI); g.fillText(String(n), 0, 0); g.restore(); }
}

function drawLines(S, g, M) {
  const { px, X, Y } = M;
  if (S.lineLos != null) { g.strokeStyle = "#3D8BFF"; g.lineWidth = 3; g.shadowColor = "#3D8BFF"; g.shadowBlur = 8; g.beginPath(); g.moveTo(X(S.lineLos), Y(0)); g.lineTo(X(S.lineLos), Y(FW)); g.stroke(); g.shadowBlur = 0; }
  if (S.lineFd != null) { g.strokeStyle = "#FFD23F"; g.lineWidth = 3; g.shadowColor = "#FFD23F"; g.shadowBlur = 8; g.beginPath(); g.moveTo(X(S.lineFd), Y(0)); g.lineTo(X(S.lineFd), Y(FW)); g.stroke(); g.shadowBlur = 0; }
}

/* the player a dot stands for, from the lineups the page gave the stage: {num, pos, name} */
function who(S, i, off) {
  const club = Math.floor(i / 11), job = i % 11, lu = S.lu && S.lu[club];
  if (!lu) return null;
  const p = (club === off ? lu.o : lu.d)[job];
  return p || null;
}

function drawDot(S, g, M, a, i, off, tagged, carry) {
  const { px, X, Y } = M, club = Math.floor(i / 11), kit = S.kit[club], r = Math.max(6, px * 1.18), x = X(a.x), y = Y(a.y), p = who(S, i, off);
  const down = a.pose === "down";
  g.save(); g.translate(x, y);
  if (a.pose === "cele") { g.strokeStyle = "rgba(255,210,63,.8)"; g.lineWidth = 2; g.beginPath(); g.arc(0, 0, r * 1.5 + Math.sin(S.clock * 9) * 2, 0, 7); g.stroke(); }
  if (carry) { g.strokeStyle = "#FFD23F"; g.lineWidth = 3; g.shadowColor = "#FFD23F"; g.shadowBlur = 10; g.beginPath(); g.arc(0, 0, r * 1.28, 0, 7); g.stroke(); g.shadowBlur = 0; }
  g.globalAlpha = down ? .55 : 1;
  g.fillStyle = kit.jersey; g.beginPath(); g.arc(0, 0, r, 0, 7); g.fill();
  g.lineWidth = Math.max(2, r * .22); g.strokeStyle = club === off ? kit.trim : "rgba(0,0,0,.55)"; g.stroke();
  if (club !== off) { g.setLineDash([r * .5, r * .35]); g.lineWidth = Math.max(1.5, r * .16); g.strokeStyle = kit.trim; g.beginPath(); g.arc(0, 0, r * 1.0, 0, 7); g.stroke(); g.setLineDash([]); }
  // which way he faces
  const f = a.face || 1; g.fillStyle = kit.trim; g.beginPath(); g.moveTo(f * (r + 3.5), 0); g.lineTo(f * (r - .5), -r * .36); g.lineTo(f * (r - .5), r * .36); g.closePath(); g.fill();
  if (down) { g.strokeStyle = "rgba(255,255,255,.8)"; g.lineWidth = 2; g.beginPath(); g.moveTo(-r * .5, -r * .5); g.lineTo(r * .5, r * .5); g.moveTo(r * .5, -r * .5); g.lineTo(-r * .5, r * .5); g.stroke(); }
  else if (p) { g.fillStyle = inkOn(kit.jersey); g.font = `800 ${Math.round(r * 1.05)}px ${FONT}`; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(String(p.num), 0, 1); }
  g.restore();
}

function drawBall(S, g, M, b) {
  const { px, X, Y } = M, x = X(b.x), y = Y(b.y), lift = Math.max(0, b.z || 0), s = 1 + lift * .07;
  g.save(); g.fillStyle = "rgba(0,0,0,.35)"; g.beginPath(); g.ellipse(x + lift * 2, y + lift * 2, px * .5, px * .32, 0, 0, 7); g.fill();
  g.translate(x, y); g.rotate(b.spin || 0); g.scale(s, s);
  g.fillStyle = "#7A4A24"; g.beginPath(); g.ellipse(0, 0, px * .55, px * .34, 0, 0, 7); g.fill(); g.strokeStyle = "#fff"; g.lineWidth = 1.2; g.beginPath(); g.moveTo(-px * .2, 0); g.lineTo(px * .2, 0); g.stroke(); g.restore();
}

/* ---------- the cues: the call, drawn after the play ---------- */
function arrow(g, pts, col, o) {
  o = o || {};
  g.save(); g.strokeStyle = col; g.fillStyle = col; g.lineWidth = o.w || 2.4; g.lineJoin = "round"; g.lineCap = "round"; if (o.dash) g.setLineDash(o.dash);
  g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let k = 1; k < pts.length; k++) g.lineTo(pts[k][0], pts[k][1]); g.stroke(); g.setLineDash([]);
  const n = pts.length, [x1, y1] = pts[n - 1];
  let k = n - 2; while (k > 0 && Math.hypot(pts[k][0] - x1, pts[k][1] - y1) < 3) k--;
  const [x0, y0] = pts[Math.max(0, k)], an = Math.atan2(y1 - y0, x1 - x0), L = o.head || 9;
  if (o.t) { g.beginPath(); g.moveTo(x1 + Math.cos(an + Math.PI / 2) * L * .8, y1 + Math.sin(an + Math.PI / 2) * L * .8); g.lineTo(x1 - Math.cos(an + Math.PI / 2) * L * .8, y1 - Math.sin(an + Math.PI / 2) * L * .8); g.lineWidth = (o.w || 2.4) + 1; g.stroke(); }
  else { g.beginPath(); g.moveTo(x1, y1); g.lineTo(x1 - Math.cos(an - .45) * L, y1 - Math.sin(an - .45) * L); g.lineTo(x1 - Math.cos(an + .45) * L, y1 - Math.sin(an + .45) * L); g.closePath(); g.fill(); }
  g.restore();
}

function drawCues(S, g, M, sc, alpha) {
  const call = sc.call; if (!call) return;
  const { px, X, Y } = M, dir = sc.dir, off = sc.off;
  const P = (u, v) => [X(sc.los + dir * u), Y(v)];
  g.save(); g.globalAlpha = alpha;
  // zones first, under everything
  call.plan.d.forEach((a, k) => {
    if ((a.act === "zone" || a.act === "deep") && a.at) {
      const [x, y] = P(a.at[0], a.at[1]), rad = (a.act === "deep" ? 7.5 : 5.2) * px;
      g.fillStyle = "rgba(255,255,255,.07)"; g.strokeStyle = "rgba(255,255,255,.35)"; g.lineWidth = 1.4; g.setLineDash([5, 4]); g.beginPath(); g.arc(x, y, rad, 0, 7); g.fill(); g.stroke(); g.setLineDash([]);
    }
  });
  // defense, in the colour of the club's trim, offense in white and yellow
  const RED = "#FF5A4F", WHITE = "#F4F7FA", YEL = "#FFD23F", ORG = "#FF9F43";
  call.plan.o.forEach((a, k) => {
    if (!a.pts.length) return;
    const st = call.at.o[k], pts = [P(st[0], st[1])].concat(a.pts.map(p => P(p[0], p[1])));
    if (a.act === "route" || a.act === "fake_route") arrow(g, pts, a.act === "route" ? YEL : "rgba(255,210,63,.55)", { dash: a.act === "fake_route" ? [5, 4] : null });
    else if (a.act === "carry") arrow(g, pts, "#FFFFFF", { w: 3.4, head: 11 });
    else if (a.act === "handoff" || a.act === "drop" || a.act === "rollout" || a.act === "fake" || a.act === "fake_carry") arrow(g, pts, a.act === "fake" || a.act === "fake_carry" ? "rgba(255,255,255,.5)" : WHITE, { dash: a.act === "fake" || a.act === "fake_carry" ? [4, 4] : null, w: 2 });
    else if (a.act === "pull") arrow(g, pts, ORG, { w: 2.6 });
    else arrow(g, pts, "rgba(244,247,250,.75)", { t: true, w: 2.2, head: 8 });                         // a block: a line ending in a bar
  });
  call.plan.d.forEach((a, k) => {
    if (!a.pts.length) return;
    const st = call.at.d[k], pts = [P(st[0], st[1])].concat(a.pts.map(p => P(p[0], p[1])));
    if (a.act === "rush" || a.act === "attack") arrow(g, pts, RED, { w: 2.4 });
    else if (a.act === "blitz") arrow(g, pts, RED, { w: 3, dash: [7, 3] });
    else if (a.act === "man") arrow(g, pts, "rgba(120,200,255,.8)", { w: 1.8, dash: [3, 3], head: 7 });
    else if (a.act === "zone" || a.act === "deep") { g.save(); g.strokeStyle = "rgba(255,255,255,.55)"; g.lineWidth = 1.6; g.setLineDash([2, 4]); g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); g.lineTo(pts[pts.length - 1][0], pts[pts.length - 1][1]); g.stroke(); g.restore(); }
    else arrow(g, pts, "rgba(255,255,255,.7)", { w: 2, head: 8 });
  });
  g.restore();
}

/* the green tick or red cross over the players who won or lost the matchup the log decided */
function drawMarks(S, g, M, sc, cur, alpha) {
  const call = sc.call; if (!call || !call.res) return;
  const { px } = M;
  const mark = (fig, v) => { if (!v) return; const a = cur.act[fig]; if (!a) return; const x = M.X(a.x) + px * .9, y = M.Y(a.y) - px * 1.1; g.save(); g.globalAlpha = alpha; g.fillStyle = v === "win" ? "#27C46B" : "#E5483D"; g.beginPath(); g.arc(x, y, px * .62, 0, 7); g.fill(); g.strokeStyle = "#fff"; g.lineWidth = 2; g.beginPath(); if (v === "win") { g.moveTo(x - px * .28, y); g.lineTo(x - px * .06, y + px * .24); g.lineTo(x + px * .3, y - px * .22); } else { g.moveTo(x - px * .22, y - px * .22); g.lineTo(x + px * .22, y + px * .22); g.moveTo(x + px * .22, y - px * .22); g.lineTo(x - px * .22, y + px * .22); } g.stroke(); g.restore(); };
  call.res.o.forEach((v, k) => mark(sc.off * 11 + k, v));
  call.res.d.forEach((v, k) => mark((1 - sc.off) * 11 + k, v));
}

function drawTags(S, g, M, cur) {
  if (!cur.ev) return; const { px } = M;
  g.font = `700 ${Math.round(Math.max(11, px * 1.05))}px ${FONT}`; g.textAlign = "center"; g.textBaseline = "alphabetic";
  cur.ev.forEach(e => {
    if (e.k !== "tag" || cur.t < e.t0 || cur.t > e.t1) return; const a = cur.act[e.a]; if (!a) return;
    const x = M.X(a.x), y = M.Y(a.y) - px * 1.55, w = g.measureText(e.text).width + 10;
    g.fillStyle = "rgba(5,7,11,.82)"; g.fillRect(x - w / 2, y - px * 1.0, w, px * 1.25); g.fillStyle = "#fff"; g.fillText(e.text, x, y - px * .12);
  });
}

function draw(S, g, cur) {
  const M = map(S);
  const off = S.scene ? S.scene.off : S.sit ? S.sit.off : 0;
  g.setTransform(S.dpr, 0, 0, S.dpr, 0, 0);
  drawField(S, g, M);
  drawLines(S, g, M);
  // the cues are up for the whole play, from the lineup to the whistle, and stay until the next play is being lined up; only the marks for who won or lost wait for the end of the play
  let cueSc = null, alpha = 0, mAlpha = 0;
  if (S.scene) { const sc = S.scene, tA = sc.tAct == null ? sc.dur - 1 : sc.tAct; cueSc = sc; alpha = clamp((S.t + (S.L || 0) + .05) / .6, 0, 1); mAlpha = clamp((S.t - tA - .35) / .5, 0, 1); }
  else if (S.cueScene && !S.tw) { cueSc = S.cueScene; alpha = 1; mAlpha = 1; }
  if (cueSc) { drawCues(S, g, M, cueSc, alpha * .92); if (S.oncue && S.cueSeen !== cueSc) { S.cueSeen = cueSc; S.oncue(cueSc.call); } }
  else if (S.cueSeen) { S.cueSeen = null; if (S.oncue) S.oncue(null); }
  // dots, far side first is not needed on a flat board; the ball carrier is ringed
  const carrier = cur.ball && cur.ball.held ? cur.ball.who : -1;
  (cur.act || []).forEach((a, i) => drawDot(S, g, M, a, i, off, false, i === carrier));
  if (cur.ball) drawBall(S, g, M, cur.ball);
  if (cueSc && mAlpha > 0) drawMarks(S, g, M, cueSc, cur, mAlpha);
  drawTags(S, g, M, cur);
  if (cur.ev) S.drawBanners(g, cur);
}

root.DFLChalk = { layout, leave, draw };
if (typeof module !== "undefined" && module.exports) module.exports = root.DFLChalk;
})(typeof window !== "undefined" ? window : globalThis);
