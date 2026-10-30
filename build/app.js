(function () {
  var BOOKS = window.__BOOKS__;
  var book = BOOKS[0], chId = 'home';
  var store = {
    get: function (k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };
  var done = store.get('nb-done') || {};

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function readyOf(b) { return b.chapters.filter(function (c) { return c.ready; }); }

  /* hash <-> (book, chapter). Longest book id that prefixes the hash wins. */
  function parse(hash) {
    var best = null;
    BOOKS.forEach(function (b) { if (hash.indexOf(b.id + '-') === 0 && (!best || b.id.length > best.id.length)) best = b; });
    if (!best) return { book: BOOKS[0], ch: 'home' };
    var cid = hash.slice(best.id.length + 1);
    return { book: best, ch: readyOf(best).some(function (c) { return c.id === cid; }) ? cid : 'home' };
  }

  /* top bar: book name and switcher */
  function renderBrand() {
    $('#brand').textContent = book.title;
    var sel = $('#bookSel');
    if (BOOKS.length < 2) { sel.hidden = true; return; }
    sel.hidden = false;
    sel.innerHTML = BOOKS.map(function (b) { return '<option value="' + b.id + '"' + (b.id === book.id ? ' selected' : '') + '>' + esc(b.short) + '</option>'; }).join('');
  }
  $('#bookSel').addEventListener('change', function (e) { location.hash = e.target.value + '-home'; });

  /* sidebar */
  function renderNav() {
    var html = '', lastPart = null;
    book.chapters.forEach(function (c) {
      if (c.part !== lastPart) { html += '<div class="part">' + esc(c.part) + '</div>'; lastPart = c.part; }
      var key = book.id + '-' + c.id;
      var cls = 'navlink' + (c.ready ? '' : ' soon') + (done[key] ? ' done' : '') + (c.id === chId ? ' active' : '');
      html += '<button class="' + cls + '" data-id="' + key + '"' + (c.ready ? '' : ' disabled aria-disabled="true"') + '>' +
        '<span class="num">' + esc(c.num || '') + '</span><span>' + esc(c.title) + '</span>' +
        (c.ready ? '<span class="tick">&#10003;</span>' : '<span class="soon-tag">soon</span>') + '</button>';
    });
    $('#navlist').innerHTML = html;
    var chapters = readyOf(book).filter(function (c) { return ['home', 'quiz'].indexOf(c.id) < 0; });
    var n = chapters.filter(function (c) { return done[book.id + '-' + c.id]; }).length;
    $('#pcount').textContent = n + ' of ' + chapters.length + ' ready chapters read';
    $('#pbar').style.width = (chapters.length ? 100 * n / chapters.length : 0) + '%';
  }
  $('#navlist').addEventListener('click', function (e) {
    var b = e.target.closest('.navlink');
    if (b && !b.disabled) { go(b.getAttribute('data-id')); document.body.classList.remove('drawer'); }
  });

  /* routing */
  function go(id) { if (location.hash.slice(1) === id) show(id); else location.hash = id; }
  function show(hash) {
    var p = parse(hash); book = p.book; chId = p.ch;
    $$('article').forEach(function (a) { a.hidden = a.id !== 'ch-' + book.id + '-' + chId; });
    var art = $('#ch-' + book.id + '-' + chId);
    renderBrand(); renderNav(); buildToc(art);
    if (chId === 'quiz') startQuiz(art);
    window.scrollTo(0, 0);
    var h1 = $('h1', art).textContent;
    document.title = (chId === 'home' ? '' : h1 + ' | ') + book.title;
    var act = $('.navlink.active'); if (act && act.scrollIntoView) { try { act.scrollIntoView({ block: 'nearest' }); } catch (e) {} }
  }
  window.addEventListener('hashchange', function () { show(location.hash.slice(1)); });

  /* on this page (wide screens) and Jump to (phones) */
  var tocObserver = null;
  function buildToc(art) {
    var hs = $$('h2, h3', art);
    var side = '<h5>On this page</h5>', jump = '';
    hs.forEach(function (h) {
      var cls = h.tagName === 'H3' ? 'l3' : 'l2';
      var a = '<a href="#" class="' + cls + '" data-t="' + h.id + '">' + esc(h.textContent) + '</a>';
      side += a; jump += a;
    });
    $('#toc').innerHTML = hs.length ? side : '';
    var jl = $('.jl', art); if (jl) { jl.innerHTML = jump; var d = $('.jump', art); if (d) { d.open = false; d.hidden = !hs.length; } }
    if (tocObserver) tocObserver.disconnect();
    if ('IntersectionObserver' in window) {
      tocObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) $$('#toc a').forEach(function (a) { a.classList.toggle('on', a.getAttribute('data-t') === en.target.id); });
        });
      }, { rootMargin: '-70px 0px -70% 0px' });
      hs.forEach(function (h) { tocObserver.observe(h); });
    }
  }
  function jumpClick(e) {
    var a = e.target.closest('a[data-t]'); if (!a) return; e.preventDefault();
    var t = document.getElementById(a.getAttribute('data-t')); if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
    var d = a.closest('details'); if (d) d.open = false;
  }
  $('#toc').addEventListener('click', jumpClick);
  $('main').addEventListener('click', jumpClick);

  /* code: highlight + copy */
  function prepCode() {
    $$('pre code').forEach(function (c) {
      var pre = c.parentNode;
      if (pre.parentNode.classList.contains('diagram-src')) return;
      if (window.hljs) { try { window.hljs.highlightElement(c); } catch (e) {} }
      var b = document.createElement('button'); b.className = 'copy'; b.type = 'button'; b.textContent = 'Copy';
      b.addEventListener('click', function () {
        var ok = function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1400); };
        try { navigator.clipboard.writeText(c.textContent).then(ok, function () { b.textContent = 'Select and copy'; }); }
        catch (e) { b.textContent = 'Select and copy'; }
      });
      pre.appendChild(b);
    });
  }

  /* checklists */
  function prepTasks() {
    $$('article').forEach(function (art) {
      $$('input[type=checkbox]', art).forEach(function (cb, i) {
        var key = 'nb-chk-' + art.id + '-' + i;
        cb.checked = !!store.get(key);
        cb.addEventListener('change', function () { store.set(key, cb.checked); });
      });
    });
  }

  /* mark as read + pager */
  document.addEventListener('click', function (e) {
    var r = e.target.closest('.readbtn');
    if (r) {
      var id = r.getAttribute('data-id'); done[id] = !done[id]; store.set('nb-done', done);
      r.classList.toggle('on', !!done[id]); r.textContent = done[id] ? 'Marked as read' : 'Mark this chapter as read'; renderNav(); return;
    }
    var p = e.target.closest('.pager button'); if (p) go(p.getAttribute('data-id'));
  });

  /* quiz */
  function startQuiz(art) {
    var root = $('.quizroot', art), prefix = 'ch-' + book.id + '-';
    var items = [];
    $$('article').forEach(function (a) {
      if (a.id.indexOf(prefix) !== 0 || a.id === prefix + 'quiz') return;
      var cid = a.id.slice(prefix.length);
      var meta = book.chapters.filter(function (c) { return c.id === cid; })[0];
      $$('details.qa', a).forEach(function (d, i) {
        items.push({ qid: a.id + '#' + i, chapter: meta ? meta.title : cid, cid: cid, q: $('summary', d).innerHTML, a: $('.ans', d).innerHTML });
      });
    });
    var key = 'nb-quiz-' + book.id, mastered = store.get(key) || {}, filter = 'all', cur = null, shown = false;
    function pool() { return items.filter(function (it) { return (filter === 'all' || it.cid === filter) && !mastered[it.qid]; }); }
    function pick() { var p = pool(); cur = p.length ? p[Math.floor(Math.random() * p.length)] : null; shown = false; draw(); }
    function chapterOptions() {
      var seen = {}, html = '<option value="all">All chapters</option>';
      items.forEach(function (it) { if (!seen[it.cid]) { seen[it.cid] = 1; html += '<option value="' + it.cid + '"' + (filter === it.cid ? ' selected' : '') + '>' + esc(it.chapter) + '</option>'; } });
      return html;
    }
    function draw() {
      var total = items.length, got = items.filter(function (it) { return mastered[it.qid]; }).length;
      var h = '<div class="qstats"><b>' + got + ' of ' + total + '</b> questions mastered' +
        '<select id="qfilter" aria-label="Filter by chapter">' + chapterOptions() + '</select>' +
        '<button class="qlink" id="qreset" type="button">Reset</button></div>';
      if (!total) h += '<div class="qcard"><p>No questions yet. Chapters add them as they are written.</p></div>';
      else if (!cur) h += '<div class="qcard"><p><b>All done here.</b> Every question in this selection is marked as known. Reset to practise again.</p></div>';
      else {
        h += '<div class="qcard"><div class="qtag">' + esc(cur.chapter) + '</div><p class="qq">' + cur.q + '</p>';
        if (!shown) h += '<button class="qbtn primary" id="qshow" type="button">Show answer</button>';
        else h += '<div class="qans">' + cur.a + '</div><div class="qrow"><button class="qbtn primary" id="qgot" type="button">I knew it</button><button class="qbtn" id="qagain" type="button">Need more practice</button></div>';
        h += '</div>';
      }
      root.innerHTML = h;
      var f = $('#qfilter', root); if (f) f.addEventListener('change', function () { filter = f.value; pick(); });
      var s = $('#qshow', root); if (s) s.addEventListener('click', function () { shown = true; draw(); });
      var g = $('#qgot', root); if (g) g.addEventListener('click', function () { mastered[cur.qid] = 1; store.set(key, mastered); pick(); });
      var a = $('#qagain', root); if (a) a.addEventListener('click', pick);
      var r = $('#qreset', root); if (r) r.addEventListener('click', function () { mastered = {}; store.set(key, mastered); pick(); });
    }
    pick();
  }

  /* search (current book only) */
  var index = [];
  function buildIndex() {
    $$('article').forEach(function (art) {
      var found = BOOKS.filter(function (b) { return art.id.indexOf('ch-' + b.id + '-') === 0; }).sort(function (a, b) { return b.id.length - a.id.length; })[0];
      if (!found) return;
      var cid = art.id.slice(('ch-' + found.id + '-').length);
      if (cid === 'quiz') return;
      var c = found.chapters.filter(function (x) { return x.id === cid; })[0];
      var title = c ? c.title : cid;
      var sec = { book: found.id, id: found.id + '-' + cid, title: title, head: title, text: '' };
      Array.prototype.forEach.call(art.children, function (el) {
        if (el.tagName === 'H2' || el.tagName === 'H3') {
          index.push(sec); sec = { book: found.id, id: found.id + '-' + cid, title: title, head: el.textContent, text: '', anchor: el.id };
        } else { sec.text += ' ' + el.textContent; }
      });
      index.push(sec);
    });
  }
  var input = $('#q'), box = $('#results');
  input.addEventListener('input', function () {
    var q = input.value.trim().toLowerCase();
    if (q.length < 2) { box.classList.remove('open'); box.innerHTML = ''; return; }
    var hits = [];
    index.forEach(function (s) {
      if (s.book !== book.id) return;
      var h = (s.head + ' ' + s.text).toLowerCase();
      if (h.indexOf(q) >= 0) hits.push({ s: s, score: s.head.toLowerCase().indexOf(q) >= 0 ? 0 : 1 });
    });
    hits.sort(function (a, b) { return a.score - b.score; });
    var html = hits.slice(0, 8).map(function (h, n) {
      var full = (h.s.head + ' ' + h.s.text).replace(/\s+/g, ' ');
      var at = Math.max(0, full.toLowerCase().indexOf(q) - 40);
      return '<button class="result" data-n="' + n + '"><b>' + esc(h.s.title) + (h.s.anchor ? ' &rsaquo; ' + esc(h.s.head) : '') + '</b><small>' + esc(full.substr(at, 120)) + '</small></button>';
    }).join('');
    box.innerHTML = html || '<div class="noresult">Nothing found for "' + esc(q) + '"</div>';
    box.classList.add('open'); box._hits = hits;
  });
  box.addEventListener('click', function (e) {
    var b = e.target.closest('.result'); if (!b) return;
    var h = box._hits[+b.getAttribute('data-n')].s;
    box.classList.remove('open'); input.value = '';
    go(h.id);
    if (h.anchor) setTimeout(function () { var t = document.getElementById(h.anchor); if (t) t.scrollIntoView({ block: 'start' }); }, 60);
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.search')) box.classList.remove('open'); });

  /* mobile drawer */
  $('#menu').addEventListener('click', function () { document.body.classList.toggle('drawer'); });
  $('#scrim').addEventListener('click', function () { document.body.classList.remove('drawer'); });

  buildIndex(); prepCode(); prepTasks();
  $$('.readbtn').forEach(function (r) { var id = r.getAttribute('data-id'); if (done[id]) { r.classList.add('on'); r.textContent = 'Marked as read'; } });
  show(location.hash.slice(1));
})();
