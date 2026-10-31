#!/usr/bin/env python3
"""Measures how much of each source item's concepts appear in the books.
Method (reproducible): take the item's distinctive terms (code identifiers, inline-code names, headings,
bold terms), drop terms that are generic for that source family, keep the 40 most distinctive, and check
which appear in the text of the books. Score = share found. Writes build/master_rows.json.
Usage: python3 -I build/master_analyze.py <course_repo_dir> <docsrc_dir>"""
import re, os, sys, json, glob, math, subprocess, collections, datetime
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO, DOCS = sys.argv[1], sys.argv[2]
BOOKS=['foundations','pydantic','agentic-ai','rag']

# ---------------- corpus ----------------
def stem(w):
    w=w.lower()
    for suf in ('ing','ed','es','s'):
        if len(w)>5 and w.endswith(suf): return w[:-len(suf)]
    return w
TOK=re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
chap_tokens={}   # 'book:chapter' -> set of stems
for b in BOOKS:
    for f in sorted(glob.glob(f'{ROOT}/books/{b}/chapters/*.md')):
        t=open(f).read()
        chap_tokens[f'{b}:{os.path.basename(f)[:-3]}']={stem(x) for x in TOK.findall(t)} | {x.lower() for x in TOK.findall(t)}
index=collections.defaultdict(set)
for ch,toks in chap_tokens.items():
    for x in toks: index[x].add(ch)

STOP=set('''about above after again against being below between both cannot could does doing down during each even every from further have having here herself himself into itself just more most never only other over same should since some such than that their theirs them then there these they this those through under until very were what when where which while will with would your yours yourself self true false none null import return print class def elif else pass lambda yield with from async await string number object array value values example examples note notes tip warning info default option options true false input output result results first second third following using used uses use make makes made also then here there what which they them like want need needs well work works working
python json http https www com org md mdx html css'''.split())

def codeish(x):
    return ('_' in x.strip('_')) or bool(re.search(r'[a-z][A-Z]',x)) or bool(re.search(r'\d',x)) or (x.isupper() and len(x)>=4) or (x[:1].isupper() and len(x)>=6 and re.search(r'[a-z][A-Z]|[A-Z][a-z]+[A-Z]',x) is not None)

def ids_from_code(code):
    out=set()
    for m in re.finditer(r'(?:def|class)\s+([A-Za-z_]\w+)',code): out.add(m.group(1))
    for m in re.finditer(r'from\s+[\w.]+\s+import\s+([\w, ]+)',code):
        for n in m.group(1).split(','): out.add(n.strip())
    for m in re.finditer(r'import\s+([\w.]+)',code): out.add(m.group(1).split('.')[0])
    for m in re.finditer(r'\b([A-Za-z_]\w{3,})\s*\(',code): out.add(m.group(1))
    for m in re.finditer(r'@([A-Za-z_][\w.]+)',code): out.add(m.group(1).split('.')[-1])
    for m in re.finditer(r'\b([A-Z][A-Z0-9_]{3,})\b',code): out.add(m.group(1))
    for m in re.finditer(r'\b([a-z]+_[a-z_0-9]+)\b',code): out.add(m.group(1))
    return out

def extract_md(text):
    """returns (title, description, term_counter)"""
    title=desc=''
    fm=re.match(r'---\n(.*?)\n---\n',text,re.S)
    if fm:
        m=re.search(r'^title:\s*(.*)$',fm.group(1),re.M); title=(m.group(1).strip(' "\'') if m else '')
        m=re.search(r'^description:\s*(.*)$',fm.group(1),re.M); desc=(m.group(1).strip(' "\'') if m else '')
        text=text[fm.end():]
    if not title:
        m=re.search(r'^#\s+(.*)$',text,re.M); title=m.group(1).strip() if m else ''
    # drop non-python code fences
    def keep(m):
        lang=(m.group(1) or '').lower()
        return m.group(0) if lang in ('','python','py','bash','sh','text','json','yaml','toml') else ''
    text2=re.sub(r'```([A-Za-z0-9_+-]*)[^\n]*\n.*?```',keep,text,flags=re.S)
    c=collections.Counter()
    for code in re.findall(r'```[^\n]*\n(.*?)```',text2,re.S):
        for i in ids_from_code(code):
            if codeish(i): c[i.lower()]+=1
    for inl in re.findall(r'`([^`\n]{2,60})`',text2):
        for x in TOK.findall(inl):
            if len(x)>=4 and codeish(x): c[x.lower()]+=1
    body=re.sub(r'```.*?```','',text2,flags=re.S)
    for h in re.findall(r'^#{2,4}\s+(.*)$',body,re.M):
        ws=tuple(sorted({stem(x) for x in re.findall(r'[A-Za-z]{5,}',h) if x.lower() not in STOP}))
        if len(ws)>=1: c['H:'+'|'.join(ws)]+=2
    return title,desc,c

