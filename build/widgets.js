/* Interactive widgets for the reader. A chapter writes ":::widget name" and this file builds it.
   Each widget is plain DOM, no libraries, and works with the page's colour variables. */
(function () {
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function btn(label, fn, cls) {
    var b = el('button', 'wbtn' + (cls ? ' ' + cls : ''), label);
    b.type = 'button';
    b.addEventListener('click', fn);
    return b;
  }
  function frame(root, title, hint) {
    root.textContent = '';
    root.classList.add('wlive');
    var h = el('div', 'whead');
    h.appendChild(el('strong', null, title));
    if (hint) h.appendChild(el('span', 'whint', hint));
    root.appendChild(h);
    var body = el('div', 'wbody');
    root.appendChild(body);
    return body;
  }
  function tabs(body, names, onPick) {
    var bar = el('div', 'wtabs'), btns = [];
    names.forEach(function (n, i) {
      var b = btn(n, function () { btns.forEach(function (x) { x.classList.remove('on'); }); b.classList.add('on'); onPick(i); }, 'wtab');
      btns.push(b); bar.appendChild(b);
    });
    body.appendChild(bar);
    btns[0].classList.add('on');
    return bar;
  }

  var W = {};

  /* ---------- MCP conversation simulator ---------- */
  var MCP_STEPS = [
    ['init', 'client', 'Step 1 · initialize request', 'Client speaks first: version, capabilities, identity.', { jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-11-25', capabilities: { roots: { listChanged: true } }, clientInfo: { name: 'RecipeBoxDesktopClient', version: '1.0.0' } } }],
    ['init', 'server', 'Step 2 · initialize response', 'Server answers with its own version, capabilities, identity.', { jsonrpc: '2.0', id: 1, result: { protocolVersion: '2025-11-25', capabilities: { tools: { listChanged: true } }, serverInfo: { name: 'RecipeBox', version: '1.0.0' } } }],
    ['init', 'client', 'Step 3 · initialized notification', 'No id: an announcement, not a question. Handshake sealed.', { jsonrpc: '2.0', method: 'notifications/initialized' }],
    ['operation', 'client', 'Discovery · tools/list', 'Fires automatically the instant the handshake completes.', { jsonrpc: '2.0', id: 2, method: 'tools/list' }],
    ['operation', 'server', 'Discovery response', 'The host quietly stores this for later matching.', { jsonrpc: '2.0', id: 2, result: { tools: [{ name: 'list_recipes', description: 'List every recipe' }, { name: 'get_recipe', description: "Get one recipe's detail" }, { name: 'search_recipes', description: 'Search by tag' }] } }],
    ['operation', 'client', 'tools/call · search_recipes', 'A real question finally arrives.', { jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'search_recipes', arguments: { tag: 'quick' } } }],
    ['operation', 'server', 'Tool call response', 'Placing the order, after reading the menu.', { jsonrpc: '2.0', id: 3, result: { content: [{ type: 'text', text: 'Weeknight Pasta, Five-Minute Salsa' }] } }],
    ['operation', 'client', 'A request for something never negotiated', 'The host asks for prompts anyway. This genuinely happens.', { jsonrpc: '2.0', id: 4, method: 'prompts/list' }],
    ['operation', 'server', 'Error · Method not found', "Not a crash, just an honest \"we don't have that\".", { jsonrpc: '2.0', id: 4, error: { code: -32601, message: 'Method not found' } }],
    ['operation', 'client', 'A long-running call, tagged for progress', 'A progressToken lets the server report back mid-task.', { jsonrpc: '2.0', id: 7, method: 'tools/call', params: { name: 'search_recipes', arguments: { tag: 'sunday' }, _meta: { progressToken: 'tok-7' } } }],
    ['operation', 'server', 'notifications/progress', 'No id: a status update, not a reply yet.', { jsonrpc: '2.0', method: 'notifications/progress', params: { progressToken: 'tok-7', progress: 60, total: 100, message: 'Searching 60 of 100 recipes' } }],
    ['operation', 'client', 'notifications/cancelled', 'A decision already made, announced, not a request for permission.', { jsonrpc: '2.0', method: 'notifications/cancelled', params: { requestId: '7', reason: 'Timeout exceeded (30s)' } }],
    ['operation', 'client', 'ping', 'Carries no information at all, just proves the line is open.', { jsonrpc: '2.0', id: 42, method: 'ping' }],
    ['operation', 'server', 'ping response', 'An empty result is the entire point.', { jsonrpc: '2.0', id: 42, result: {} }],
    ['shutdown', 'event', 'EVENT, not a JSON-RPC message', 'Shutdown has no message format of its own. The transport closing IS the goodbye.', null, 'Server transport closed { metadata: undefined }']
  ];
  W['mcp-sim'] = function (root) {
    var body = frame(root, 'MCP conversation simulator', 'press Play, or step one message at a time; tap a message to show or hide its JSON');
    var bar = el('div', 'wrow'), badge = el('span', 'wbadge', 'Initialization'), log = el('div', 'mlog');
    var idx = 0, timer = null, playBtn;
    var LBL = { init: 'Initialization', operation: 'Operation', shutdown: 'Shutdown' };
    function stepOnce() {
      if (idx >= MCP_STEPS.length) { pause(); return; }
      var s = MCP_STEPS[idx++], m = el('div', 'msg ' + s[1]);
      m.appendChild(el('div', 'mlbl', (s[1] === 'client' ? 'Client → Server' : s[1] === 'server' ? 'Server → Client' : 'Event') + ' · ' + s[2]));
      m.appendChild(el('div', 'mcap', s[3]));
      var pre = el('pre', 'mjson', s[4] ? JSON.stringify(s[4], null, 2) : s[5]);
      m.appendChild(pre);
      m.addEventListener('click', function () { pre.hidden = !pre.hidden; });
      Array.prototype.forEach.call(log.querySelectorAll('.mjson'), function (p) { p.hidden = true; });
      log.appendChild(m);
      badge.textContent = LBL[s[0]]; badge.className = 'wbadge ph-' + s[0];
      log.scrollTop = log.scrollHeight;
      if (idx >= MCP_STEPS.length) pause();
    }
    function play() { playBtn.textContent = 'Pause'; timer = setInterval(stepOnce, 1400); }
    function pause() { playBtn.textContent = 'Play'; clearInterval(timer); timer = null; }
    function reset() { pause(); idx = 0; log.textContent = ''; badge.textContent = 'Initialization'; badge.className = 'wbadge ph-init'; }
    playBtn = btn('Play', function () { timer ? pause() : play(); }, 'primary');
    bar.appendChild(playBtn); bar.appendChild(btn('Step', stepOnce)); bar.appendChild(btn('Reset', reset)); bar.appendChild(badge);
    body.appendChild(bar); body.appendChild(log);
  };

  /* ---------- Legacy vs modern MCP ---------- */
  W['legacy-modern'] = function (root) {
    var body = frame(root, 'Remember me, or tell me every time?', 'toggle the two models, then play the confirm-and-continue sequence');
    var view = el('div', 'wcard'), on = false;
    var texts = {
      legacy: ['Legacy: remember me', 'You shake hands once. The server keeps a session (the Mcp-Session-Id header), so one specific server remembers who you are. If that server is busy or gone, the next one knows nothing about you, which makes it hard to add more servers behind the scenes.'],
      modern: ['Modern: tell me every time', 'No handshake and no session id. Every request carries everything about itself (who is asking, which version, what is needed), so any server can handle any request. Slightly more data per request, but servers can be added freely.']
    };
    function paint() { var t = texts[on ? 'modern' : 'legacy']; view.textContent = ''; view.appendChild(el('strong', null, t[0])); view.appendChild(el('p', null, t[1])); }
    var sw = btn('Switch to modern', function () { on = !on; sw.textContent = on ? 'Switch to legacy' : 'Switch to modern'; paint(); }, 'primary');
    body.appendChild(sw); body.appendChild(view); paint();
    body.appendChild(el('div', 'wsub', 'Confirming and continuing (the OTP example)'));
    var seq = el('div', 'mlog'), STEPS = [
      ['client', 'You → Server', '"Confirm my order for 3 items."'],
      ['server', 'Server → You', 'Order total looks unusually high. Please enter the OTP sent to your phone. [+ a sealed order reference]'],
      ['client', 'You → Server', 'OTP: 482913 [+ the same sealed order reference]'],
      ['server', 'Server → You', 'Confirmed! Your order is on its way.']
    ], t = null, i = 0;
    function play() { clearInterval(t); seq.textContent = ''; i = 0; t = setInterval(function () { if (i >= STEPS.length) { clearInterval(t); return; } var s = STEPS[i++], m = el('div', 'msg ' + s[0]); m.appendChild(el('div', 'mlbl', s[1])); m.appendChild(el('div', 'mcap', s[2])); seq.appendChild(m); }, 1000); }
    var row = el('div', 'wrow'); row.appendChild(btn('Play the sequence', play)); row.appendChild(btn('Reset', function () { clearInterval(t); seq.textContent = ''; }));
    body.appendChild(row); body.appendChild(seq);
    body.appendChild(el('div', 'wnote', 'Because the sealed reference carries everything, the server that asked the question can go and do other work while it waits, and whichever server is free can pick up your answer.'));
  };

  /* ---------- Context window ---------- */
  function estTokens(t) { return Math.ceil(t.trim().split(/\s+/).length * 1.3); }
  W['ctx-window'] = function (root) {
    var body = frame(root, 'Context window simulator', 'messages are counted in rough tokens (words x 1.3); the oldest fall off when the window is full');
    var msgs = [{ r: 'user', t: 'Hi! My name is Rahul and I love football.' }, { r: 'assistant', t: "Nice to meet you Rahul! I'll remember that." }];
    var LIMIT = 120;
    var row = el('div', 'wrow'), lab = el('span', 'wlab'), sl = document.createElement('input');
    sl.type = 'range'; sl.min = 40; sl.max = 300; sl.value = LIMIT; sl.className = 'wslider';
    row.appendChild(el('span', null, 'Window size')); row.appendChild(sl); row.appendChild(lab);
    var barEl = el('div', 'cbar'), chat = el('div', 'mlog'), stat = el('div', 'wnote');
    var inp = document.createElement('input'); inp.type = 'text'; inp.className = 'winput'; inp.placeholder = 'Type a message...';
    var r2 = el('div', 'wrow');
    function add(r) { if (!inp.value.trim()) return; msgs.push({ r: r, t: inp.value }); inp.value = ''; paint(); }
    r2.appendChild(inp); r2.appendChild(btn('Send as user', function () { add('user'); }, 'primary')); r2.appendChild(btn('Send as AI', function () { add('assistant'); })); r2.appendChild(btn('Reset', function () { msgs = []; paint(); }));
    function paint() {
      lab.textContent = LIMIT + ' tokens'; chat.textContent = ''; barEl.textContent = '';
      var tot = 0, run = 0, keep = {};
      msgs.forEach(function (m) { m.k = estTokens(m.t); tot += m.k; });
      for (var i = msgs.length - 1; i >= 0; i--) { run += msgs[i].k; if (run <= LIMIT) keep[i] = 1; }
      msgs.forEach(function (m, i) {
        var d = el('div', 'msg ' + (m.r === 'user' ? 'client' : 'server') + (keep[i] ? '' : ' gone'));
        d.appendChild(el('div', 'mcap', m.t)); d.appendChild(el('div', 'mlbl', m.k + ' tokens' + (keep[i] ? '' : ' · forgotten')));
        chat.appendChild(d);
      });
      var blocks = Math.ceil(LIMIT / 5), fill = Math.ceil(tot / 5);
      for (var b = 0; b < blocks; b++) barEl.appendChild(el('i', b < fill ? 'f' : ''));
      var kept = Object.keys(keep).length;
      stat.textContent = 'Total ' + tot + ' tokens. The model still sees ' + kept + ' of ' + msgs.length + ' messages.';
      chat.scrollTop = chat.scrollHeight;
    }
    sl.addEventListener('input', function () { LIMIT = +sl.value; paint(); });
    inp.addEventListener('keydown', function (e) { if (e.key === 'Enter') add('user'); });
    body.appendChild(row); body.appendChild(barEl); body.appendChild(chat); body.appendChild(r2); body.appendChild(stat); paint();
  };

  W['ctx-memory'] = function (root) {
    var body = frame(root, 'Why the model "forgets", and how it hallucinates', 'save a fact, flood the window with noise, then ask');
    var LIMIT = 60, msgs = [], fact = '', longMem = [];
    var inp = document.createElement('input'); inp.type = 'text'; inp.className = 'winput'; inp.placeholder = 'e.g. My favourite city is Kyoto.';
    var status = el('div', 'wnote', 'No fact saved yet.'), ans = el('div', 'wcard', 'AI has no answer yet.');
    var lm = el('div', 'wnote'), mem = document.createElement('input'); mem.type = 'text'; mem.className = 'winput'; mem.placeholder = 'Save to long-term memory (kept even after overflow)';
    function inWindow() { var run = 0, ok = []; for (var i = msgs.length - 1; i >= 0; i--) { run += estTokens(msgs[i]); if (run <= LIMIT) ok.unshift(msgs[i]); } return ok; }
    function paint() { status.textContent = fact ? ('Fact saved: "' + fact + '". Messages now: ' + msgs.length + '. Still inside the window: ' + inWindow().length + '.') : 'No fact saved yet.'; lm.textContent = longMem.length ? 'Long-term memory: ' + longMem.join(' | ') : 'Long-term memory is empty.'; }
    var r1 = el('div', 'wrow');
    r1.appendChild(inp);
    r1.appendChild(btn('Save fact', function () { if (!inp.value.trim()) return; fact = inp.value.trim(); msgs.push(fact); inp.value = ''; paint(); }, 'primary'));
    r1.appendChild(btn('Flood the window', function () { for (var i = 0; i < 6; i++) msgs.push('Unrelated chatter message number ' + (msgs.length + 1) + ' about nothing important.'); paint(); }));
    r1.appendChild(btn('Ask: what was my fact?', function () {
      if (!fact) { ans.textContent = 'Save a fact first.'; return; }
      var known = inWindow().indexOf(fact) >= 0 || longMem.some(function (m) { return m === fact; });
      if (known) { ans.textContent = 'AI answers correctly: ' + fact; }
      else { var fake = ['I think it was Paris.', 'Maybe London?', 'Possibly New York.', 'Could be Singapore.']; ans.textContent = 'Hallucinated answer: ' + fake[Math.floor(Math.random() * fake.length)] + '  (the fact fell out of the window)'; }
    }));
    r1.appendChild(btn('Reset', function () { msgs = []; fact = ''; ans.textContent = 'AI has no answer yet.'; paint(); }));
    var r2 = el('div', 'wrow'); r2.appendChild(mem); r2.appendChild(btn('Save to long-term memory', function () { if (!mem.value.trim()) return; longMem.push(mem.value.trim()); mem.value = ''; paint(); }));
    body.appendChild(r1); body.appendChild(status); body.appendChild(ans); body.appendChild(r2); body.appendChild(lm);
    body.appendChild(el('div', 'wnote', 'Tip: save the same text to long-term memory as your fact, flood the window, and ask again. Long-term memory survives because it lives outside the window and is fed back in.'));
    paint();
  };

  /* ---------- Tokenizer illustration ---------- */
  W['tokenizer'] = function (root) {
    var body = frame(root, 'Tokens: puzzle pieces, not words', 'an illustration with a simple rule, not a real tokenizer');
    var inp = document.createElement('input'); inp.type = 'text'; inp.className = 'winput'; inp.value = 'unbelievable things happen';
    var out = el('div', 'tokrow'), stat = el('div', 'wnote');
    function piece(w) { if (w.length <= 5) return [w]; var parts = [], i = 0; while (i < w.length) { var n = Math.min(w.length - i, i === 0 ? 4 : 4); parts.push(w.substr(i, n)); i += n; } return parts; }
    function paint() {
      out.textContent = ''; var n = 0;
      inp.value.split(/(\s+)/).forEach(function (w) { if (!w) return; if (/^\s+$/.test(w)) return; piece(w).forEach(function (p) { n++; out.appendChild(el('span', 'tok', p)); }); });
      stat.textContent = n + ' tokens · ' + inp.value.length + ' characters. Short everyday words stay whole; long or unusual words are split, which is why they cost more.';
    }
    inp.addEventListener('input', paint);
    body.appendChild(inp); body.appendChild(out); body.appendChild(stat); paint();
  };

  /* ---------- Agent loop ---------- */
  W['agent-loop'] = function (root) {
    var body = frame(root, 'The agent loop', 'perceive, reason, act, observe, repeat until the goal is met');
    var names = ['1. Perceive', '2. Reason', '3. Act', '4. Observe'], notes = [
      'Read the goal and everything seen so far.',
      'Decide: can I answer now, or do I need a tool?',
      'Call the chosen tool (this is the model asking; your code runs it).',
      'Feed the tool result back into the message list.'
    ];
    var boxes = [], row = el('div', 'loopbox');
    names.forEach(function (n) { var b = el('div', 'lstep'); b.appendChild(el('strong', null, n)); row.appendChild(b); boxes.push(b); });
    var caption = el('div', 'wnote', 'Press Run to watch one goal go round the loop twice, then answer.'), t = null;
    function run() {
      clearInterval(t); var i = 0, lap = 0;
      t = setInterval(function () {
        boxes.forEach(function (b) { b.classList.remove('on'); });
        if (lap >= 2) { clearInterval(t); caption.textContent = 'No more tools needed: the model gives the final answer. The loop ended because the model stopped asking for tools.'; return; }
        boxes[i].classList.add('on'); caption.textContent = 'Lap ' + (lap + 1) + ' · ' + names[i] + ': ' + notes[i];
        i++; if (i === 4) { i = 0; lap++; }
      }, 900);
    }
    body.appendChild(row); body.appendChild(caption); body.appendChild(btn('Run', run, 'primary'));
  };

  /* ---------- Pydantic validation playground ---------- */
  W['pydantic-playground'] = function (root) {
    var body = frame(root, 'Live validation playground', 'a JavaScript imitation of the Pydantic rules below; edit the JSON or try a preset');
    var code = el('pre', 'wcode', 'class JobApplication(BaseModel):\n    full_name: str = Field(min_length=2, max_length=100)\n    email: EmailStr\n    years_experience: int = Field(ge=0, le=50)');
    var P = {
      'Valid data': '{\n  "full_name": "Aditi Sharma",\n  "email": "aditi@example.com",\n  "years_experience": "6"\n}',
      'Missing field': '{\n  "full_name": "Rohan Mehta"\n}',
      'Wrong types': '{\n  "full_name": "Meera Iyer",\n  "email": "not-an-email",\n  "years_experience": "a lot"\n}',
      'Out of range': '{\n  "full_name": "K",\n  "email": "karan@example.com",\n  "years_experience": 75\n}'
    };
    var ta = document.createElement('textarea'); ta.className = 'wtext'; ta.rows = 6; ta.value = P['Valid data'];
    var res = el('pre', 'wcode');
    var presets = el('div', 'wrow'); Object.keys(P).forEach(function (k) { presets.appendChild(btn(k, function () { ta.value = P[k]; res.textContent = ''; })); });
    function validate() {
      var t, errs = [];
      try { t = JSON.parse(ta.value); } catch (e) { res.textContent = 'Invalid JSON: check quotes, commas and brackets.'; return; }
      if (!('full_name' in t)) errs.push('full_name: Field required'); else if (typeof t.full_name !== 'string') errs.push('full_name: Input should be a valid string'); else if (t.full_name.length < 2) errs.push('full_name: String should have at least 2 characters'); else if (t.full_name.length > 100) errs.push('full_name: String should have at most 100 characters');
      if (!('email' in t)) errs.push('email: Field required'); else if (typeof t.email !== 'string') errs.push('email: Input should be a valid string'); else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(t.email)) errs.push('email: value is not a valid email address');
      var y = t.years_experience;
      if (!('years_experience' in t)) errs.push('years_experience: Field required');
      else {
        if (typeof y === 'string') { var n = Number(y); if (isFinite(n) && y.trim() !== '') y = n; else { errs.push('years_experience: Input should be a valid integer, unable to parse string as an integer'); y = undefined; } }
        if (y !== undefined) { if (typeof y !== 'number' || y % 1 !== 0) errs.push('years_experience: Input should be a valid integer'); else if (y < 0) errs.push('years_experience: Input should be greater than or equal to 0'); else if (y > 50) errs.push('years_experience: Input should be less than or equal to 50'); }
      }
      res.textContent = errs.length ? errs.length + ' validation error(s)\n' + errs.join('\n') : 'Valid. Note that the string "6" was coerced to the integer 6.';
    }
    body.appendChild(code); body.appendChild(presets); body.appendChild(ta); body.appendChild(btn('Validate', validate, 'primary')); body.appendChild(res);
  };

  /* ---------- Multi-agent patterns ---------- */
  W['agent-patterns'] = function (root) {
    var body = frame(root, 'Six multi-agent patterns, in a kitchen', 'pick a pattern, then press Run');
    var names = ['Chain', 'Parallel', 'Controller', 'Feedback loop', 'Hierarchical', 'Planner-Executor'];
    var stage = el('div', 'pstage'), cap = el('div', 'wnote'), controls = el('div', 'wrow'), cur = 0, timer = null;
    function nodes(list) { stage.textContent = ''; return list.map(function (l) { var n = el('div', 'pnode', l); stage.appendChild(n); return n; }); }
    function off(ns) { ns.forEach(function (n) { n.classList.remove('on', 'bad'); }); }
    function stop() { clearInterval(timer); }
    var info = [
      'Chain: agents run one after another and each output feeds the next. Best when the order is part of the job (draft, fact-check, format).',
      'Parallel: independent agents run at the same time and a merge step combines the results. Faster, but only if the pieces do not depend on each other. Anthropic reports its Research feature beats a single agent by over 90 percent on broad research, at about 15 times the token cost.',
      'Controller (router): one agent only decides who handles a request and hands it to exactly one specialist. It is often the cheapest agent in the system.',
      'Feedback loop: a second agent checks the first one\'s work and sends it back if it is not good enough, before anything goes out.',
      'Hierarchical: an orchestrator treats specialist agents as tools and combines their work ("agent as a tool"). This is the shape of Anthropic\'s multi-agent Research system.',
      'Planner-Executor: one agent only plans (a big vague goal into small steps), another only executes the list. The planner never executes and the executor never plans.'
    ];
    function setup(i) {
      stop(); cur = i; controls.textContent = ''; cap.textContent = info[i];
      var ns, run;
      if (i === 0) { ns = nodes(['Prep Cook', 'Sauce Station', 'Grill Station', 'Plating']); run = function () { off(ns); var k = 0; timer = setInterval(function () { off(ns); if (k >= ns.length) { stop(); return; } ns[k++].classList.add('on'); }, 800); }; }
      else if (i === 1) { ns = nodes(['Grill', 'Sauce', 'Vegetables', 'Garnish', 'Merge step']); run = function () { off(ns); ns.slice(0, 4).forEach(function (n) { n.classList.add('on'); }); setTimeout(function () { ns[4].classList.add('on'); }, 1000); }; }
      else if (i === 2) {
        var tickets = ['A rare ribeye, please.', 'Just the seasonal salad.', 'The chocolate tart for dessert.'], target = [1, 2, 3];
        ns = nodes(['Expediter (router)', 'Grill', 'Cold Station', 'Pastry']);
        tickets.forEach(function (t, j) { controls.appendChild(btn(t, function () { off(ns); ns[0].classList.add('on'); setTimeout(function () { ns[target[j]].classList.add('on'); }, 700); })); });
        run = null;
      }
      else if (i === 3) {
        ns = nodes(['Cook', 'Evaluator', 'Table']); var loopOn = true;
        controls.appendChild(btn('Feedback loop: ON (click to switch)', function () { loopOn = !loopOn; this.textContent = 'Feedback loop: ' + (loopOn ? 'ON' : 'OFF') + ' (click to switch)'; }));
        run = function () { off(ns); ns[0].classList.add('on'); setTimeout(function () { off(ns); ns[1].classList.add('on'); }, 700); setTimeout(function () { off(ns); if (loopOn) { ns[1].classList.add('bad'); cap.textContent = 'Undercooked: sent back to the cook for another pass, nothing left the kitchen.'; } else { ns[2].classList.add('bad'); cap.textContent = 'No check: the undercooked plate reached the table.'; } }, 1500); };
      }
      else if (i === 4) {
        ns = nodes(['Executive Chef (orchestrator)', 'Grill Chef', 'Pastry Chef', 'Sauce Chef']);
        ['Grill Chef', 'Pastry Chef', 'Sauce Chef'].forEach(function (s, j) { controls.appendChild(btn('Call ' + s, function () { off(ns); ns[0].classList.add('on'); setTimeout(function () { ns[j + 1].classList.add('on'); }, 500); })); });
        run = null;
      }
      else { ns = nodes(['Planner: Cook Sunday dinner', '1 Shop for ingredients', '2 Prep the vegetables', '3 Cook the mains', '4 Plate and garnish']); run = function () { off(ns); var k = 0; timer = setInterval(function () { off(ns); if (k >= ns.length) { stop(); return; } ns[k++].classList.add('on'); }, 800); }; }
      if (run) controls.appendChild(btn('Run', function () { stop(); run(); }, 'primary'));
    }
    tabs(body, names, setup); body.appendChild(stage); body.appendChild(controls); body.appendChild(cap); setup(0);
  };

  W['pattern-chooser'] = function (root) {
    var body = frame(root, 'Which pattern does your task need?', 'answer four questions (the recommendation rules are a simple reading of the guide, not an official algorithm)');
    var Q = [
      ['Do the steps have to happen in a strict order?', 'Chain of agents'],
      ['Could the pieces be worked on at the same time, independently?', 'Parallel agents'],
      ['Does it mainly need deciding who should handle it, not doing the work?', 'Controller (router) agent'],
      ['Does the output need a second check before it goes out?', 'Feedback loop (reactive agent)']
    ], ans = [null, null, null, null], out = el('div', 'wcard', 'Answer the questions above.');
    function paint() {
      var picks = []; Q.forEach(function (q, i) { if (ans[i]) picks.push(q[1]); });
      out.textContent = ans.every(function (a) { return a === null; }) ? 'Answer the questions above.' : (picks.length ? 'Start with: ' + picks.join(' + ') + '. Real systems often combine patterns, for example a hierarchical supervisor whose subagents are small chains, with a feedback loop around the riskiest step.' : 'None of the four apply, so start with a single agent. Add a pattern only when you hit its limits.');
    }
    Q.forEach(function (q, i) {
      var r = el('div', 'wrow'); r.appendChild(el('span', 'wq', q[0]));
      var y = btn('Yes', function () { ans[i] = true; y.classList.add('on'); n.classList.remove('on'); paint(); }), n = btn('No', function () { ans[i] = false; n.classList.add('on'); y.classList.remove('on'); paint(); });
      r.appendChild(y); r.appendChild(n); body.appendChild(r);
    });
    body.appendChild(out);
    body.appendChild(el('div', 'wnote', 'Start with the simplest pattern that fits, and add more only once you hit its limits.'));
  };

  window.__initWidgets = function (art) {
    Array.prototype.forEach.call(art.querySelectorAll('.widget[data-w]'), function (root) {
      if (root.getAttribute('data-ready')) return;
      var f = W[root.getAttribute('data-w')];
      if (!f) return;
      root.setAttribute('data-ready', '1');
      try { f(root); } catch (e) { root.setAttribute('data-ready', ''); }
    });
  };
})();
