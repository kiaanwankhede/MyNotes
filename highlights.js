/* Highlights for the notes reader.
   - Select text, tap "Highlight". Tap a highlight to remove it.
   - Each highlight stores its exact text plus a little text before and after it, so it is
     re-found after the page changes. If the text itself is rewritten it moves to "Needs attention".
   - "Marked only" shows just the highlighted lines (with their headings).
   - Highlights are kept on the device and synced through a private GitHub repo (file highlights.json). */
(function () {
  var CFG = { owner: 'kiaanwankhede', repo: 'MyNotes-highlights', path: 'highlights.json' };
  var API = 'https://api.github.com/repos/' + CFG.owner + '/' + CFG.repo + '/contents/' + CFG.path;
  var LS_DATA = 'notes-hl-data', LS_TOK = 'notes-hl-token', LS_ONLY = 'notes-hl-only';
  var doc = document.getElementById('doc');
  var store = loadStore(), cur = null, idx = null, orphans = [];
  var only = false, busy = false, again = false, timer = null, status = 'local', errMsg = '';
  var pending = null, barMode = null, removeIds = [], barTouch = false, barTimer = null, selTimer = null;
  try { only = localStorage.getItem(LS_ONLY) === '1'; } catch (e) {}

  function loadStore() { try { var d = JSON.parse(localStorage.getItem(LS_DATA)); if (d && d.items) return d; } catch (e) {} return { items: {} }; }
  function saveStore() { try { localStorage.setItem(LS_DATA, JSON.stringify(store)); } catch (e) {} }
  function token() { try { return localStorage.getItem(LS_TOK) || ''; } catch (e) { return ''; } }

  /* ---------- text index of the page ---------- */
  var SKIP = '.mtoc,.pager,.mermaid,.hlbanner,.hlnone';
  function buildIndex() {
    var nodes = [], S = '';
    var w = document.createTreeWalker(doc, NodeFilter.SHOW_TEXT, { acceptNode: function (n) {
      var p = n.parentElement; return (!p || p.closest(SKIP)) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; } });
    while (w.nextNode()) { var n = w.currentNode; nodes.push({ n: n, s: S.length }); S += n.data; }
    idx = { S: S, nodes: nodes };
  }
  function offsetOf(node, off) {
    var i, e;
    if (node.nodeType === 3) { for (i = 0; i < idx.nodes.length; i++) { e = idx.nodes[i]; if (e.n === node) return e.s + off; } }
    var r = document.createRange(); r.setStart(node, off); r.collapse(true);
    for (i = 0; i < idx.nodes.length; i++) { e = idx.nodes[i]; if (r.comparePoint(e.n, 0) >= 0) return e.s; }
    return idx.S.length;
  }
  function sfx(a, b) { var n = 0; while (n < a.length && n < b.length && a[a.length - 1 - n] === b[b.length - 1 - n]) n++; return n; }
  function pfx(a, b) { var n = 0; while (n < a.length && n < b.length && a[n] === b[n]) n++; return n; }
  function locate(h) {
    var S = idx.S, t = h.text, hits = [], i = -1;
    while ((i = S.indexOf(t, i + 1)) >= 0) hits.push(i);
    if (hits.length) {
      var best = hits[0], bs = -1;
      hits.forEach(function (p) {
        var sc = sfx(h.pre || '', S.slice(Math.max(0, p - 40), p)) + pfx(h.post || '', S.slice(p + t.length, p + t.length + 40));
        if (sc > bs) { bs = sc; best = p; }
      });
      return [best, best + t.length];
    }
    var pt = (h.pre || '').slice(-24), qt = (h.post || '').slice(0, 24);
    if (pt.length >= 12 && qt.length >= 12) {
      var a = S.indexOf(pt);
      if (a >= 0) { var s0 = a + pt.length, b = S.indexOf(qt, s0); if (b >= 0 && b - s0 > 0 && b - s0 <= Math.max(t.length * 2, 60)) return [s0, b]; }
    }
    return null;
  }
  function wrap(a, b, id) {
    idx.nodes.forEach(function (e) {
      var s = e.s, t = s + e.n.data.length; if (t <= a || s >= b) return;
      var from = Math.max(a, s) - s, to = Math.min(b, t) - s;
      if (!e.n.data.slice(from, to).trim()) return;
      var r = document.createRange(); r.setStart(e.n, from); r.setEnd(e.n, to);
      var m = document.createElement('mark'); m.className = 'hl'; m.setAttribute('data-id', id);
      r.surroundContents(m);
    });
  }
  function unwrapAll() {
    doc.querySelectorAll('mark.hl').forEach(function (m) {
      var p = m.parentNode; if (!p) return; while (m.firstChild) p.insertBefore(m.firstChild, m); p.removeChild(m); p.normalize();
    });
  }

  /* ---------- render ---------- */
  function mine() {
    return Object.keys(store.items).map(function (k) { return store.items[k]; })
      .filter(function (h) { return !h.del && cur && h.book === cur.book && h.ch === cur.ch; });
  }
  function apply(book, ch) { cur = { book: book, ch: ch || '_intro' }; render(); }
  function render() {
    if (!cur) return;
    unwrapAll();
    var old = doc.querySelector('.hlbanner'); if (old) old.remove();
    buildIndex(); orphans = [];
    mine().forEach(function (h) {
      var r = locate(h); if (!r) { orphans.push(h); return; }
      wrap(r[0], r[1], h.id); buildIndex();
    });
    banner(); applyMode(); updateUi();
  }
  function banner() {
    if (!orphans.length) return;
    var h1 = doc.querySelector('h1'); if (!h1) return;
    var d = document.createElement('div'); d.className = 'hlbanner';
    d.innerHTML = '<span></span> <button type="button">Review</button>';
    d.firstChild.textContent = '⚠ ' + orphans.length + ' highlight' + (orphans.length > 1 ? 's' : '') + ' on this page could not be placed because the text changed.';
    d.querySelector('button').addEventListener('click', openPanel);
    h1.after(d);
  }

  /* ---------- "marked only" view ---------- */
  function applyMode() {
    doc.classList.toggle('hlonly', only);
    doc.querySelectorAll('.hlhide').forEach(function (e) { e.classList.remove('hlhide'); });
    var nm = doc.querySelector('.hlnone'); if (nm) nm.remove();
    if (!only) return;
    var keeps = [];
    doc.querySelectorAll('mark.hl').forEach(function (m) {
      var k = m.closest('li,p,tr,pre,h1,h2,h3,h4,summary'); if (k && keeps.indexOf(k) < 0) keeps.push(k);
    });
    var full = new Set(), anc = new Set(), h1 = doc.querySelector('h1');
    if (h1) full.add(h1);
    if (!keeps.length) {
      var n = document.createElement('p'); n.className = 'hlnone';
      n.textContent = 'No highlights on this page yet. Select any text and tap Highlight.';
      if (h1) h1.after(n);
    }
    keeps.forEach(function (k) {
      full.add(k);
      for (var x = k.parentElement; x && x !== doc; x = x.parentElement) {
        anc.add(x);
        if (x.tagName === 'DETAILS') { x.open = true; var s = x.querySelector(':scope>summary'); if (s) full.add(s); }
        if (x.classList.contains('callout')) { var t = x.querySelector('.ctitle'); if (t) full.add(t); }
        if (x.tagName === 'TABLE') { var hd = x.querySelector('thead tr'); if (hd) full.add(hd); }
      }
      var top = k; while (top.parentElement && top.parentElement !== doc) top = top.parentElement;
      var g3 = false, sib = top.previousElementSibling;
      while (sib) {
        if (sib.tagName === 'H3' && !g3) { full.add(sib); g3 = true; }
        else if (sib.tagName === 'H2') { full.add(sib); break; }
        sib = sib.previousElementSibling;
      }
    });
    doc.querySelectorAll('*').forEach(function (el) {
      if (el.closest('.pager,.hlbanner,.hlnone')) return;
      if (anc.has(el)) return;
      for (var x = el; x && x !== doc; x = x.parentElement) if (full.has(x)) return;
      el.classList.add('hlhide');
    });
  }

  /* ---------- create / remove ---------- */
  function readSelection() {
    var sel = window.getSelection(); if (!sel || sel.isCollapsed || !sel.rangeCount) return null;
    var r = sel.getRangeAt(0);
    if (!doc.contains(r.startContainer) || !doc.contains(r.endContainer)) return null;
    buildIndex();
    var a = offsetOf(r.startContainer, r.startOffset), b = offsetOf(r.endContainer, r.endOffset);
    if (b <= a) return null;
    var S = idx.S, t = S.slice(a, b), lead = t.length - t.replace(/^\s+/, '').length;
    a += lead; t = t.trim(); b = a + t.length;
    if (t.length < 2 || t.length > 2000) return null;
    return { text: t, pre: S.slice(Math.max(0, a - 40), a), post: S.slice(b, b + 40) };
  }
  function newId() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }
  function add(o) {
    if (!cur) return; var id = newId();
    store.items[id] = { id: id, book: cur.book, ch: cur.ch, text: o.text, pre: o.pre, post: o.post, u: Date.now() };
    saveStore(); render(); schedule();
  }
  function removeId(id) {
    var h = store.items[id]; if (!h) return;
    store.items[id] = { id: id, del: 1, book: h.book, ch: h.ch, u: Date.now() };
    saveStore(); render(); schedule();
  }

  /* ---------- bottom button ---------- */
  var bar = document.createElement('button');
  bar.type = 'button'; bar.className = 'hlbar'; bar.hidden = true; document.body.appendChild(bar);
  function showBar(mode, label) { barMode = mode; bar.textContent = label; bar.hidden = false; }
  function hideBar() { bar.hidden = true; barMode = null; pending = null; removeIds = []; clearTimeout(barTimer); }
  bar.addEventListener('pointerdown', function (e) { barTouch = true; e.preventDefault(); setTimeout(function () { barTouch = false; }, 600); });
  bar.addEventListener('mousedown', function (e) { e.preventDefault(); });
  bar.addEventListener('click', function () {
    if (barMode === 'hl' && pending) { add(pending); var s = window.getSelection(); if (s) s.removeAllRanges(); }
    else if (barMode === 'rm') { removeIds.forEach(removeId); }
    hideBar();
  });
  document.addEventListener('selectionchange', function () {
    clearTimeout(selTimer);
    selTimer = setTimeout(function () {
      if (barTouch) return;
      var o = readSelection();
      if (o) { pending = o; showBar('hl', '✎ Highlight'); }
      else if (barMode === 'hl') hideBar();
    }, 140);
  });
  doc.addEventListener('click', function (e) {
    var m = e.target.closest && e.target.closest('mark.hl'); var s = window.getSelection();
    if (!m || (s && !s.isCollapsed)) { if (barMode === 'rm') hideBar(); return; }
    removeIds = []; for (var x = m; x && x !== doc; x = x.parentElement) if (x.tagName === 'MARK' && x.getAttribute('data-id')) removeIds.push(x.getAttribute('data-id'));
    showBar('rm', '✕ Remove highlight'); clearTimeout(barTimer); barTimer = setTimeout(hideBar, 7000);
  });

  /* ---------- header buttons ---------- */
  var tbtn = document.getElementById('hlt'), sbtn = document.getElementById('hlset');
  function updateUi() {
    tbtn.setAttribute('aria-pressed', only ? 'true' : 'false');
    tbtn.classList.toggle('on', only);
    sbtn.querySelector('.dot').className = 'dot ' + status;
    sbtn.title = statusText();
    var n = mine().length; tbtn.title = n ? n + ' highlight' + (n > 1 ? 's' : '') + ' on this page' : 'No highlights on this page';
  }
  tbtn.addEventListener('click', function () {
    only = !only; try { localStorage.setItem(LS_ONLY, only ? '1' : '0'); } catch (e) {}
    applyMode(); updateUi(); var m = document.getElementById('main'); if (m) m.scrollTop = 0;
  });
  sbtn.addEventListener('click', openPanel);

  /* ---------- sync with the private repo ---------- */
  function b64e(s) { var b = new TextEncoder().encode(s), r = ''; for (var i = 0; i < b.length; i += 8192) r += String.fromCharCode.apply(null, b.subarray(i, i + 8192)); return btoa(r); }
  function b64d(s) { var r = atob(s.replace(/\s/g, '')), b = new Uint8Array(r.length); for (var i = 0; i < r.length; i++) b[i] = r.charCodeAt(i); return new TextDecoder().decode(b); }
  function gh(method, body) {
    return fetch(API, { method: method, cache: 'no-store', body: body ? JSON.stringify(body) : undefined,
      headers: { 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + token(), 'X-GitHub-Api-Version': '2022-11-28' } });
  }
  function merge(a, b) {
    var out = {}, localChanged = false, remoteChanged = false, ids = {};
    Object.keys(a).forEach(function (k) { ids[k] = 1; }); Object.keys(b).forEach(function (k) { ids[k] = 1; });
    Object.keys(ids).forEach(function (k) {
      var x = a[k], y = b[k], c = !x ? y : !y ? x : (y.u > x.u ? y : x);
      out[k] = c;
      if (!x || x.u !== c.u) localChanged = true;
      if (!y || y.u !== c.u) remoteChanged = true;
    });
    return { items: out, local: localChanged, remote: remoteChanged };
  }
  function setStatus(s) { status = s; updateUi(); var el = document.getElementById('hlstatus'); if (el) el.textContent = statusText(); }
  function statusText() {
    if (status === 'ok') return 'Synced ✓';
    if (status === 'busy') return 'Syncing…';
    if (status === 'err') return 'Sync problem: ' + errMsg;
    return 'Saved on this device only. Add a token to sync across devices.';
  }
  function schedule() { if (!token()) return; clearTimeout(timer); timer = setTimeout(sync, 1200); }
  function sync() {
    if (!token()) { setStatus('local'); return Promise.resolve(); }
    if (busy) { again = true; return Promise.resolve(); }
    busy = true; setStatus('busy');
    return attempt(0).then(function () { setStatus('ok'); })
      .catch(function (e) { errMsg = String(e && e.message || e); setStatus(navigator.onLine === false ? 'local' : 'err'); })
      .then(function () { busy = false; if (again) { again = false; schedule(); } });
  }
  function attempt(n) {
    return gh('GET').then(function (r) {
      if (r.status === 404) return { items: {}, sha: null };
      if (r.status === 401 || r.status === 403) throw new Error('GitHub rejected the token (' + r.status + '). It needs Contents read and write on ' + CFG.repo + '.');
      if (!r.ok) throw new Error('GitHub error ' + r.status);
      return r.json().then(function (j) { var d = {}; try { d = JSON.parse(b64d(j.content)); } catch (e) {} return { items: d.items || {}, sha: j.sha }; });
    }).then(function (rem) {
      var m = merge(store.items, rem.items);
      if (m.local) { store.items = m.items; saveStore(); render(); }
      if (!m.remote && rem.sha) return;
      var body = { message: 'Update highlights', content: b64e(JSON.stringify({ v: 1, items: m.items })) };
      if (rem.sha) body.sha = rem.sha;
      return gh('PUT', body).then(function (r) {
        if (r.status === 409 || r.status === 422) { if (n < 2) return attempt(n + 1); throw new Error('Conflict, will retry'); }
        if (r.status === 404) throw new Error('Repository ' + CFG.repo + ' not found, or the token has no access to it.');
        if (r.status === 401 || r.status === 403) throw new Error('GitHub rejected the token (' + r.status + '). It needs Contents read and write on ' + CFG.repo + '.');
        if (!r.ok) throw new Error('GitHub error ' + r.status);
      });
    });
  }
  setInterval(function () { if (!document.hidden) sync(); }, 15000);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) sync(); });
  window.addEventListener('online', sync);
  window.addEventListener('focus', sync);

  /* ---------- settings panel ---------- */
  var panel = document.createElement('div');
  panel.id = 'hlpanel'; panel.hidden = true; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Highlights and sync');
  panel.innerHTML =
    '<div class="hlcard"><div class="hlhead"><strong>Highlights &amp; sync</strong><button type="button" id="hlclose" aria-label="Close">✕</button></div>' +
    '<p id="hlstatus" class="hlstat"></p>' +
    '<label for="hltoken">GitHub token (stays in this browser only)</label>' +
    '<input id="hltoken" type="password" autocomplete="off" placeholder="github_pat_…">' +
    '<div class="hlrow"><button type="button" id="hlsave">Save &amp; sync</button><button type="button" id="hlnow">Sync now</button><button type="button" id="hlforget">Disconnect</button></div>' +
    '<details class="hlhelp"><summary>How to get a token</summary><ol>' +
    '<li>GitHub → Settings → Developer settings → Fine-grained tokens → Generate new token.</li>' +
    '<li>Repository access: only <code>' + CFG.repo + '</code>. Permissions → Contents: Read and write.</li>' +
    '<li>Copy the token and paste it above, once on each device.</li></ol></details>' +
    '<div class="hlrow"><button type="button" id="hlexp">Export</button><label class="hlfile">Import<input type="file" id="hlimp" accept="application/json" hidden></label></div>' +
    '<div id="hlorph"></div></div>';
  document.body.appendChild(panel);
  function openPanel() {
    document.getElementById('hltoken').value = token() ? '••••••••••••' : '';
    document.getElementById('hlstatus').textContent = statusText();
    var box = document.getElementById('hlorph'); box.innerHTML = '';
    if (orphans.length) {
      var h = document.createElement('p'); h.className = 'hlstat'; h.textContent = 'Needs attention on this page (' + orphans.length + '): the text changed, so these could not be placed.'; box.appendChild(h);
      orphans.forEach(function (o) {
        var row = document.createElement('div'); row.className = 'hlorph';
        var q = document.createElement('q'); q.textContent = o.text.length > 160 ? o.text.slice(0, 160) + '…' : o.text;
        var b = document.createElement('button'); b.type = 'button'; b.textContent = 'Remove';
        b.addEventListener('click', function () { removeId(o.id); openPanel(); });
        row.appendChild(q); row.appendChild(b); box.appendChild(row);
      });
    }
    panel.hidden = false;
  }
  function closePanel() { panel.hidden = true; }
  document.getElementById('hlclose').addEventListener('click', closePanel);
  panel.addEventListener('click', function (e) { if (e.target === panel) closePanel(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePanel(); });
  document.getElementById('hlsave').addEventListener('click', function () {
    var v = document.getElementById('hltoken').value.trim();
    if (v && v.indexOf('•') < 0) { try { localStorage.setItem(LS_TOK, v); } catch (e) {} }
    document.getElementById('hltoken').value = token() ? '••••••••••••' : '';
    sync();
  });
  document.getElementById('hlnow').addEventListener('click', function () { sync(); });
  document.getElementById('hlforget').addEventListener('click', function () {
    try { localStorage.removeItem(LS_TOK); } catch (e) {}
    document.getElementById('hltoken').value = ''; setStatus('local');
  });
  document.getElementById('hlexp').addEventListener('click', function () {
    var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify({ v: 1, items: store.items }, null, 1)], { type: 'application/json' }));
    a.download = 'notes-highlights.json'; document.body.appendChild(a); a.click(); a.remove();
  });
  document.getElementById('hlimp').addEventListener('change', function (e) {
    var f = e.target.files[0]; if (!f) return; var rd = new FileReader();
    rd.onload = function () {
      try { var d = JSON.parse(rd.result); var m = merge(store.items, d.items || {}); store.items = m.items; saveStore(); render(); schedule(); } catch (x) { alert('That file is not a highlights export.'); }
    }; rd.readAsText(f); e.target.value = '';
  });

  window.HL = { apply: apply, sync: sync, render: render };
  setStatus(token() ? 'busy' : 'local');
  sync();
})();