def extract_code(text,ext):
    c=collections.Counter()
    for i in ids_from_code(text):
        if codeish(i): c[i.lower()]+=1
    return c

def read_text(path):
    ext=os.path.splitext(path)[1].lower()
    if ext in ('.png','.jpg','.jpeg','.gif','.svg','.ico','.webp','.mp4','.zip','.pyc'): return None
    if ext=='.pdf':
        r=subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True)
        return r.stdout
    if ext=='.ipynb':
        try: nb=json.load(open(path))
        except Exception: return None
        parts=[]
        for cell in nb.get('cells',[]):
            src=''.join(cell.get('source',[]))
            parts.append(src if cell.get('cell_type')=='markdown' else '```python\n'+src+'\n```')
        return '\n'.join(parts)
    try: return open(path,errors='ignore').read()
    except Exception: return None

# ---------------- idf per family ----------------
def build_idf(counters):
    df=collections.Counter()
    for c in counters:
        for t in c: df[t]+=1
    return df,len(counters)

def family_index(pred):
    chaps={k:v for k,v in chap_tokens.items() if pred(k)}
    idx=collections.defaultdict(set)
    for ch,toks in chaps.items():
        for x in toks: idx[x].add(ch)
    return chaps,idx
def score(counter,df,N,fam=None,generic_cut=0.30):
    chaps,idx=fam if fam else family_index(lambda k:True)
    cands=[]
    for t,tf in counter.items():
        if len(t)>60: continue
        if not t.startswith('H:') and (t in STOP or len(t)<4 or t.isdigit()): continue
        d=df.get(t,1)
        if d/N>generic_cut and N>20 and not t.startswith('H:'): continue
        cands.append((tf*math.log(1+N/d),t))
    cands.sort(reverse=True)
    terms=[t for _,t in cands[:40]]
    if not terms: return None,[],[],[]
    found=[];missing=[];chap=collections.Counter()
    for t in terms:
        if t.startswith('H:'):
            ws=t[2:].split('|'); best=0; bch=[]
            for ch,toks in chaps.items():
                r=sum(1 for w in ws if w in toks)/len(ws)
                if r>best: best=r
                if r>=0.7: bch.append(ch)
            ok=best>=0.7
            (found if ok else missing).append(t if ok else 'heading: '+' '.join(ws))
            for ch in bch: chap[ch]+=1
        else:
            hit=idx.get(t) or idx.get(stem(t))
            if hit:
                found.append(t)
                for ch in hit: chap[ch]+=1
            else: missing.append(t)
    top=[f'{ch} ({n})' for ch,n in chap.most_common(3) if n>=2]
    return len(found)/len(terms),terms,missing[:12],top

FAM={
 'all':family_index(lambda k:True),
 'mcp':family_index(lambda k:k.startswith('agentic-ai:ch1') and k.split('ch')[1].rstrip('a') in ('11','12','13','14','15','16','17','18')),
 'pydantic':family_index(lambda k:k.startswith('pydantic:')),
 'langchain':family_index(lambda k:k.startswith('agentic-ai:')),
 'rag':family_index(lambda k:k.startswith('rag:') or k=='agentic-ai:ch20'),
 'found':family_index(lambda k:k.startswith('foundations:') or k.startswith('pydantic:')),
}
rows=[]
def add(**kw): rows.append(kw)

