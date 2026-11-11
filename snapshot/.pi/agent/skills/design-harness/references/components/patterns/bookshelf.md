---
title: Library shelf
slug: bookshelf
status: published
description: "Library, \"Spines\": books standing spine-out on shelves filled to the column, drawn by three.js under the DOM; hover tips a spine, a click pulls the book out to its cover."
chips:
  - Pattern
  - Library
  - WebGL
  - Grid
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:08:52Z
---

The Library section is one grid page ("Books"), with no sub-nav (`html.is-solo`). The concept is by Wren ([wren](../../intelligence/agents/wren.md)).

- **Shelves.** The books stand spine-out, in order, each shelf filled to the column's width and the next starting below. On a phone it is one shelf that scrolls sideways (`.sp-row`, natively, which also steps the sound's drag). The DOM lays out every slot (thickness, height, lean) and keeps focus and hits. One three.js canvas under the page (`canvas.grid-gl`, `html.sp-gl`) draws the books on those slots. See [spine](../components/spine.md).
- **Interaction.** Hover or focus tips a spine out: the top comes toward you a little, on a spring, and a neighbour leans into a gap (30% at Neat). A click pulls the book: out of the shelf toward you, then across in an arc that stays in front of the shelf, turning to its cover and landing flat under its slot, kept inside the column with room for the text. Its details appear beside it as plain text once it has landed (`fillDetails`, no modal; see [book card](../components/cover.md)). The shelves below make room. Clicking it again, clicking its cover or anywhere away, or pressing Escape returns it.
- **Live params.** `--fnd-spine-order` .4 (Neat → Leaning), `--fnd-spine-depth` .45 (Flat → Deep: how close the eye stands, how far a spine tips), `--fnd-spine-tone` .85 (Ink → Colour), and the site's `--fnd-energy` (the pull's speed and the spring in the tip).
- **Theme.** The spine colours stay the covers'. The paper they mix with and the type follow the theme. The page edges are `#efebe3` and `#e6e1d7`.
- **Static shelf.** Under reduced motion, or without WebGL, the same layout is drawn as DOM spines, with type in ink or paper to suit. Switching reduced motion on mid-visit ends the books and leaves the static shelf (with its book out, if one is).
- **Live content.** "Books", 34 books on two shelves at 1440 (2026-11-11).

Source: `site/js/grids/spines.js`, lines 147 to 532

