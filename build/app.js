(function () {
  var CH = window.__CHAPTERS__; // [{id,num,title,part,ready}]
  var ready = CH.filter(function (c) { return c.ready; });
  var current = null;
  var store = {
    get: function (k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };
  var done = store.get('a3-done') || {};

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  /* sidebar */
  function renderNav() {
    var html = '', lastPart = null;
    CH.forEach(function (c) {
      if (c.part !== lastPart) { html += '<div class="part">' + c.part + '</div>'; lastPart = c.part; }
      var cls = 'navlink' + (c.ready ? '' : ' soon') + (done[c.id] ? ' done' : '') + (c.id === current ? ' active' : '');
      html += '<button class="' + cls + '" data-id="' + c.id + '"' + (c.ready ? '' : ' disabled aria-disabled="true"') + '>' +
        '<span class="num">' + (c.num || '') + '</span><span>' + c.title + '</span>' +
        (c.ready ? '<span class="tick">&#10003;</span>' : '<span class="soon-tag">soon</span>') + '</button>';
    });
    $('#navlist').innerHTML = html;
    var total = ready.filter(function (c) { return c.id !== 'home'; }).length;
    var n = ready.filter(function (c) { return c.id !== 'home' && done[c.id]; }).length;
    $('#pcount').textContent = n + ' of ' + total + ' ready chapters read';
    $('#pbar').style.width = (total ? (100 * n / total) : 0) + '%';
  }
  $('#navlist').addEventListener('click', function (e) {
    var b = e.target.closest('.navlink');
    if (b && !b.disabled) { go(b.getAttribute('data-id')); document.body.classList.remove('drawer'); }
  });

  /* routing */
  function go(id) { if (location.hash.slice(1) === id) show(id); else location.hash = id; }
  function show(id) {
    if (!ready.some(function (c) { return c.id === id; })) id = 'home';
    current = id;
    $$('article').forEach(function (a) { a.hidden = a.id !== 'ch-' + id; });
    renderNav();
    var art = $('#ch-' + id);
    buildToc(art);
    window.scrollTo(0, 0);
    drawMermaid(art);
    document.title = (id === 'home' ? '' : $('h1', art).textContent + ' | ') + 'Agentic AI 3.0 Notes';
    var act = $('.navlink.active'); if (act && act.scrollIntoView) { try { act.scrollIntoView({ block: 'nearest' }); } catch (e) {} }
  }
  window.addEventListener('hashchange', function () { show(location.hash.slice(1) || 'home'); });

  /* on this page */
  var tocObserver = null;
  function buildToc(art) {
    var hs = $$('h2, h3', art);
    var html = '<h5>On this page</h5>';
    hs.forEach(function (h) { html += '<a href="#" class="' + (h.tagName === 'H3' ? 'l3' : 'l2') + '" data-t="' + h.id + '">' + h.textContent + '</a>'; });
    $('#toc').innerHTML = hs.length ? html : '';
    if (tocObserver) tocObserver.disconnect();
    if ('IntersectionObserver' in window) {
      tocObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            $$('#toc a').forEach(function (a) { a.classList.toggle('on', a.getAttribute('data-t') === en.target.id); });
          }
        });
      }, { rootMargin: '-70px 0px -70% 0px' });
      hs.forEach(function (h) { tocObserver.observe(h); });
    }
  }
  $('#toc').addEventListener('click', function (e) {
    var a = e.target.closest('a'); if (!a) return; e.preventDefault();
    var t = document.getElementById(a.getAttribute('data-t')); if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  /* code: highlight + copy */
  function prepCode() {
    $$('pre code').forEach(function (c) {
      var pre = c.parentNode;
      if (pre.classList.contains('mermaid')) return;
      if (window.hljs) { try { window.hljs.highlightElement(c); } catch (e) {} }
      var b = document.createElement('button'); b.className = 'copy'; b.type = 'button'; b.textContent = 'Copy';
      b.addEventListener('click', function () {
        var text = c.textContent;
        var ok = function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1400); };
        try { navigator.clipboard.writeText(text).then(ok, function () { b.textContent = 'Press and hold to select'; }); }
        catch (e) { b.textContent = 'Select and copy'; }
      });
      pre.appendChild(b);
    });
  }

  /* mermaid */
  var mermaidReady = false;
  function drawMermaid(art) {
    if (!window.mermaid) return;
    if (!mermaidReady) {
      var dark = document.documentElement.getAttribute('data-theme') === 'dark' ||
        (!document.documentElement.getAttribute('data-theme') && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
      try { window.mermaid.initialize({ startOnLoad: false, theme: dark ? 'dark' : 'neutral', flowchart: { useMaxWidth: true } }); mermaidReady = true; } catch (e) { return; }
    }
    var nodes = $$('pre.mermaid:not([data-processed])', art);
    if (nodes.length) { try { window.mermaid.run({ nodes: nodes }); } catch (e) {} }
  }
  window.addEventListener('load', function () { drawMermaid($('article:not([hidden])')); });

  /* checklists */
  function prepTasks() {
    $$('article').forEach(function (art) {
      $$('input[type=checkbox]', art).forEach(function (cb, i) {
        var key = 'a3-chk-' + art.id + '-' + i;
        cb.checked = !!store.get(key);
        cb.addEventListener('change', function () { store.set(key, cb.checked); });
      });
    });
  }

  /* mark as read + pager */
  document.addEventListener('click', function (e) {
    var r = e.target.closest('.readbtn');
    if (r) { var id = r.getAttribute('data-id'); done[id] = !done[id]; store.set('a3-done', done); r.classList.toggle('on', !!done[id]); r.textContent = done[id] ? 'Marked as read' : 'Mark this chapter as read'; renderNav(); return; }
    var p = e.target.closest('.pager button'); if (p) go(p.getAttribute('data-id'));
  });

  /* search */
  var index = [];
  function buildIndex() {
    $$('article').forEach(function (art) {
      var cid = art.id.slice(3);
      var c = CH.filter(function (x) { return x.id === cid; })[0];
      var title = c ? c.title : cid;
      var sec = { id: cid, title: title, head: title, text: '' };
      Array.prototype.forEach.call(art.children, function (el) {
        if (el.tagName === 'H2' || el.tagName === 'H3') {
          index.push(sec); sec = { id: cid, title: title, head: el.textContent, text: '', anchor: el.id };
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
      var h = (s.head + ' ' + s.text).toLowerCase(), i = h.indexOf(q);
      if (i >= 0) hits.push({ s: s, score: s.head.toLowerCase().indexOf(q) >= 0 ? 0 : 1, i: i });
    });
    hits.sort(function (a, b) { return a.score - b.score; });
    var html = hits.slice(0, 8).map(function (h, n) {
      var full = (h.s.head + ' ' + h.s.text).replace(/\s+/g, ' ');
      var at = Math.max(0, full.toLowerCase().indexOf(q) - 40);
      var snip = full.substr(at, 120).replace(/</g, '&lt;');
      return '<button class="result" data-n="' + n + '"><b>' + h.s.title + (h.s.anchor ? ' &rsaquo; ' + h.s.head : '') + '</b><small>' + snip + '</small></button>';
    }).join('');
    box.innerHTML = html || '<div class="noresult">Nothing found for "' + q.replace(/</g, '&lt;') + '"</div>';
    box.classList.add('open');
    box._hits = hits;
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

  buildIndex();
  prepCode();
  prepTasks();
  // restore read buttons
  $$('.readbtn').forEach(function (r) { var id = r.getAttribute('data-id'); if (done[id]) { r.classList.add('on'); r.textContent = 'Marked as read'; } });
  show(location.hash.slice(1) || 'home');
})();