# ---------------- repo files ----------------
led={b:json.load(open(f'{ROOT}/books/{b}/sources.json'))['files'] for b in BOOKS}
tracked=[x for x in subprocess.run(['git','-C',REPO,'ls-files','-z'],capture_output=True,text=True).stdout.split('\0') if x]
repo=[]
for p in tracked:
    st=None;cited=[]
    for b in BOOKS:
        e=led[b].get(p)
        if e:
            st=e['status']; cited+=[f'{b}:{c}' for c in e.get('cited_in',[])]
            reason=e.get('reason','')
    repo.append((p,st or 'new',cited))
rc={}
for p,st,cited in repo:
    if st=='ignored': continue
    txt=read_text(os.path.join(REPO,p))
    if txt is None: rc[p]=None; continue
    ext=os.path.splitext(p)[1].lower()
    if ext in ('.py','.js','.ts','.tsx','.jsx','.sh'): c=extract_code(txt,ext); title=''; desc=''
    else: title,desc,c=extract_md(txt)
    if ext in ('.py',):
        m=re.match(r'\s*(?:#.*\n)*\s*"""(.*?)"""',txt,re.S)
        desc=(m.group(1).strip().split('\n')[0][:140] if m else '')
    rc[p]=(title,desc,c,len(txt))
df_r,N_r=build_idf([v[2] for v in rc.values() if v])

def topic_of(p):
    pl=p.lower()
    if 'frontend' in pl: return 'Frontend (dropped by you)'
    if 'mcp' in pl: return 'MCP'
    if 'meridian' in pl: return 'Meridian / RAG'
    if 'pydantic' in pl: return 'Pydantic'
    if p.startswith('classes_'): return 'Class notes'
    if 'langchain' in pl or 'middleware' in pl or 'runtime' in pl or 'cinebot' in pl: return 'LangChain'
    if 'python' in pl or 'agent' in pl: return 'Foundations'
    return 'Repo (general)'
for p,st,cited in repo:
    sc=terms=miss=top=None
    topic=topic_of(p)
    if st=='ignored':
        cov='No teaching content'; why='lock file, log, config or archive'; score_v=None; concept=os.path.basename(p)
        miss=[];top=[]
    elif rc.get(p) is None:
        cov='No teaching content'; why='image or binary'; score_v=None; concept=os.path.basename(p); miss=[];top=[]
    elif 'frontend' in p.lower():
        cov='Excluded by you'; why='frontend material dropped by request'; score_v=None; concept=os.path.basename(p); miss=[];top=[]
    else:
        title,desc,c,ln=rc[p]
        fam={'MCP':'mcp','Pydantic':'pydantic','LangChain':'langchain','Meridian / RAG':'rag','Foundations':'found'}.get(topic,'all')
        score_v,terms,miss,top=score(c,df_r,N_r,FAM[fam])
        concept=(title or desc or os.path.basename(p))[:140]
        if score_v is None or len(terms)<5:
            cov='Covered' if cited else 'No teaching content'; why='too little text to measure'+('' if not cited else '; a chapter links to it'); score_v=None
        else:
            if score_v>=0.55 or (cited and score_v>=0.35): cov='Covered'
            elif score_v>=0.25 or cited: cov='Partly covered'
            else: cov='Not covered'
            why=''
    add(source='Course repo file',group=p.split('/')[0] if '/' in p else '(repo root)',item=p.split('/')[-1],path=p,concept=concept,
        read_status={'read':'Read properly','skimmed':'Looked through','ignored':'Ignored','new':'NOT READ','not_read':'NOT READ'}.get(st,'NOT READ'),
        coverage=cov,score=score_v,where=', '.join(top or []) or (', '.join(cited[:3]) if cited else ''),missing=', '.join(miss or []),
        linked=', '.join(cited),topic=topic,priority=('High' if p.startswith('classes_transcription') else 'Medium'),note=why)

# ---------------- docs pages ----------------
def doc_family(name,files):
    out={}
    for key,path in files:
        if not os.path.exists(path): out[key]=None; continue
        t=open(path,errors='ignore').read()
        out[key]=extract_md(t)
    return out