```js
  // ---------- the DOM: header, shelf, reader ----------
  const wrap = document.createElement('div'); wrap.className = 'sp';
  wrap.innerHTML = `<header class="sp-head"><h2 class="sp-title">${title} <span class="sp-count">${recs.length}</span></h2>
    <p class="sp-read" aria-hidden="true"><span class="sp-read-title"></span><span class="sp-read-by"></span></p></header>
    <div class="sp-case" role="group" aria-label="${title}, spine out">
      <div class="sp-gap"><div class="sp-gap-in"><section class="sp-reader" id="sp-reader" aria-label="Book details" hidden>
        <button type="button" class="sp-cover" aria-label="Put the book back"><img alt=""></button>
        <div class="sp-text"><div class="sp-details"></div></div>
      </section></div></div>
    </div>`;
  const caseEl = wrap.querySelector('.sp-case'), gap = wrap.querySelector('.sp-gap'), read = wrap.querySelector('.sp-read');
  // the shelves: each a row (it scrolls on a phone) holding an ordered list; layoutShelves fills them
  const rowEls = [];
  function rowEl(k) {
    while (rowEls.length <= k) {
      const row = document.createElement('div'); row.className = 'sp-row';
      const ol = document.createElement('ol'); ol.className = 'sp-shelf'; row.append(ol);
      rowEls.push(row);
    }
    if (!rowEls[k].isConnected) k ? rowEls[k - 1].after(rowEls[k]) : caseEl.prepend(rowEls[k]);
    return rowEls[k];
  }
  const shelf = rowEl(0).firstChild;
  const reader = wrap.querySelector('.sp-reader'), readerImg = reader.querySelector('img'), readerDetails = reader.querySelector('.sp-details');
  root.classList.add('sp-pending');
  life.later(() => root.classList.remove('sp-pending', 'sp-gl', 'sp-static'));
  col.replaceChildren(wrap);

  // the books' sizes come from their covers, so wait for the covers (and the spine type)
  const [imgs] = await Promise.all([
    Promise.all(recs.map(r => loadImage(r.images[0]))),
    Promise.all([document.fonts.load(`13px ${UI}`), document.fonts.load(`9px ${MONO}`)]).catch(() => {}),
  ]);
  if (life.dead) return null;
  readScale();

  const books = recs.map((rec, i) => {
    const img = imgs[i];
    const aspect = img ? img.naturalWidth / img.naturalHeight : 0.68;
    const f = clamp01((aspect - 0.6) / 0.25);
    const H = Math.round(236 + 82 * (0.5 * f + 0.5 * hash(rec.slug + 'h')));
    const T = Math.round(20 + 24 * hash(rec.slug + 't'));
    const D = Math.round(H * aspect);
    const colour = img ? sampleColour(img) : [0.86, 0.86, 0.86];
    const [dir, a] = LEANS[i] || [1, 0];
    const year = rec.chips[0] || '';
    const li = document.createElement('li'); li.className = 'sp-book' + (a ? (dir < 0 ? ' lean-r' : ' lean-l') : '');
    li.style.cssText = `--bt:${T};--bh:${H};--a:${a};--j:${hash(rec.slug + 'j').toFixed(3)};--c:rgb(${colour.map(v => Math.round(v * 255)).join(',')})`;
    const b = document.createElement('button'); b.type = 'button'; b.className = 'sp-btn';
    b.setAttribute('aria-label', `${rec.title}${rec.desc ? ', ' + rec.desc : ''}${year ? ', ' + year : ''}`);
    b.setAttribute('aria-expanded', 'false'); b.setAttribute('aria-controls', 'sp-reader');
    const face = document.createElement('span'); face.className = 'sp-face'; face.setAttribute('aria-hidden', 'true');
    const spine = layoutSpine(rec, T, H);
    face.innerHTML = '<span class="sf-title"></span><span class="sf-by"></span><span class="sf-year"></span>';
    face.querySelector('.sf-title').textContent = spine.title.join(' ');
    face.querySelector('.sf-by').textContent = spine.by;
    face.querySelector('.sf-year').textContent = year;
    b.append(face); li.append(b); shelf.append(li);
    return { i, rec, li, b, img, aspect, T, H, D, colour, dir, a, a0: a, j: hash(rec.slug + 'j'), row: 0, spine, year,
      tip: 0, tipV: 0, q: 0, qV: 0, target: 0, dyn: 0, dynV: 0, land: null, group: null };
  });

  // ---------- the shelves: fill each to the column's width, then start the next below ----------
  const narrow = matchMedia('(max-width: 899px)');
  let shelfKey = '', caseW = 0;
  function layoutShelves() {
    const order = P['spine-order'], avail = narrow.matches ? Infinity : caseEl.clientWidth - 1;
    const slot = (bk) => S * (bk.T + bk.H * bk.a0 * order), sp = (bk) => S * (1 + bk.j * order * 5);
    const width = (row) => row.reduce((w, bk, n) => w + (n ? sp(bk) : 0) + slot(bk), 0);
    // how many shelves filling them takes
    let rows = [[]], w = 0;
    for (const bk of books) {
      let row = rows[rows.length - 1];
      if (row.length && w + sp(bk) + slot(bk) > avail) { rows.push(row = []); w = 0; }
      w += (row.length ? sp(bk) : 0) + slot(bk); row.push(bk);
    }
    // then the books split evenly over that many, in order (one more shelf if an even split won't fit)
    for (let n = rows.length; n > 1 && n <= books.length; n++) {
      const even = []; let at = 0;
      for (let k = 0; k < n; k++) { const c = Math.floor(books.length / n) + (k < books.length % n ? 1 : 0); even.push(books.slice(at, at += c)); }
      if (even.every(r => width(r) <= avail)) { rows = even; break; }
    }
    // a book leans on a neighbour, so none leans off the end of a shelf
    rows.forEach((row, k) => row.forEach((bk, n) => {
      bk.row = k;
      const lone = bk.a0 && (bk.dir > 0 ? n === 0 : n === row.length - 1);
      bk.a = lone ? 0 : bk.a0;
    }));
    const key = rows.map(r => r.length).join() + '|' + books.map(b => b.a ? 1 : 0).join('');
    if (key === shelfKey) return; shelfKey = key;
    const had = document.activeElement;
    rows.forEach((row, k) => {
      const ol = rowEl(k).firstChild; ol.start = row[0].i + 1;
      if (row.some((bk, n) => ol.children[n] !== bk.li) || ol.children.length !== row.length) ol.append(...row.map(bk => bk.li));
    });
    for (let k = rows.length; k < rowEls.length; k++) rowEls[k].remove();
    for (const bk of books) {
      bk.li.style.setProperty('--a', bk.a);
      bk.li.classList.toggle('lean-r', !!bk.a && bk.dir < 0);
      bk.li.classList.toggle('lean-l', !!bk.a && bk.dir > 0);
    }
    if (out >= 0) seatGap(books[out]);
    if (had && had !== document.activeElement && had.isConnected) had.focus({ preventScroll: true });
  }
  // the reader sits under its book's shelf; the shelves below it make room
  function seatGap(bk) {
    const row = rowEls[bk.row];
    if (gap.previousElementSibling !== row) { gap.classList.remove('is-open'); row.after(gap); void gap.offsetHeight; }
  }
  const ro = new ResizeObserver(() => {
    if (caseEl.clientWidth === caseW) return; caseW = caseEl.clientWidth;
    readScale(); layoutShelves(); if (out >= 0) placeReader(books[out]);
  });
  ro.observe(caseEl); life.later(() => ro.disconnect());
  life.on(narrow, 'change', () => { readScale(); layoutShelves(); });

  // ---------- state ----------
  let hover = -1, focused = -1, out = -1, lastPointer = 'mouse', hasGL = false;
  function setRead(i) {
    if (i < 0) { read.classList.remove('is-on'); return; }
    const r = books[i].rec;
    read.querySelector('.sp-read-title').textContent = r.title;
    read.querySelector('.sp-read-by').textContent = [r.desc, r.chips[0]].filter(Boolean).join(', ');
    read.classList.add('is-on');
  }
  for (const bk of books) {
    life.on(bk.b, 'pointerenter', (e) => { if (e.pointerType === 'mouse') { hover = bk.i; setRead(bk.i); } });
    life.on(bk.b, 'pointerleave', () => { if (hover === bk.i) { hover = -1; setRead(focused); } });
    life.on(bk.b, 'pointerdown', (e) => { lastPointer = e.pointerType; });
    life.on(bk.b, 'focus', () => { if (lastPointer === 'keyboard') { focused = bk.i; setRead(bk.i); } });
    life.on(bk.b, 'blur', () => { if (focused === bk.i) { focused = -1; setRead(hover); } });
    life.on(bk.b, 'click', () => { lastPointer = 'keyboard'; out === bk.i ? putBack() : pull(bk.i); });
  }
  life.on(window, 'keydown', (e) => {
    lastPointer = 'keyboard';
    if (e.key === 'Escape' && out >= 0 && !document.querySelector('dialog[open]')) { const b = books[out].b; putBack(); b.focus({ preventScroll: true }); }
  }, { capture: true });
  const back = () => { const b = out >= 0 ? books[out].b : null; putBack(); b?.focus({ preventScroll: true }); };
  // clicking anywhere away from the shelf and the open book's text puts it back
  life.on(document, 'click', (e) => {
    if (out < 0 || !e.isTrusted) return;
    const t = e.target;
    if (books.some(bk => bk.b.contains(t)) || readerDetails.contains(t) || t.closest?.('a, button, dialog, input, textarea, select')) return;
    if (getSelection()?.toString()) return; // selecting the description isn't clicking away
    putBack();
  });
  life.on(reader.querySelector('.sp-cover'), 'click', back);

  function placeReader(bk) {
    const cw = bk.D * S, ch = bk.H * S;
    reader.style.setProperty('--cw', cw + 'px');
    reader.style.setProperty('--ch', ch + 'px');
    // the cover lands under its own slot, kept inside the column with room for the text
    const main = wrap.getBoundingClientRect(), slot = bk.li.getBoundingClientRect();
    const need = cw + 28 + Math.min(440, main.width);
    const rx = Math.max(0, Math.min(slot.left - main.left - cw * 0.25, main.width - need));
    reader.style.setProperty('--rx', Math.round(rx) + 'px');
  }
  function pull(i) {
    if (out >= 0 && out !== i) { const o = books[out]; o.target = 0; o.b.setAttribute('aria-expanded', 'false'); o.li.classList.remove('is-out'); }
    const bk = books[i];
    out = i; bk.target = 1;
    bk.b.setAttribute('aria-expanded', 'true'); bk.li.classList.add('is-out');
    readerImg.src = bk.rec.images[0] || ''; readerImg.alt = `Cover of ${bk.rec.title}`;
    fillDetails(readerDetails, bk.rec);
    reader.hidden = false; reader.classList.remove('is-in');
    seatGap(bk); gap.classList.add('is-open');
    placeReader(bk);
    if (!hasGL) reader.classList.add('is-in');
  }
  function putBack() {
    if (out < 0) return;
    const bk = books[out];
    bk.target = 0; bk.b.setAttribute('aria-expanded', 'false'); bk.li.classList.remove('is-out');
    out = -1; reader.classList.remove('is-in'); gap.classList.remove('is-open');
    if (!hasGL) reader.hidden = true;
  }
  life.on(window, 'resize', () => { readScale(); layoutShelves(); if (out >= 0) placeReader(books[out]); });
  layoutShelves();

  // ---------- the static shelf (reduced motion, no WebGL): DOM spines, type in ink or paper to suit ----------
  function tintStatic() {
    for (const bk of books) {
      const bg = mixRGB(TH.paper, bk.colour, P['spine-tone']);
      bk.li.style.setProperty('--tc', typeOn(bg, TH) === TH.ink ? 'var(--ink)' : 'var(--paper)');
    }
  }
  let staticT = 0;
  function goStatic() {
    hasGL = false;
    root.classList.remove('sp-gl', 'sp-pending'); root.classList.add('sp-static');
    if (out >= 0) { reader.hidden = false; reader.classList.add('is-in'); } else reader.hidden = true;
    tintStatic();
    clearInterval(staticT); staticT = setInterval(() => { readFnd(P); tintStatic(); layoutShelves(); }, 400);
  }
  life.later(() => clearInterval(staticT));
  life.later(onTheme((c) => { TH = c; if (!hasGL) tintStatic(); }));

  // ---------- the books (three.js), in a lifetime of their own so reduced motion can end them alone ----------
  const noGL = reduced.matches || /(^|[?&])static\b/.test(location.search);
  const THREE = noGL ? null : await loadThree();
  if (life.dead) return null;
  let renderer = null, canvas = null;
  if (THREE) {
    canvas = gridCanvas('spines');
    try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' }); if (!renderer.getContext()) throw 0; }
    catch { renderer?.dispose(); renderer = null; canvas.remove(); if (!document.querySelector('canvas.grid-gl')) root.classList.remove('has-grid-gl'); }
  }
  if (!renderer) { goStatic(); return api(); }

  const gl = lifetime(life.signal);
  hasGL = true;
  root.classList.remove('sp-pending', 'sp-static'); root.classList.add('sp-gl');
  renderer.setClearColor(0x000000, 0);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera();
  const R = Math.max(2, Math.min(3, devicePixelRatio || 1));
  const loader = new THREE.TextureLoader();
  const PAGES = new THREE.Color('#efebe3'), EDGE = new THREE.Color('#e6e1d7');
  for (const bk of books) {
    const geo = new THREE.BoxGeometry(bk.T, bk.H, bk.D); geo.translate(0, bk.H / 2, -bk.D / 2);
    const cover = bk.rec.images[0] ? loader.load(bk.rec.images[0]) : null;
    if (cover) { cover.colorSpace = THREE.SRGBColorSpace; cover.anisotropy = 8; }
    const mask = new THREE.CanvasTexture(spineMask(bk, R)); mask.colorSpace = THREE.NoColorSpace; mask.anisotropy = 8;
    const spineMat = new THREE.ShaderMaterial({
      vertexShader: SPINE_VERT, fragmentShader: SPINE_FRAG,
      uniforms: { uMask: { value: mask }, uColor: { value: new THREE.Color() }, uInk: { value: new THREE.Color() }, uSize: { value: new THREE.Vector2(bk.T, bk.H) }, uTip: { value: 0 }, uEdge: { value: 0.09 } },
    });
    const backMat = new THREE.MeshBasicMaterial({ color: new THREE.Color() });
    const coverMat = cover ? new THREE.MeshBasicMaterial({ map: cover }) : new THREE.MeshBasicMaterial({ color: new THREE.Color() });
    const mats = [
      coverMat,                                          // +x: the front cover
      backMat,                                           // -x: the back
      new THREE.MeshBasicMaterial({ color: PAGES }),     // top: the page block
      new THREE.MeshBasicMaterial({ color: EDGE }),      // bottom
      spineMat,                                          // +z: the spine
      new THREE.MeshBasicMaterial({ color: PAGES }),     // -z: the fore-edge
    ];
    const mesh = new THREE.Mesh(geo, mats);
    const group = new THREE.Group(); group.rotation.order = 'ZXY'; group.add(mesh);
    scene.add(group);
    Object.assign(bk, { group, mesh, spineMat, backMat, coverMat: cover ? null : coverMat });
  }
  gl.later(() => {
    // CanvasTextures and the cover maps are on plain materials too
    scene.traverse((o) => { for (const m of [].concat(o.material || [])) m.map?.dispose(); });
    disposeGL(THREE, renderer, scene, canvas);
  });

  // the theme: spine colours stay the covers', the paper they mix with and the type follow it
  let colourKey = '';
  function paintSpines() {
    const key = TH.paper.join() + TH.ink.join() + P['spine-tone'].toFixed(3);
    if (key === colourKey) return; colourKey = key;
    const edge = TH.dark ? 0.16 : 0.09;
    for (const bk of books) {
      const rgb = mixRGB(TH.paper, bk.colour, P['spine-tone']);
      const u = bk.spineMat.uniforms;
      u.uColor.value.setRGB(rgb[0], rgb[1], rgb[2], THREE.SRGBColorSpace);
      const t = typeOn(rgb, TH);
      u.uInk.value.setRGB(t[0], t[1], t[2], THREE.SRGBColorSpace);
      u.uEdge.value = edge;
      bk.backMat.color.copy(u.uColor.value).multiplyScalar(0.86);
      bk.coverMat?.color.copy(u.uColor.value);
    }
  }

  let vw = 0, vh = 0;
  function resize() {
    if (vw === innerWidth && vh === innerHeight) return;
    vw = innerWidth; vh = innerHeight;
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
    renderer.setSize(vw, vh, false);
  }
  // an off-axis camera: world units are CSS px, the z = 0 plane is the page exactly
  function aimCamera(ex, ey, dist) {
    const near = 10, far = dist + 4000, k = near / dist;
    camera.position.set(ex, ey, dist);
    camera.updateMatrixWorld();
    camera.projectionMatrix.makePerspective((0 - ex) * k, (vw - ex) * k, (0 - ey) * k, (-vh - ey) * k, near, far);
    camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();
  }
  function spring(o, key, vkey, target, k, zeta, dt) {
    const w = Math.sqrt(k), c = 2 * zeta * w;
    o[vkey] += (k * (target - o[key]) - c * o[vkey]) * dt;
    o[key] += o[vkey] * dt;
  }

  let last = performance.now(), frameN = 0;
  function frame(now) {
    gl.frame(frame);
    if (document.hidden) return;
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (frameN++ % 6 === 0) { readFnd(P); layoutShelves(); }
    if (document.querySelector('dialog[open]') && frameN % 4) return;
    resize(); paintSpines();
    const s = S, E = P.energy, order = P['spine-order'], depth = P['spine-depth'];

    const sr = shelf.getBoundingClientRect(), sc = caseEl.getBoundingClientRect();
    aimCamera(sc.left + sc.width * 0.45, -(sr.top - 36 * s), lerp(9000, 1900, depth));

    const pullK = lerp(26, 70, E), tipK = lerp(120, 260, E), tipZ = lerp(1, 0.55, E);
    let landed = false;
    for (const bk of books) {
      const i = bk.i, r = bk.li.getBoundingClientRect();
      const T = bk.T * s, H = bk.H * s, D = bk.D * s;

      // springs: the tip under the cursor, the pull, a neighbour leaning into a gap (30% at Neat)
      const tipTo = (i === hover || i === focused) && bk.target === 0 && bk.q < 0.05 ? 1 : 0;
      spring(bk, 'tip', 'tipV', tipTo, tipK, tipZ, dt);
      spring(bk, 'q', 'qV', bk.target, pullK, 1, dt);
      bk.q = Math.min(1.02, Math.max(-0.02, bk.q));
      const left = books[i - 1];
      let dynTo = 0;
      if (left && left.row === bk.row && bk.dir > 0 && !(bk.a > 0) && bk.q < 0.05) {
        const gap = left.li.getBoundingClientRect().width + 1 * s;
        dynTo = (0.3 + 0.7 * order) * Math.min(0.32, Math.asin(Math.min(0.95, gap / H)) * 0.9) * smooth(left.q * 3);
      }
      spring(bk, 'dyn', 'dynV', dynTo, lerp(30, 80, E), lerp(1, 0.7, E), dt);

      // the pose on the shelf
      const bottom = -r.bottom, base = bk.a * order;
      let x, y, rz;
      if (bk.dir < 0) {                                  // leaning right, on its bottom right corner
        const px = r.left + T * Math.cos(base);
        x = px - T / 2 * Math.cos(base); y = bottom + T / 2 * Math.sin(base); rz = -base;
      } else {                                           // upright, or leaning left on its bottom left corner
        const a = base + bk.dyn;
        const px = r.left + H * Math.sin(base);
        x = px + T / 2 * Math.cos(a); y = bottom + T / 2 * Math.sin(a); rz = a;
      }
      // the tip: the top comes toward you a little
      const tip = bk.tip;
      let z = tip * lerp(4, 16, depth) * s, rx = tip * lerp(0.05, 0.13, depth), ry = 0;
      bk.spineMat.uniforms.uTip.value = Math.max(0, tip);

      // the pull: out of the shelf toward you, then across, turning to the cover
      const q = Math.max(0, bk.q);
      if (q > 0.0005) {
        if (out === i) {
          const ir = readerImg.getBoundingClientRect();
          if (ir.width) bk.land = { x: ir.left + scrollX, y: ir.bottom + scrollY };
        }
        const a1 = smoother(q / 0.34), a2 = smoother((q - 0.3) / 0.7);
        const mz = D + 26 * s, my = y + 10 * s;
        const x1 = x, y1 = lerp(y, my, a1), z1 = lerp(z, mz, a1);
        if (bk.land && a2 > 0) {
          const ex = bk.land.x - scrollX, ey = -(bk.land.y - scrollY), ez = -T / 2;
          // an arc that stays in front of the shelf, landing flat on the page
          const cx = lerp(x1, ex, 0.5), cy = Math.max(y1, ey) + 30 * s, cz = Math.max(mz, D) + 60 * s;
          const u = a2, iu = 1 - u;
          x = iu * iu * x1 + 2 * iu * u * cx + u * u * ex;
          y = iu * iu * y1 + 2 * iu * u * cy + u * u * ey;
          z = iu * iu * z1 + 2 * iu * u * cz + u * u * ez;
          ry = -Math.PI / 2 * smoother((q - 0.36) / 0.56);
        } else { x = x1; y = y1; z = z1; }
        rz *= 1 - a1; rx *= 1 - a1;
        if (out === i && q > 0.97) landed = true;
      }
      bk.group.position.set(x, y, z);
      bk.group.rotation.set(rx, ry, rz);
      bk.mesh.scale.setScalar(s);
      bk.group.renderOrder = q > 0 ? 2 : 0;
    }
    // the details arrive once the book has landed; the reader goes when the book is home
    if (landed) reader.classList.add('is-in');
    if (out < 0 && !reader.hidden && books.every(b => b.q < 0.45)) reader.hidden = true;
    renderer.render(scene, camera);
  }
  gl.frame(frame);
  // reduced motion switched on: the books go, the static shelf stays (with its book out, if one is)
  life.on(reduced, 'change', () => { if (reduced.matches && !gl.dead) { gl.kill(); goStatic(); } });

  return api();

  function api() {
    // ?pull=N opens book N (1-based) on load, for checks without a pointer
    const n = parseInt(new URLSearchParams(location.search).get('pull'), 10);
    if (n >= 1 && n <= books.length) { const t = setTimeout(() => { if (!life.dead) pull(n - 1); }, 300); life.later(() => clearTimeout(t)); }
    return { destroy: () => { putBack(); life.kill(); } };
  }
}
```


