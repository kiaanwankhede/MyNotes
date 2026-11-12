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
  var pageMode = false, focusId = null, fBook = '', fText = '';
  var pending = null, barMode = null, removeIds = [], barTouch = false, barTimer = null, selTimer = null;
  try { only = localStorage.getItem(LS_ONLY) === '1'; } catch (e) {}

  function loadStore() { try { var d = JSON.parse(localStorage.getItem(LS_DATA)); if (d && d.items) { if (!d.notes) d.notes = {}; return d; } } catch (e) {} return { items: {}, notes: {} }; }
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
  function wrap(a, b, id, kind) {
    idx.nodes.forEach(function (e) {
      var s = e.s, t = s + e.n.data.length; if (t <= a || s >= b) return;
      var from = Math.max(a, s) - s, to = Math.min(b, t) - s;
      if (!e.n.data.slice(from, to).trim()) return;
      var r = document.createRange(); r.setStart(e.n, from); r.setEnd(e.n, to);
      var m = document.createElement('mark'); m.className = kind === 'flag' ? 'hl flag' : 'hl'; m.setAttribute('data-id', id);
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
  function apply(book, ch) { pageMode = false; cur = { book: book, ch: ch || '_intro' }; render(); focus(); }
  function focus() {
    if (!focusId) return; var m = doc.querySelector('mark.hl[data-id="' + focusId + '"]'); focusId = null; if (!m) return;
    m.scrollIntoView({ block: 'center' }); var all = doc.querySelectorAll('mark.hl[data-id="' + m.getAttribute('data-id') + '"]');
    all.forEach(function (x) { x.classList.add('flash'); }); setTimeout(function () { all.forEach(function (x) { x.classList.remove('flash'); }); }, 2200);
  }
  function render() {
    if (!cur) return;
    unwrapAll();
    var old = doc.querySelector('.hlbanner'); if (old) old.remove();
    buildIndex(); orphans = [];
    mine().forEach(function (h) {
      var r = locate(h); if (!r) { orphans.push(h); return; }
      wrap(r[0], r[1], h.id, h.kind); buildIndex();
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
  function add(o, kind) {
    if (!cur) return; var id = newId();
    store.items[id] = { id: id, book: cur.book, ch: cur.ch, text: o.text, pre: o.pre, post: o.post, kind: kind === 'flag' ? 'flag' : 'hl', u: Date.now() };
    saveStore(); render(); schedule();
  }
  function removeId(id) {
    var h = store.items[id]; if (!h) return;
    store.items[id] = { id: id, del: 1, book: h.book, ch: h.ch, u: Date.now() };
    saveStore(); if (pageMode) page(); else render(); schedule();
  }


  /* ---------- "My highlights" page ---------- */
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
  function allItems() { return Object.keys(store.items).map(function (k) { return store.items[k]; }).filter(function (h) { return !h.del; }); }
  function page() {
    pageMode = true; cur = null;
    var items = allItems(), slugs = {}; items.forEach(function (h) { slugs[h.book] = 1; });
    var bs = BOOKS.filter(function (b) { return slugs[b.slug]; });
    Promise.all(bs.map(function (b) { return loadBook(b); })).then(function () { if (pageMode) draw(items, bs); });
  }
  function draw(items, bs) {
    doc.innerHTML = ''; doc.classList.remove('hlonly');
    doc.appendChild(el('h1', '', '★ My highlights'));
    var bar = el('div', 'hlctl'), sel = el('select'), inp = el('input'), cp = el('button', '', 'Copy all');
    sel.setAttribute('aria-label', 'Filter by book'); sel.appendChild(new Option('All books', ''));
    bs.forEach(function (b) { sel.appendChild(new Option(b.title, b.slug)); }); sel.value = fBook;
    inp.type = 'search'; inp.placeholder = 'Search highlights'; inp.value = fText; inp.setAttribute('aria-label', 'Search highlights');
    cp.type = 'button'; bar.appendChild(sel); bar.appendChild(inp); bar.appendChild(cp); doc.appendChild(bar);
    var count = el('p', 'hlstat'), list = el('div'); doc.appendChild(count); doc.appendChild(list);
    function visible() {
      var q = fText.trim().toLowerCase();
      return items.filter(function (h) { return (!fBook || h.book === fBook) && (!q || h.text.toLowerCase().indexOf(q) >= 0); });
    }
    function chTitle(b, id) { var c = (b.chapters || []).filter(function (x) { return x.id === id; })[0]; return c ? c.title : null; }
    function chOrder(b, id) { var i = (b.chapters || []).map(function (x) { return x.id; }).indexOf(id); return i < 0 ? 999 : i; }
    function paint() {
      var vis = visible(); list.innerHTML = '';
      count.textContent = vis.length ? vis.length + ' highlight' + (vis.length > 1 ? 's' : '') + (items.length !== vis.length ? ' (of ' + items.length + ')' : '') : '';
      if (!items.length) { list.appendChild(el('p', 'hlnone', 'No highlights yet. Select text in any chapter and tap Highlight.')); return; }
      if (!vis.length) { list.appendChild(el('p', 'hlnone', 'No highlights match.')); return; }
      bs.forEach(function (b) {
        var mine = vis.filter(function (h) { return h.book === b.slug; }); if (!mine.length) return;
        list.appendChild(el('h2', '', b.title));
        var chs = {}; mine.forEach(function (h) { (chs[h.ch] = chs[h.ch] || []).push(h); });
        Object.keys(chs).sort(function (x, y) { return chOrder(b, x) - chOrder(b, y); }).forEach(function (id) {
          var t = chTitle(b, id), hd = el('h3'), a = el('a', '', t ? t : (id === '_intro' ? b.title + ' (intro)' : id + ' (chapter not found)'));
          if (t || id === '_intro') a.href = '#' + b.slug + (id === '_intro' ? '' : '-' + id); hd.appendChild(a); list.appendChild(hd);
          chs[id].sort(function (x, y) { return x.u - y.u; }).forEach(function (h) {
            var row = el('div', 'hlitem' + (h.kind === 'flag' ? ' flag' : '')), q = el('blockquote', '', h.text), acts = el('div', 'hlacts');
            if (h.kind === 'flag') row.appendChild(el('span', 'hltag', '🔴 To revisit'));
            if (t || id === '_intro') { var o = el('a', 'hlopen', 'Open in chapter'); o.href = a.href; o.addEventListener('click', function () { focusId = h.id; }); acts.appendChild(o); }
            var rm = el('button', '', 'Remove'); rm.type = 'button'; rm.addEventListener('click', function () { removeId(h.id); }); acts.appendChild(rm);
            row.appendChild(q); row.appendChild(acts); list.appendChild(row);
          });
        });
      });
    }
    sel.addEventListener('change', function () { fBook = sel.value; paint(); });
    inp.addEventListener('input', function () { fText = inp.value; paint(); });
    cp.addEventListener('click', function () {
      var out = [], vis = visible();
      bs.forEach(function (b) {
        var mine = vis.filter(function (h) { return h.book === b.slug; }); if (!mine.length) return; out.push('## ' + b.title);
        var last = null; mine.sort(function (x, y) { return chOrder(b, x.ch) - chOrder(b, y.ch) || x.u - y.u; }).forEach(function (h) {
          if (h.ch !== last) { last = h.ch; out.push('### ' + (chTitle(b, h.ch) || h.ch)); } out.push('- ' + h.text.replace(/\s+/g, ' '));
        });
      });
      var txt = out.join('\n');
      function done() { cp.textContent = 'Copied ✓'; setTimeout(function () { cp.textContent = 'Copy all'; }, 1800); }
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, function () {});
      else { var ta = el('textarea'); ta.value = txt; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); done(); } catch (e) {} ta.remove(); }
    });
    paint(); document.getElementById('main').scrollTop = 0; updateUi();
  }

  /* ---------- bottom bar: Highlight / Revisit / Remove ---------- */
  var bar = document.createElement('div');
  bar.className = 'hlbar'; bar.hidden = true;
  var btnHl = document.createElement('button'); btnHl.type = 'button'; btnHl.className = 'hlbtn'; btnHl.textContent = '✎ Highlight';
  var btnFlag = document.createElement('button'); btnFlag.type = 'button'; btnFlag.className = 'hlbtn flagbtn'; btnFlag.textContent = '🔴 Revisit';
  var btnRm = document.createElement('button'); btnRm.type = 'button'; btnRm.className = 'hlbtn rmbtn'; btnRm.textContent = '✕ Remove';
  bar.appendChild(btnHl); bar.appendChild(btnFlag); bar.appendChild(btnRm); document.body.appendChild(bar);
  function showBar(mode) {
    barMode = mode;
    btnHl.hidden = mode !== 'add'; btnFlag.hidden = mode !== 'add'; btnRm.hidden = mode !== 'rm';
    if (mode === 'rm') { btnRm.textContent = '✕ Remove ' + (removeIds.length > 1 ? 'marks' : 'mark'); clearTimeout(barTimer); barTimer = setTimeout(hideBar, 7000); }
    bar.hidden = false;
  }
  function hideBar() { bar.hidden = true; barMode = null; pending = null; removeIds = []; clearTimeout(barTimer); }
  bar.addEventListener('pointerdown', function (e) { barTouch = true; e.preventDefault(); setTimeout(function () { barTouch = false; }, 600); });
  bar.addEventListener('mousedown', function (e) { e.preventDefault(); });
  function doAdd(kind) { if (pending) { add(pending, kind); var s = window.getSelection(); if (s) s.removeAllRanges(); } hideBar(); }
  btnHl.addEventListener('click', function () { doAdd('hl'); });
  btnFlag.addEventListener('click', function () { doAdd('flag'); });
  btnRm.addEventListener('click', function () { removeIds.forEach(removeId); hideBar(); });
  document.addEventListener('selectionchange', function () {
    clearTimeout(selTimer);
    selTimer = setTimeout(function () {
      if (barTouch) return;
      var sel = window.getSelection();
      if (sel && !sel.isCollapsed && sel.rangeCount && doc.contains(sel.anchorNode) && doc.contains(sel.focusNode)) {
        var r = sel.getRangeAt(0), hit = [];
        doc.querySelectorAll('mark.hl').forEach(function (m) {
          if (r.intersectsNode(m)) { var id = m.getAttribute('data-id'); if (hit.indexOf(id) < 0) hit.push(id); }
        });
        if (hit.length) { removeIds = hit; showBar('rm'); return; }
      }
      var o = readSelection();
      if (o) { pending = o; showBar('add'); }
      else if (barMode === 'add') hideBar();
    }, 140);
  });
  doc.addEventListener('click', function (e) {
    var m = e.target.closest && e.target.closest('mark.hl'); var s = window.getSelection();
    if (!m || (s && !s.isCollapsed)) { if (barMode === 'rm') hideBar(); return; }
    removeIds = []; for (var x = m; x && x !== doc; x = x.parentElement) if (x.tagName === 'MARK' && x.getAttribute('data-id')) removeIds.push(x.getAttribute('data-id'));
    showBar('rm');
  });

  /* ---------- chapter notes (free-text, per book+chapter) ---------- */
  function noteKey() { return cur ? cur.book + '-' + cur.ch : null; }
  function getNote() { var k = noteKey(); var n = k && store.notes[k]; return (n && !n.del) ? n.text : ''; }
  function setNote(text) {
    var k = noteKey(); if (!k) return;
    var prev = store.notes[k];
    if (!text && (!prev || !prev.text)) return;
    store.notes[k] = text ? { text: text, u: Date.now() } : { text: '', del: 1, u: Date.now() };
    saveStore(); updateUi(); schedule();
  }

  /* ---------- header buttons ---------- */
  var tbtn = document.getElementById('hlt'), sbtn = document.getElementById('hlset'), nbtn = document.getElementById('chnote');
  function updateUi() {
    tbtn.setAttribute('aria-pressed', only ? 'true' : 'false');
    tbtn.classList.toggle('on', only);
    sbtn.querySelector('.dot').className = 'dot ' + status;
    sbtn.title = statusText();
    var n = mine().length; tbtn.title = n ? n + ' highlight' + (n > 1 ? 's' : '') + ' on this page' : 'No highlights on this page';
    var inChapter = !!cur && !pageMode;
    nbtn.hidden = !inChapter;
    if (inChapter) {
      var has = !!getNote();
      nbtn.classList.toggle('on', has);
      nbtn.title = has ? 'This chapter has a note — click to view or edit' : 'Add a note for this chapter';
    }
  }
  tbtn.addEventListener('click', function () {
    only = !only; try { localStorage.setItem(LS_ONLY, only ? '1' : '0'); } catch (e) {}
    applyMode(); updateUi(); var m = document.getElementById('main'); if (m) m.scrollTop = 0;
  });
  sbtn.addEventListener('click', openPanel);
  nbtn.addEventListener('click', openNotePanel);

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
      if (r.status === 404) return { items: {}, notes: {}, sha: null };
      if (r.status === 401 || r.status === 403) throw new Error('GitHub rejected the token (' + r.status + '). It needs Contents read and write on ' + CFG.repo + '.');
      if (!r.ok) throw new Error('GitHub error ' + r.status);
      return r.json().then(function (j) { var d = {}; try { d = JSON.parse(b64d(j.content)); } catch (e) {} return { items: d.items || {}, notes: d.notes || {}, sha: j.sha }; });
    }).then(function (rem) {
      var mi = merge(store.items, rem.items), mn = merge(store.notes, rem.notes);
      if (mi.local || mn.local) {
        store.items = mi.items; store.notes = mn.items; saveStore();
        if (pageMode) page(); else render();
        updateUi();
      }
      if (!mi.remote && !mn.remote && rem.sha) return;
      var body = { message: 'Update highlights', content: b64e(JSON.stringify({ v: 1, items: mi.items, notes: mn.items })) };
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
    '<div class="hlrow"><button type="button" id="hlall">★ My highlights</button><button type="button" id="hlexp">Export</button><label class="hlfile">Import<input type="file" id="hlimp" accept="application/json" hidden></label></div>' +
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
  document.getElementById('hlall').addEventListener('click', function () { closePanel(); location.hash = 'highlights'; });
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
    var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify({ v: 1, items: store.items, notes: store.notes }, null, 1)], { type: 'application/json' }));
    a.download = 'notes-highlights.json'; document.body.appendChild(a); a.click(); a.remove();
  });
  document.getElementById('hlimp').addEventListener('change', function (e) {
    var f = e.target.files[0]; if (!f) return; var rd = new FileReader();
    rd.onload = function () {
      try {
        var d = JSON.parse(rd.result);
        var mi = merge(store.items, d.items || {}), mn = merge(store.notes, d.notes || {});
        store.items = mi.items; store.notes = mn.items; saveStore(); render(); updateUi(); schedule();
      } catch (x) { alert('That file is not a highlights export.'); }
    }; rd.readAsText(f); e.target.value = '';
  });

  /* ---------- chapter notes panel ---------- */
  var npanel = document.createElement('div');
  npanel.id = 'ntpanel'; npanel.hidden = true; npanel.setAttribute('role', 'dialog'); npanel.setAttribute('aria-label', 'Chapter notes');
  npanel.innerHTML =
    '<div class="hlcard"><div class="hlhead"><strong id="nttitle">Notes</strong><button type="button" id="ntclose" aria-label="Close">✕</button></div>' +
    '<p class="hlstat">Private notes for yourself about this chapter — what to fix, check, or revisit. Saved and synced the same way as highlights.</p>' +
    '<textarea id="nttext" placeholder="e.g. Section 2.3 needs a real code example; double-check the pricing claim in 1.4…"></textarea>' +
    '<p id="ntstat" class="hlstat"></p>' +
    '<div class="hlrow"><button type="button" id="ntclear">Clear note</button></div></div>';
  document.body.appendChild(npanel);
  var ntText = document.getElementById('nttext'), ntStat = document.getElementById('ntstat'), ntTimer = null;
  function openNotePanel() {
    if (!cur) return;
    var title = (allItems0Title() || cur.ch);
    document.getElementById('nttitle').textContent = 'Notes: ' + title;
    ntText.value = getNote();
    ntStat.textContent = ''; ntStat.className = 'hlstat';
    npanel.hidden = false; setTimeout(function () { ntText.focus(); }, 30);
  }
  function allItems0Title() {
    var b = cur && BOOKS.filter(function (x) { return x.slug === cur.book; })[0];
    var c = b && (b.chapters || []).filter(function (x) { return x.id === cur.ch; })[0];
    return c ? c.title : null;
  }
  function closeNotePanel() { npanel.hidden = true; }
  document.getElementById('ntclose').addEventListener('click', closeNotePanel);
  npanel.addEventListener('click', function (e) { if (e.target === npanel) closeNotePanel(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !npanel.hidden) closeNotePanel(); });
  ntText.addEventListener('input', function () {
    clearTimeout(ntTimer); ntStat.textContent = 'Saving…'; ntStat.className = 'hlstat';
    ntTimer = setTimeout(function () {
      setNote(ntText.value);
      ntStat.textContent = 'Saved ✓'; ntStat.className = 'hlstat ntsaved';
    }, 500);
  });
  document.getElementById('ntclear').addEventListener('click', function () {
    ntText.value = ''; setNote(''); ntStat.textContent = 'Cleared'; ntStat.className = 'hlstat';
  });

  window.HL = { apply: apply, sync: sync, render: render, page: page };
  setStatus(token() ? 'busy' : 'local');
  sync();
})();