# LangChain
lc_read={'oss/python/langchain/'+x for x in json.load(open(f'{ROOT}/books/agentic-ai/docs_sources.json'))['read_in_full']}
EXCL={'oss/python/langchain/ui','oss/python/langchain/deep-agent-from-scratch','oss/python/langchain/multi-agent/subagents-personal-assistant','oss/python/langchain/multi-agent/handoffs-customer-support','oss/python/langchain/multi-agent/router-knowledge-base','oss/python/langchain/multi-agent/skills-sql-assistant'}
REL={'oss/python/concepts/products','oss/python/concepts/providers-and-models','oss/python/concepts/memory','oss/python/concepts/context','oss/python/concepts/human-in-the-loop','oss/python/migrate/langchain-v1','oss/python/migrate/langchain-mcp-adapters','oss/python/releases/langchain-v1','oss/python/releases/changelog','oss/python/versioning','oss/python/common-errors','oss/python/langchain/get-help'}
def lc_file(path):
    cands=[]
    rel=path.replace('oss/python/','')
    for base in (f'{DOCS}/langchain-ai-docs/src/oss/{rel}',f'{DOCS}/docs/src/oss/{rel}',f'{DOCS}/docs/src/oss/python/{rel}',f'{DOCS}/docs/src/oss/{rel}/index',f'{DOCS}/docs/src/oss/python/{rel}/index'):
        for ext in ('.mdx','.md'):
            if os.path.exists(base+ext): return base+ext
    if rel.endswith('/index'):
        for ext in ('.mdx',):
            b=f'{DOCS}/docs/src/oss/{rel[:-6]}'
            if os.path.exists(b+ext): return b+ext
    for sub in (rel, 'python/'+rel):
        b=f'{DOCS}/docs/src/oss/{sub}'
        for ext in ('.mdx','.md'):
            if os.path.exists(b+ext): return b+ext
    return None
lcrows=[]
for line in open(f'{ROOT}/build/inventory_data/langchain_docs.txt'):
    path,title=line.rstrip('\n').split('|',1)
    f=lc_file(path) if path.startswith('oss/') else None
    lcrows.append((path,title,f))
lc_ex={p:extract_md(open(f,errors='ignore').read()) for p,t,f in lcrows if f}
df_l,N_l=build_idf([v[2] for v in lc_ex.values()])
LC_NEWREAD={'oss/python/concepts/products','oss/python/concepts/providers-and-models','oss/python/concepts/memory','oss/python/concepts/context','oss/python/concepts/human-in-the-loop','oss/python/migrate/langchain-v1','oss/python/migrate/langchain-mcp-adapters','oss/python/releases/langchain-v1','oss/python/versioning','oss/python/common-errors'}
def lc_group(path):
    if path in LC_NEWREAD: return ('Read (text and tables; long code samples skimmed)','High','LangChain')
    if path in lc_read: return ('Read in full','High','LangChain')
    if path.startswith('oss/python/langchain/frontend/') or path in EXCL: return ('Excluded by you','Low','LangChain')
    if path in REL: return ('NOT READ','High','LangChain')
    if 'langgraph' in path: return ('NOT READ (LangGraph not started)','Low','LangGraph')
    if path.startswith(('oss/python/deepagents','langsmith/','oss/openwiki','build-overview')): return ('NOT READ (other product)','Low','Other product')
    return ('NOT READ (reference or community)','Low','Reference')
for path,title,f in lcrows:
    rs,prio,top_=lc_group(path)
    if f is None:
        add(source='LangChain docs',group=top_,item=title,path='docs.langchain.com/'+path,concept=title,read_status=rs,coverage='Not applicable' if prio=='Low' else 'Not measured',score=None,where='',missing='',linked='',topic='LangChain',priority=prio,note='source file not available for measurement' if prio!='Low' else 'outside the LangChain book')
        continue
    t,d,c=lc_ex[path]
    s,terms,miss,top=score(c,df_l,N_l,FAM['langchain'])
    if prio=='Low':
        cov='Excluded by you' if rs=='Excluded by you' else 'Not applicable'; why={'Excluded by you':'dropped by request','Not applicable':'outside the LangChain book (LangGraph / other product / reference)'}[cov]
    elif s is None: cov='No teaching content'; why='too little text to measure'
    else:
        cov='Covered' if s>=0.55 else ('Partly covered' if s>=0.25 else 'Not covered'); why=''
    add(source='LangChain docs',group=top_,item=title,path='docs.langchain.com/'+path,concept=(t or title)+((' - '+d) if d else ''),read_status=rs,coverage=cov,score=s,where=', '.join(top),missing=', '.join(miss),linked='',topic='LangChain',priority=prio,note=why)