Source: `site/js/grids/common.js`, whole file

```js
// What every gallery grid shares: its fixed canvas behind the page, its --fnd params,
// and one teardown that frees the WebGL context, the loop and every listener.
export const root = document.documentElement;
export const reduced = matchMedia('(prefers-reduced-motion: reduce)');

// three.js, fetched once and only when a grid needs it; null when it can't load
let threeP = null;
export function loadThree() {
  threeP ||= import('three').catch(() => { threeP = null; return null; });
  return threeP;
}

// the --fnd-* values a grid reads, clamped to 0..1; scale maps a key to the grid's own range
export function readFnd(P, scale = {}) {
  const cs = getComputedStyle(root);
  let changed = false;
  for (const k in P) {
    const v = parseFloat(cs.getPropertyValue('--fnd-' + k));
    if (!Number.isFinite(v)) continue;
    const n = Math.min(1, Math.max(0, v * (scale[k] ?? 1)));
    if (Math.abs(n - P[k]) > 1e-4) { P[k] = n; changed = true; }
  }
  return changed;
}

// the grid's canvas: fixed, full window, under the page (the site's own #gl stays above it)
export function gridCanvas(name) {
  const c = document.createElement('canvas');
  c.className = 'grid-gl grid-gl-' + name;
  c.setAttribute('aria-hidden', 'true');
  document.body.prepend(c);
  root.classList.add('has-grid-gl');
  return c;
}

// a lifetime: listeners via its signal, a rAF loop, and things to dispose, all ended by kill()
export function lifetime(outer) {
  const ac = new AbortController();
  const undo = [];
  let raf = 0, dead = false;
  const life = {
    signal: ac.signal,
    get dead() { return dead; },
    on(target, type, fn, opts = {}) { target.addEventListener(type, fn, { ...opts, signal: ac.signal }); },
    later(fn) { undo.push(fn); },
    frame(fn) { if (!dead) { cancelAnimationFrame(raf); raf = requestAnimationFrame(fn); } },
    kill() {
      if (dead) return;
      dead = true; ac.abort(); cancelAnimationFrame(raf);
      for (const f of undo.reverse()) { try { f(); } catch (e) { console.warn(e); } }
    },
  };
  // the gallery's own signal: a route change mid-mount ends the grid too
  if (outer?.aborted) life.kill(); else outer?.addEventListener('abort', () => life.kill(), { once: true });
  return life;
}

// free everything three made: geometries, materials, textures, then the context itself
export function disposeGL(THREE, renderer, scene, canvas) {
  scene?.traverse((o) => {
    o.geometry?.dispose();
    for (const m of [].concat(o.material || [])) {
      for (const u of Object.values(m.uniforms || {})) if (u?.value?.isTexture) u.value.dispose();
      m.dispose();
    }
  });
  if (renderer) { renderer.dispose(); renderer.forceContextLoss(); }
  canvas?.remove();
  if (!document.querySelector('canvas.grid-gl')) root.classList.remove('has-grid-gl');
}
```


