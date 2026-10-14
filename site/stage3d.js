/* The 3D view of the DFL stage (an option next to the 2D field).

   It draws nothing of its own accord: Stage (site/stage.js) keeps the timeline, the camera focus and the lines, and hands every frame to Renderer3D as a list of 22 figures
   and the ball (the very same numbers the 2D field draws). Only the drawing differs. The banners and name tags stay on the 2D canvas laid over the picture.

   Three.js is not part of the page: it is fetched from a CDN the first time somebody switches the 3D view on (load()), and when that fails, or the browser has no WebGL,
   the stage stays 2D and says so. Units are the stage's (yards): world x along the field, world y across it, z up; in three.js x stays x, y becomes depth (z) and z becomes up (y). */
(function (root) {
"use strict";
const THREE_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js";
const FW = 53.3, MID = FW / 2;
const K = 1.45;                                                        // a figure is drawn this much bigger than life, so that it can be seen from the stands
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
let loading = null;

/* load(): a promise of the THREE namespace; the page may name another address with window.DFL_THREE_URL (the checks serve their own copy) */
function load() {
  if (root.THREE) return Promise.resolve(root.THREE);
  if (!loading) loading = new Promise((res, rej) => {
    const s = document.createElement("script");
    s.src = root.DFL_THREE_URL || THREE_URL; s.async = true;
    s.onload = () => root.THREE ? res(root.THREE) : (loading = null, rej(new Error("three.js did not start")));
    s.onerror = () => { loading = null; s.remove(); rej(new Error("three.js did not load")); };
    document.head.appendChild(s);
  });
  return loading;
}
function webgl() { try { const c = document.createElement("canvas"); return !!(c.getContext("webgl2") || c.getContext("webgl")); } catch (e) { return false; } }

/* the angles of a pose, in the same terms as the 2D sprite (stage.js drawPlayer): lean of the body, thigh and knee of both legs, shoulder and elbow of both arms, hip height */
function poseOf(pose, ph, clk) {
  const sw = Math.sin(ph);
  const p = { lean: 0, th1: .08, th2: -.1, fl1: .1, fl2: .1, hy: 1.06, a1: .15, a2: -.1, e1: .35, e2: .35, bob: 0, down: false };
  switch (pose) {
    case "run": case "back": p.th1 = .95 * sw; p.th2 = -.95 * sw; p.fl1 = .3 + .75 * (1 + Math.sin(ph - 1.3)) / 2; p.fl2 = .3 + .75 * (1 + Math.sin(ph + Math.PI - 1.3)) / 2; p.lean = .22; p.a1 = -.95 * sw; p.a2 = .95 * sw; p.e1 = p.e2 = 1.25; p.bob = Math.abs(sw) * .09; break;
    case "stance": p.lean = .85; p.th1 = .75; p.th2 = -.35; p.fl1 = 1.0; p.fl2 = .4; p.hy = .82; p.a1 = 1.5; p.e1 = .1; p.a2 = -.5; p.e2 = .6; break;
    case "kneel": p.lean = .35; p.th1 = 1.2; p.th2 = -.3; p.fl1 = 1.5; p.fl2 = 1.2; p.hy = .62; p.a1 = 1.0; p.e1 = .6; p.a2 = .8; p.e2 = .6; break;
    case "block": p.lean = .38; p.th1 = .55; p.th2 = -.4; p.fl1 = .55; p.fl2 = .35; p.hy = .98; p.a1 = 1.35; p.e1 = .8; p.a2 = 1.2; p.e2 = .9; break;
    case "tackle": p.lean = .95; p.th1 = .9; p.th2 = -.7; p.fl1 = .5; p.fl2 = .6; p.hy = .9; p.a1 = 1.55; p.e1 = .15; p.a2 = 1.3; p.e2 = .2; break;
    case "throw": p.lean = -.08; p.th1 = .35; p.th2 = -.35; p.fl1 = .25; p.fl2 = .15; p.a1 = -2.5; p.e1 = .9; p.a2 = 1.0; p.e2 = .3; break;
    case "catch": p.lean = -.05; p.th1 = .15; p.th2 = -.15; p.a1 = -2.85; p.e1 = .1; p.a2 = -2.55; p.e2 = .15; p.bob = Math.abs(Math.sin(clk * 9)) * .05; break;
    case "cele": p.th1 = .2; p.th2 = -.2; p.a1 = -3.0; p.e1 = .1; p.a2 = -2.7; p.e2 = .1; p.bob = Math.abs(Math.sin(clk * 8)) * .35; break;
    case "kick": p.lean = -.22; p.th1 = 1.55; p.th2 = -.2; p.fl1 = .1; p.fl2 = .15; p.a1 = -.9; p.e1 = .4; p.a2 = 1.0; p.e2 = .4; break;
    case "down": p.down = true; p.lean = .1; p.th1 = .3; p.th2 = -.2; p.fl1 = .5; p.fl2 = .3; p.a1 = 1.2; p.e1 = .5; p.a2 = .3; p.e2 = .3; break;
  }
  return p;
}

function Renderer3D(T, o) {
  this.T = T; this.o = o; this.dead = false; this.view = "side"; this.t0 = 0;
  const r = this.renderer = new T.WebGLRenderer({ antialias: true, alpha: false, powerPreference: "high-performance" });
  r.setClearColor(0x05070B, 1);
  this.el = r.domElement; this.el.setAttribute("aria-hidden", "true");
  this.scene = new T.Scene(); this.scene.fog = new T.Fog(0x05070B, 90, 230);
  this.cam = new T.PerspectiveCamera(40, 3, .5, 400);
  this.cp = new T.Vector3(60, 20, 80); this.cl = new T.Vector3(60, 0, 20); this.fresh = true;
  this.W = 600; this.H = 200;
  this.scene.add(new T.HemisphereLight(0xE4ECFF, 0x1D3A24, .82));
  const sun = new T.DirectionalLight(0xFFF1D0, .62); sun.position.set(-30, 60, 40); this.scene.add(sun);
  this.mats = {};
  this.buildField(); this.buildSurround(); this.buildPosts();
  // the two lines
  const line = (col, w, op) => { const m = new T.Mesh(new T.PlaneGeometry(w, FW), new T.MeshBasicMaterial({ color: col, transparent: true, opacity: op, depthWrite: false })); m.rotation.x = -Math.PI / 2; m.position.set(0, .05, MID); m.visible = false; this.scene.add(m); return m; };
  this.los = [line(0x3D8BFF, .42, .95), line(0x3D8BFF, 1.4, .22)]; this.fd = [line(0xFFD21F, .42, .95), line(0xFFD21F, 1.4, .22)];
  // twenty-two figures, the ball, and the flags
  this.fig = []; for (let i = 0; i < 22; i++) { const f = this.makeFigure(i < 11 ? 0 : 1, i); this.scene.add(f.root); this.scene.add(f.shadow); this.fig.push(f); }
  this.makeBall();
  this.flags = []; for (let i = 0; i < 4; i++) { const m = new T.Mesh(new T.PlaneGeometry(.9, .6), new T.MeshLambertMaterial({ color: 0xFFD21F, side: T.DoubleSide })); m.visible = false; this.scene.add(m); this.flags.push(m); }
}
Renderer3D.prototype = {
  mat(col, key) { const k = key || col; return this.mats[k] || (this.mats[k] = new this.T.MeshLambertMaterial({ color: new this.T.Color(col) })); },
  resize(w, h, dpr) { this.W = w; this.H = h; this.renderer.setPixelRatio(dpr); this.renderer.setSize(w, h, false); this.cam.aspect = w / h; this.cam.updateProjectionMatrix(); },

  /* ---- the field: one texture laid on the ground, painted like the 2D field but seen from above ---- */
  buildField() {
    const T = this.T, o = this.o;
    if (this.fieldMesh) { this.scene.remove(this.fieldMesh); this.fieldMesh.material.map.dispose(); this.fieldMesh.material.dispose(); this.fieldMesh.geometry.dispose(); }
    const PPY = 16, X0 = -6, Z0 = -8, WX = 132, WZ = 70, cv = document.createElement("canvas"); cv.width = WX * PPY; cv.height = WZ * PPY;
    const g = cv.getContext("2d"), px = x => (x - X0) * PPY, pz = z => (z - Z0) * PPY;
    g.fillStyle = "#124A2A"; g.fillRect(0, 0, cv.width, cv.height);
    for (let i = 0; i < 24; i++) { g.fillStyle = i % 2 ? "#207745" : "#1B6B3C"; g.fillRect(px(10 + i * 5), pz(0), 5 * PPY, FW * PPY); }
    [[0, o.club[1]], [110, o.club[0]]].forEach(([x0, c]) => {
      g.fillStyle = c.colors[0]; g.fillRect(px(x0), pz(0), 10 * PPY, FW * PPY); g.fillStyle = "rgba(0,0,0,.25)"; g.fillRect(px(x0), pz(0), 10 * PPY, FW * PPY);
      g.save(); g.translate(px(x0 + 5), pz(MID)); g.rotate(x0 ? Math.PI / 2 : -Math.PI / 2); g.fillStyle = o.inkOn(c.colors[0]); g.globalAlpha = .92;
      let fz = 7.6 * PPY; g.font = `italic 800 ${fz}px ${o.font}`; const w = g.measureText(c.abbr).width; if (w > FW * PPY * .8) { fz *= FW * PPY * .8 / w; g.font = `italic 800 ${fz}px ${o.font}`; }
      g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(c.abbr, 0, 0); g.restore();
    });
    g.strokeStyle = "#fff"; g.fillStyle = "#fff";
    for (let i = 0; i <= 20; i++) { const x = 10 + i * 5; g.globalAlpha = i === 0 || i === 20 ? 1 : i % 2 ? .6 : .9; g.lineWidth = i === 0 || i === 20 ? .36 * PPY : .2 * PPY; g.beginPath(); g.moveTo(px(x), pz(0)); g.lineTo(px(x), pz(FW)); g.stroke(); }
    g.globalAlpha = 1; g.lineWidth = .36 * PPY; for (const z of [0, FW]) { g.beginPath(); g.moveTo(px(0), pz(z)); g.lineTo(px(120), pz(z)); g.stroke(); }
    g.beginPath(); g.moveTo(px(0), pz(0)); g.lineTo(px(0), pz(FW)); g.moveTo(px(120), pz(0)); g.lineTo(px(120), pz(FW)); g.stroke();
    g.globalAlpha = .8; g.lineWidth = .1 * PPY;                         // a mark at every yard along the hashes and the sidelines
    for (let x = 11; x < 110; x++) for (const z of [0, 23.4, 29.9, FW]) { const d = z === 0 ? 1 : z === FW ? -1 : 0, len = .6; g.beginPath(); if (d) { g.moveTo(px(x), pz(z)); g.lineTo(px(x), pz(z + d * len * 2)); } else { g.moveTo(px(x), pz(z - len / 2)); g.lineTo(px(x), pz(z + len / 2)); } g.stroke(); }
    g.globalAlpha = .72; g.textAlign = "center"; g.textBaseline = "middle"; g.font = `italic 800 ${2.9 * PPY}px ${o.font}`;
    for (let i = 1; i < 10; i++) {
      const n = String(i <= 5 ? i * 10 : (10 - i) * 10), x = 10 + i * 10;
      g.save(); g.translate(px(x), pz(FW - 7)); g.fillText(n, 0, 0); g.restore();                           // the near row reads from the near sideline
      g.save(); g.translate(px(x), pz(7)); g.rotate(Math.PI); g.fillText(n, 0, 0); g.restore();             // the far row reads from the far one
    }
    g.globalAlpha = .16; g.save(); g.translate(px(60), pz(MID)); g.rotate(Math.PI / 4); g.fillRect(-3.4 * PPY, -3.4 * PPY, 6.8 * PPY, 6.8 * PPY); g.restore();
    const tex = new T.CanvasTexture(cv); tex.anisotropy = Math.min(8, this.renderer.capabilities.getMaxAnisotropy());
    const m = new T.Mesh(new T.PlaneGeometry(WX, WZ), new T.MeshBasicMaterial({ map: tex }));
    m.rotation.x = -Math.PI / 2; m.position.set(X0 + WX / 2, 0, Z0 + WZ / 2); this.scene.add(m); this.fieldMesh = m;
  },
  /* the stands, the boards and the dark ground around the field */
  buildSurround() {
    const T = this.T, o = this.o, rnd = o.rng(77);
    const ground = new T.Mesh(new T.PlaneGeometry(500, 500), new T.MeshBasicMaterial({ color: 0x070B10 })); ground.rotation.x = -Math.PI / 2; ground.position.set(60, -.06, MID); this.scene.add(ground);
    const cv = document.createElement("canvas"); cv.width = 1024; cv.height = 256; const g = cv.getContext("2d");
    g.fillStyle = "#141B27"; g.fillRect(0, 0, 1024, 256);
    for (let i = 0; i < 5200; i++) { g.fillStyle = ["#2A3550", "#3A2F3F", "#1E2A3E", "#46405A", "#5A4A3A", "#2B3B4A"][(rnd() * 6) | 0]; g.globalAlpha = .55 + rnd() * .4; g.fillRect(rnd() * 1024, rnd() * 256, 5, 6); }
    const tex = new T.CanvasTexture(cv); tex.wrapS = tex.wrapT = T.RepeatWrapping;
    const stand = (w, rep, x, z, ry) => {
      const t = tex.clone(); t.needsUpdate = true; t.repeat.set(rep, 1);
      const m = new T.Mesh(new T.PlaneGeometry(w, 40), new T.MeshBasicMaterial({ map: t, color: 0x6C7488 }));
      m.position.set(x, 15, z); m.rotation.set(0, ry, 0); m.rotateX(-Math.PI / 4.3); this.scene.add(m);
    };
    stand(200, 2, 60, -22, 0); stand(200, 2, 60, FW + 22, Math.PI); stand(130, 1.3, -22, MID, Math.PI / 2); stand(130, 1.3, 142, MID, -Math.PI / 2);
    // the boards along both sidelines
    const bc = document.createElement("canvas"); bc.width = 1024; bc.height = 64; const b = bc.getContext("2d");
    for (let i = 0; i < 16; i++) { const c = i % 3 === 0 ? o.club[1].colors[0] : i % 3 === 1 ? o.club[0].colors[0] : "#1B2330"; b.fillStyle = c; b.fillRect(i * 64 + 2, 4, 60, 56); b.fillStyle = o.inkOn(c); b.font = `italic 800 34px ${o.font}`; b.textAlign = "center"; b.textBaseline = "middle"; b.fillText(i % 3 === 2 ? "DFL" : (i % 3 === 0 ? o.abbr[1] : o.abbr[0]), i * 64 + 32, 34); }
    const bt = new T.CanvasTexture(bc); bt.wrapS = T.RepeatWrapping; bt.repeat.set(4, 1);
    const bm = new T.MeshLambertMaterial({ map: bt });
    for (const z of [-3.2, FW + 3.2]) { const m = new T.Mesh(new T.BoxGeometry(124, 1.6, .5), bm); m.position.set(60, .8, z); this.scene.add(m); }
  },
  /* the goal posts, at the back of both end zones */
  buildPosts() {
    const T = this.T, yel = this.mat(0xFFD21F, "post"), bar = 3.33, half = 3.08, top = 10;
    const cyl = (r, h, x, y, z, rx, rz) => { const m = new T.Mesh(new T.CylinderGeometry(r, r, h, 6), yel); m.position.set(x, y, z); if (rx) m.rotation.x = rx; if (rz) m.rotation.z = rz; this.scene.add(m); };
    for (const x of [0, 120]) {
      cyl(.2, bar, x, bar / 2, MID);                                                    // the post
      cyl(.14, half * 2, x, bar, MID, Math.PI / 2);                                     // the crossbar
      cyl(.12, top - bar, x, (top + bar) / 2, MID - half); cyl(.12, top - bar, x, (top + bar) / 2, MID + half);
    }
  },

  /* ---- a figure: low-poly, jointed like the 2D sprite (hips, torso, head, two arms of two parts, two legs of two parts) ---- */
  makeFigure(team, idx) {
    const T = this.T, o = this.o, kit = o.kit[team], skin = o.skins[idx % o.skins.length];
    const jersey = this.mat(kit.jersey, "j" + team), pads = this.mat(o.shade(kit.jersey, .82), "p" + team), pants = this.mat(kit.pants, "n" + team), helmet = this.mat(kit.helmet, "h" + team), trim = this.mat(kit.trim, "t" + team);
    const sk = this.mat(skin, "s" + skin), shoe = this.mat(0x0B0D10, "shoe"), mask = this.mat(0xD8DDE3, "mask");
    const box = (w, h, d, m, x, y, z, parent) => { const g = new T.BoxGeometry(w, h, d); const me = new T.Mesh(g, m); me.position.set(x, y, z); parent.add(me); return me; };
    const hang = (w, h, d, m, parent) => { const g = new T.BoxGeometry(w, h, d); g.translate(0, -h / 2, 0); const me = new T.Mesh(g, m); parent.add(me); return me; };
    const root = new T.Group(), tilt = new T.Group(), pelvis = new T.Group(), torso = new T.Group();
    root.scale.set(K, K, K); root.add(tilt); tilt.add(pelvis); pelvis.add(torso);
    box(.3, .16, .5, pants, 0, 0, 0, pelvis);
    box(.36, .58, .6, jersey, 0, .3, 0, torso); box(.5, .24, .82, pads, 0, .74, 0, torso); box(.37, .06, .62, trim, 0, .1, 0, torso);
    box(.12, .12, .14, sk, 0, .92, 0, torso);
    const head = new T.Mesh(new T.SphereGeometry(.3, 10, 8), helmet); head.position.set(.04, 1.22 - 0, 0); head.scale.set(1.08, .98, 1); torso.add(head);
    box(.08, .22, .34, mask, .3, 1.14, 0, torso); box(.3, .05, .06, mask, .2, 1.06, 0, torso);
    box(.5, .05, .08, jersey, .04, 1.5, 0, torso);                                     // the stripe over the helmet
    const arms = [], legs = [];
    for (const s of [1, -1]) {
      const sh = new T.Group(); sh.position.set(0, .8, s * .46); torso.add(sh); hang(.17, .46, .17, jersey, sh);
      const el = new T.Group(); el.position.set(0, -.46, 0); sh.add(el); hang(.13, .42, .13, sk, el);
      const hand = new T.Mesh(new T.SphereGeometry(.09, 6, 5), sk); hand.position.set(0, -.44, 0); el.add(hand);
      arms.push({ sh, el });
      const hp = new T.Group(); hp.position.set(0, 0, s * .15); pelvis.add(hp); hang(.22, .56, .2, pants, hp);
      const kn = new T.Group(); kn.position.set(0, -.56, 0); hp.add(kn); hang(.18, .56, .17, pants, kn);
      box(.36, .1, .2, shoe, .08, -.58, 0, kn);
      legs.push({ hp, kn });
    }
    const shadow = new T.Mesh(new T.CircleGeometry(.75, 14), new T.MeshBasicMaterial({ color: 0, transparent: true, opacity: .34, depthWrite: false }));
    shadow.rotation.x = -Math.PI / 2; shadow.position.y = .03;
    return { root, tilt, pelvis, torso, arms, legs, shadow, yaw: idx < 11 ? 0 : Math.PI, px: null, pz: null, idx, team };
  },
  makeBall() {
    const T = this.T;
    const grp = new T.Group(), g = new T.SphereGeometry(.5, 12, 8); g.scale(1, .56, .56);
    const body = new T.Mesh(g, this.mat(0x9A5F2B, "ball")); grp.add(body);
    const lace = new T.Mesh(new T.BoxGeometry(.4, .03, .08), this.mat(0xFFFFFF, "lace")); lace.position.set(0, .285, 0); body.add(lace);
    grp.scale.set(.62, .62, .62); this.ballG = grp; this.ballBody = body; this.scene.add(grp);
    this.ballShadow = new T.Mesh(new T.CircleGeometry(.4, 10), new T.MeshBasicMaterial({ color: 0, transparent: true, opacity: .3, depthWrite: false })); this.ballShadow.rotation.x = -Math.PI / 2; this.ballShadow.position.y = .03; this.scene.add(this.ballShadow);
    this.ballDir = new T.Vector3(1, 0, 0); this.pb = null;
  },

  /* ---- one frame ---- */
  /* v: { act, ball, ev, t } (the stage's current()), cam (the focus along the field), dir (the way the offense goes), clock, los, fd */
  render(v, s) {
    if (this.dead) return;
    const now = performance.now(), dt = this.t0 ? Math.min(.1, (now - this.t0) / 1000) : .016; this.t0 = now;
    const act = v.act || [];
    for (let i = 0; i < 22; i++) { const a = act[i], f = this.fig[i]; if (!a) { f.root.visible = false; f.shadow.visible = false; continue; } this.pose(f, a, s.clock, dt); }
    this.placeBall(v.ball, act, dt);
    for (const [pair, x] of [[this.los, s.los], [this.fd, s.fd]]) for (const m of pair) { m.visible = x != null; if (x != null) m.position.x = x; }
    // flags
    let nf = 0; if (v.ev) for (const e of v.ev) if (e.k === "flag" && v.t >= e.t0 && nf < this.flags.length) { const m = this.flags[nf++], age = v.t - e.t0; m.visible = true; m.position.set(e.x, .35 + Math.max(0, 3 * (1 - Math.min(1, age / .5))), e.y); m.rotation.set(-.4, age < .5 ? age * 12 : Math.sin(s.clock * 6) * .3, 0); }
    for (; nf < this.flags.length; nf++) this.flags[nf].visible = false;
    this.camera(s, dt);
    this.renderer.render(this.scene, this.cam);
  },
  pose(f, a, clk, dt) {
    const T = this.T, p = poseOf(a.pose || "stand", (a.x + a.y * .6) * 3.7, clk);
    const root = f.root; root.visible = true; f.shadow.visible = true;
    // the way the figure looks: along its run while it runs, otherwise the way the log says it faces
    let want = a.face >= 0 ? 0 : Math.PI;
    if (f.px != null && dt > .002) {
      const dx = a.x - f.px, dz = a.y - f.pz, sp = Math.hypot(dx, dz) / dt;
      if ((a.pose === "run") && sp > 1.2 && sp < 40) want = Math.atan2(-dz, dx);                // three.js: a heading (dx, dz) is a rotation of -atan2(dz, dx) about the vertical
      else if (a.pose === "back") want = a.face >= 0 ? 0 : Math.PI;
    }
    f.px = a.x; f.pz = a.y;
    if (a.pose === "run" || a.pose === "back") { /* turn smoothly */ }
    let d = want - f.yaw; d = Math.atan2(Math.sin(d), Math.cos(d)); f.yaw += clamp(d, -dt * 14, dt * 14); if (!(dt > .002) && Math.abs(d) > 0) f.yaw = want;
    root.position.set(a.x, 0, a.y); root.rotation.y = f.yaw;
    f.shadow.position.set(a.x, .03, a.y); f.shadow.scale.set(p.down ? 2.0 : 1, 1, p.down ? 1.2 : 1);
    f.shadow.rotation.z = 0;
    f.tilt.rotation.z = p.down ? -1.5 : 0; f.tilt.position.set(p.down ? -.7 : 0, p.down ? .2 : 0, 0);
    f.pelvis.position.y = p.hy + p.bob;
    f.torso.rotation.z = -p.lean;
    f.legs[0].hp.rotation.z = p.th1; f.legs[0].kn.rotation.z = -p.fl1; f.legs[1].hp.rotation.z = p.th2; f.legs[1].kn.rotation.z = -p.fl2;
    f.arms[0].sh.rotation.z = p.a1; f.arms[0].el.rotation.z = p.e1; f.arms[1].sh.rotation.z = p.a2; f.arms[1].el.rotation.z = p.e2;
  },
  placeBall(b, act, dt) {
    const G = this.ballG; if (!b) { G.visible = false; return; }
    G.visible = true;
    const y = b.z + .26;
    G.position.set(b.x, y, b.y);
    if (b.flying && this.pb) {
      const dx = b.x - this.pb[0], dy = b.y - this.pb[2], dz = y - this.pb[1];
      if (Math.hypot(dx, dy, dz) > .01) { this.ballDir.set(dx, dz, dy).normalize(); }
    } else if (b.held && act[b.who]) { const h = act[b.who]; this.ballDir.set(h.face >= 0 ? 1 : -1, 0, 0); }
    G.quaternion.setFromUnitVectors(new this.T.Vector3(1, 0, 0), this.ballDir);
    this.ballBody.rotation.x = b.flying ? b.spin : 0;
    this.pb = [b.x, y, b.y];
    this.ballShadow.visible = b.z > .15 || !b.held; this.ballShadow.position.set(b.x, .03, b.y); const sc = clamp(1 - b.z / 14, .35, 1); this.ballShadow.scale.set(sc, sc, sc);
  },
  camera(s, dt) {
    const cx = s.cam, dir = s.dir || 1, p = this.cam.position, T = this.T;
    let px, py, pz, lx, ly, lz, fov;
    if (this.view === "behind") { px = cx - dir * 26; py = 12; pz = MID + 1; lx = cx + dir * 13; ly = .5; lz = MID; fov = 46; }
    else { px = cx; py = 25; pz = FW + 36; lx = cx; ly = 0; lz = 23; fov = 25; }
    const k = this.fresh ? 1 : 1 - Math.exp(-dt * 3.2);
    this.cp.x += (px - this.cp.x) * k; this.cp.y += (py - this.cp.y) * k; this.cp.z += (pz - this.cp.z) * k;
    this.cl.x += (lx - this.cl.x) * k; this.cl.y += (ly - this.cl.y) * k; this.cl.z += (lz - this.cl.z) * k;
    this.fresh = false;
    this.cam.position.copy(this.cp); this.cam.lookAt(this.cl);
    if (Math.abs(this.cam.fov - fov) > .05) { this.cam.fov += (fov - this.cam.fov) * k; this.cam.updateProjectionMatrix(); }
    this.cam.updateMatrixWorld();
  },
  /* where a point of the field shows on the picture, in CSS pixels */
  project(x, y, z) {
    const v = new this.T.Vector3(x, z, y).project(this.cam);
    return { x: (v.x * .5 + .5) * this.W, y: (-v.y * .5 + .5) * this.H, ok: v.z < 1 };
  },
  setView(v) { this.view = v === "behind" ? "behind" : "side"; this.fresh = true; },
  dispose() {
    this.dead = true;
    try { this.scene.traverse(n => { if (n.geometry) n.geometry.dispose(); }); for (const k in this.mats) this.mats[k].dispose(); this.renderer.dispose(); if (this.renderer.forceContextLoss) this.renderer.forceContextLoss(); } catch (e) {}
    if (this.el.parentNode) this.el.parentNode.removeChild(this.el);
  },
};

root.DFLStage3D = { load, webgl, Renderer3D, poseOf, THREE_URL, K };
if (typeof module !== "undefined" && module.exports) module.exports = root.DFLStage3D;
})(typeof window !== "undefined" ? window : globalThis);