# MCP
MCP_READ={'changelog':'Read in full','deprecated':'Read in full','server/discover':'Read in full','basic/patterns/cancellation':'Read in full','basic/patterns/progress':'Read in full',
 'basic/patterns/mrtr':'Read in part (to server requirements)','basic/versioning':'Read in part (compatibility matrix)','basic/patterns/subscriptions':'Read in part','basic/transports/stdio':'Read in part (backward compatibility)','basic/transports/streamable-http':'Read in part (headings and header rules)',
 'develop/connect-local-servers':'Headings and openings only','develop/connect-remote-servers':'Headings and openings only','develop/build-with-agent-skills':'Headings and openings only','develop/clients/client-best-practices':'Headings and openings only','sdk':'Headings and openings only',
 'tutorials/security/authorization':'Headings and openings only','tutorials/security/security_best_practices':'Headings and openings only','tutorials/security/local-server-security':'Headings and openings only'}
mcp=[]
for line in open(f'{ROOT}/build/inventory_data/mcp_docs.txt'):
    grp,title,url=line.rstrip('\n').split('|')
    mcp.append((grp,title,url))
def mcp_file(url):
    rel=url.replace('https://modelcontextprotocol.io/','')
    if rel.endswith('/index') or rel in ('specification/2026-07-28/index',):
        pass
    base=f'{DOCS}/modelcontextprotocol/docs/{rel}'
    for cand in (base+'.mdx',base+'.md',base+'/index.mdx',base.replace('/index','')+'.mdx'):
        if os.path.exists(cand): return cand
    return None
mex={}
for g,t,u in mcp:
    f=mcp_file(u)
    if f: mex[u]=extract_md(open(f,errors='ignore').read())
df_m,N_m=build_idf([v[2] for v in mex.values()])
for g,t,u in mcp:
    core=g.startswith(('Docs','Specification'))
    prio='High' if core else ('Medium' if g.startswith('Extensions') else 'Low')
    rs='Read in full' if u.endswith('getting-started/intro') else MCP_READ.get(u.split('2026-07-28/',1)[-1],'NOT READ')
    if u not in mex:
        add(source='MCP docs',group=g,item=t,path=u.replace('https://',''),concept=t,read_status=rs,coverage='Not measured',score=None,where='',missing='',linked='',topic='MCP',priority=prio,note='source file not found');continue
    tt,d,c=mex[u]
    s,terms,miss,top=score(c,df_m,N_m,FAM['mcp'])
    if s is None: cov='No teaching content'; why='too little text'
    else: cov='Covered' if s>=0.55 else ('Partly covered' if s>=0.25 else 'Not covered'); why=''
    add(source='MCP docs',group=g,item=t,path=u.replace('https://',''),concept=(tt or t)+((' - '+d) if d else ''),read_status=rs,coverage=cov,score=s,where=', '.join(top),missing=', '.join(miss),linked='',topic='MCP',priority=prio,note=why)

# Pydantic
import yaml
nav=open(f'{DOCS}/pydantic/mkdocs.yml').read()
pyd=[]
cur=None
for line in nav[nav.index('\nnav:'):].split('\n')[2:]:
    if re.match(r'^\S',line) and not line.startswith(' '): break
    m=re.match(r'^  - ([^:]+):\s*$',line)
    if m: cur=m.group(1); continue
    m=re.match(r'^\s+- ([^:]+):\s*(\S+\.md)\s*$',line)
    if m: pyd.append((cur,m.group(1).strip(),m.group(2)))