Source: `site/css/site.css`, lines 583 to 669

```css
/* ---------- the gallery grids (js/grids/*): a canvas under the page, the DOM over it for focus and clicks ---------- */
.grid-gl { position: fixed; inset: 0; width: 100vw; height: 100vh; z-index: 0; pointer-events: none; display: block; }
html.has-grid-gl .site { position: relative; z-index: 1; }
@media print { .grid-gl { display: none; } }

/* Library, "Spines": the books stand spine-out on shelves, each filled to the column, the next below (one sideways shelf on a phone). The DOM sets every slot; the canvas draws the books on it.
   Hover tips a spine out; a click pulls the book, turns it to its cover and sets its details beside it. */
.sp { --spine-s: 1; --sp-rule: color-mix(in srgb, var(--ink) 14%, transparent); min-width: 0;
  --sp-shadow: 0 14px 32px -14px color-mix(in srgb, var(--shadow) calc(40% * var(--shadow-k)), transparent), 0 2px 6px -3px color-mix(in srgb, var(--shadow) calc(18% * var(--shadow-k)), transparent); }
.sp-head { display: flex; align-items: baseline; gap: var(--gap); height: 16px; margin-bottom: 40px; font: 400 16px/16px var(--ui); letter-spacing: var(--track); }
.sp-title { margin: 0; font: inherit; white-space: nowrap; filter: url(#ink-ui); }
.sp-count { margin-left: 4px; opacity: var(--op-faint); font-variant-numeric: tabular-nums; }
.sp-read { display: flex; gap: 8px; min-width: 0; white-space: nowrap; overflow: hidden; filter: url(#ink-ui); opacity: 0; transition: opacity 200ms var(--ease-land); }
.sp-read.is-on { opacity: 1; }
.sp-read-title { overflow: hidden; text-overflow: ellipsis; }
.sp-read-by { opacity: var(--op-meta); flex: none; }
.sp-case { position: relative; }
.sp-case > .sp-row:not(:first-child) { margin-top: 48px; }
.sp-shelf { display: flex; align-items: flex-end; width: 100%; margin: 0; padding: 0; list-style: none; box-shadow: 0 1px 0 var(--sp-rule); }
html.sp-pending .sp-shelf { visibility: hidden; }
/* the room the reader takes under its shelf opens and closes with the book; the sides keep its shadow */
.sp-gap { display: grid; grid-template-rows: 0fr; transition: grid-template-rows 520ms var(--ease-land); }
.sp-gap.is-open { grid-template-rows: 1fr; }
.sp-gap-in { min-height: 0; overflow: hidden; margin: 0 -40px; padding: 0 40px; }
.sp-book {
  /* --bt thickness, --bh height (px at scale 1), --a base lean in rad (its side is set in JS), --j gap jitter, --c cover colour */
  flex: none; position: relative;
  margin-left: calc(var(--spine-s) * (1px + var(--j, 0) * var(--fnd-spine-order) * 5px));
  /* the slot: thickness plus the room a lean takes (sin a ~ a, cos a ~ 1 at these angles) */
  width: calc(var(--spine-s) * 1px * (var(--bt) + var(--bh) * var(--a, 0) * var(--fnd-spine-order)));
  height: calc(var(--spine-s) * var(--bh) * 1px);
}
.sp-book:first-child { margin-left: 0; }
.sp-btn { position: absolute; inset: 0; display: block; width: 100%; height: 100%; padding: 0; cursor: pointer; outline: none;
  -webkit-tap-highlight-color: transparent; touch-action: manipulation; }
.sp-btn:focus-visible::after { content: ""; position: absolute; left: 0; right: 0; bottom: -6px; height: 1px; background: var(--ring); }
.sp-face { position: absolute; left: 0; bottom: 0; width: calc(var(--spine-s) * var(--bt) * 1px); height: 100%; display: flex; flex-direction: column; justify-content: space-between; align-items: center;
  padding: calc(var(--spine-s) * 12px) 0 calc(var(--spine-s) * 10px); overflow: hidden;
  background: color-mix(in srgb, var(--c, #ddd) calc(var(--fnd-spine-tone) * 100%), var(--paper)); color: var(--tc, var(--ink));
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--ink) 10%, transparent); }
.sp-face span { writing-mode: vertical-rl; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-height: 100%; }
.sf-title { font: 400 calc(var(--spine-s) * 13px)/1 var(--ui); letter-spacing: -0.3px; flex: 0 1 auto; }
.sf-by { font: 400 calc(var(--spine-s) * 11px)/1 var(--ui); letter-spacing: -0.2px; opacity: .62; margin-top: calc(var(--spine-s) * 10px); flex: 0 1 auto; }
.sf-year { font: 400 calc(var(--spine-s) * 9px)/1 var(--mono); opacity: .5; margin-top: auto; flex: none; font-variant-numeric: tabular-nums; }
/* the canvas draws the books; the DOM keeps the layout, the focus and the hits */
html.sp-gl .sp-face { visibility: hidden; }
html.sp-static .sp-book.is-out .sp-face { visibility: hidden; }
html.sp-static .sp-btn:hover .sp-face { translate: 0 -3px; }
/* the static leans: on a corner, into the room the slot keeps for them */
html.sp-static .lean-r .sp-face { transform-origin: 100% 100%; transform: rotate(calc(var(--a) * var(--fnd-spine-order) * 1rad)); }
html.sp-static .lean-l .sp-face { left: auto; right: 0; transform-origin: 0 100%; transform: rotate(calc(var(--a) * var(--fnd-spine-order) * -1rad)); }
/* the reader: the pulled book's cover and its details, no modal */
.sp-reader { position: relative; display: flex; gap: 28px; align-items: flex-start; padding: 44px 0 28px; margin-left: var(--rx, 0px); width: max-content; max-width: 100%; }
.sp-reader[hidden] { display: none; }
.sp-cover { position: relative; flex: none; display: block; width: var(--cw, 200px); height: var(--ch, 280px); padding: 0; cursor: pointer; outline: none; }
.sp-cover img { display: block; width: 100%; height: 100%; object-fit: fill; border-radius: 1px;
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 8%, transparent), var(--sp-shadow); }
html.sp-gl .sp-cover img { visibility: hidden; }
/* the book's own shadow on the page, there once it has landed */
html.sp-gl .sp-cover::before { content: ""; position: absolute; inset: 0; border-radius: 1px; pointer-events: none; opacity: 0; box-shadow: var(--sp-shadow); transition: opacity 320ms var(--ease-land); }
html.sp-gl .sp-reader.is-in .sp-cover::before { opacity: 1; }
.sp-cover:focus-visible { box-shadow: 0 1px 0 0 var(--ring); }
.sp-text { display: flex; flex-direction: column; gap: 6px; width: min(440px, 100%); min-width: 0; padding-top: 2px;
  opacity: 0; transform: translateY(4px); filter: blur(3px); transition: opacity 260ms var(--ease-land), transform 260ms var(--ease-land), filter 260ms var(--ease-land); }
.sp-reader.is-in .sp-text { opacity: 1; transform: none; filter: blur(0); }
.sp-details { display: flex; flex-direction: column; gap: 6px; }
.sp-back { align-self: flex-start; margin-top: 18px; display: inline-flex; gap: 8px; padding: 0; font: 400 14px/20px var(--ui); letter-spacing: -0.3px; color: color-mix(in srgb, var(--ink) 56%, var(--paper)); transition: color 160ms var(--ease-land); }
.sp-back span { font: 400 11px/20px var(--mono); opacity: .7; }
.sp-back:hover, .sp-back:focus-visible { color: var(--ink); outline: none; }
.sp-back:focus-visible { text-decoration: underline; text-underline-offset: 4px; text-decoration-thickness: 1px; }
@media (max-width: 899px) {
  .sp { --spine-s: 0.72; width: 100%; }
  .sp-head { flex-direction: column; align-items: flex-start; height: auto; gap: 8px; margin-bottom: 28px; }
  .sp-read { max-width: 100%; height: 16px; }
  /* the shelf runs to the screen's edges and scrolls sideways */
  .sp-row { overflow-x: auto; overflow-y: visible; scrollbar-width: none; padding: 28px 12px 0; margin: -28px -12px 0; scroll-padding: 0 12px; }
  .sp-row::-webkit-scrollbar { display: none; }
  .sp-shelf { min-width: 100%; width: max-content; }
  .sp-reader { flex-direction: column; gap: 20px; margin-left: 0; padding-top: 32px; width: auto; }
  .sp-text { width: 100%; }
}
@media (prefers-reduced-motion: reduce) {
  .sp-text { transition: none; transform: none; filter: none; }
  .sp-gap { transition: none; }
  html.sp-static .sp-btn:hover .sp-face { translate: none; }
}
```