PYD_NEW={'concepts/json.md':'Read (text; code skimmed)','concepts/forward_annotations.md':'Read (text; code skimmed)','concepts/validation_decorator.md':'Read (text; code skimmed)','concepts/experimental.md':'Read in part','get-started/migration.md':'Read in part','concepts/conversion_table.md':'Not readable (generated table)'}
PYD_READ={'concepts/alias.md','concepts/config.md','concepts/dataclasses.md','concepts/fields.md','concepts/json_schema.md','concepts/models.md','concepts/performance.md','concepts/pydantic_settings.md','concepts/serialization.md','concepts/strict_mode.md','concepts/type_adapter.md','concepts/types.md','concepts/unions.md','concepts/validators.md','errors/errors.md','examples/pydantic_ai.md'}
pex={}
for g,t,p in pyd:
    f=f'{DOCS}/pydantic/docs/{p}'
    if os.path.exists(f): pex[p]=extract_md(open(f,errors='ignore').read())
df_p,N_p=build_idf([v[2] for v in pex.values() if not v is None])
for g,t,p in pyd:
    api=g.startswith(('API','Pydantic','Pydantic Core','Pydantic Settings','Pydantic Extra')) or p.startswith('api/')
    prio='Low' if (api or p=='pydantic_people.md') else ('High' if p.startswith('concepts/') else 'Medium')
    rs='Read in full' if p in PYD_READ else ('Probably read' if p=='why.md' else ('NOT READ (reference)' if api else 'NOT READ'))
    if p=='concepts/pydantic_settings.md': rs='Read (about 96%)'
    if p in PYD_NEW: rs=PYD_NEW[p]
    if p not in pex:
        add(source='Pydantic docs',group=g,item=t,path='pydantic.dev/docs/validation/latest/'+p,concept=t,read_status=rs,coverage='Not measured',score=None,where='',missing='',linked='',topic='Pydantic',priority=prio,note='source file not found');continue
    tt,d,c=pex[p]
    s,terms,miss,top=score(c,df_p,N_p,FAM['pydantic'])
    if api: cov='Not applicable'; why='generated API reference'
    elif s is None: cov='No teaching content'; why='too little text'
    else: cov='Covered' if s>=0.55 else ('Partly covered' if s>=0.25 else 'Not covered'); why=''
    add(source='Pydantic docs',group=g,item=t,path='pydantic.dev/docs/validation/latest/'+p,concept=(tt or t)+((' - '+d) if d else ''),read_status=rs,coverage=cov,score=s,where=', '.join(top),missing=', '.join(miss),linked='',topic='Pydantic',priority=prio,note=why)


# ---------------- Meridian slide chapters ----------------
mrows=[]
for line in open(f'{ROOT}/build/inventory_data/meridian_chapters.txt'):
    mod,ch,title,slides,terms=line.rstrip('\n').split('|')
    c=collections.Counter({t:1 for t in terms.split() if t})
    # chapter title as a heading unit
    ws=tuple(sorted({stem(x) for x in re.findall(r'[A-Za-z]{5,}',title) if x.lower() not in STOP}))
    if ws: c['H:'+'|'.join(ws)]+=2
    mrows.append((int(mod),int(ch),title,int(slides),c))
df_me,N_me=build_idf([m[4] for m in mrows])
for mod,ch,title,slides,c in mrows:
    s_,terms,miss,top=score(c,df_me,N_me,FAM['rag'],generic_cut=0.9)
    if ch==33: cov='Excluded by you'; why='frontend dropped by request (summarised in one page of chapter 20)'
    elif s_ is None or len(terms)<2: cov='Covered' if ch<=3 else 'No teaching content'; why='story chapter, no code terms'
    else: cov='Covered' if s_>=0.55 else ('Partly covered' if s_>=0.25 else 'Not covered'); why=''
    add(source='Meridian slides',group=f'Module {mod}',item=f'Chapter {ch}: {title}',path=f'meridian-ai-course.netlify.app/module-{mod}',concept=f'{title} ({slides} slides)',read_status='Read in full',coverage=cov,score=s_,where=', '.join(top),missing=', '.join(miss),linked='',topic='Meridian / RAG' if mod in (1,2,3,4) else ('LangChain' if mod==5 else 'Meridian / RAG'),priority='Medium',note=why)

json.dump(rows,open(f'{ROOT}/build/master_rows.json','w'),indent=0,ensure_ascii=False)
cnt=collections.Counter((r['source'],r['coverage']) for r in rows)
for k,v in sorted(cnt.items()): print(k,v)
print(len(rows))
