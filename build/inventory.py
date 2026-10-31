#!/usr/bin/env python3
"""Builds COVERAGE_INVENTORY.md: every file in the course repo and every page of the LangChain, MCP and
Pydantic documentation, each with its status. Run: python3 -I build/inventory.py <course_repo_dir>"""
import json, os, re, subprocess, sys, glob, collections, datetime
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO=sys.argv[1]
D=os.path.join(ROOT,'build','inventory_data')
BOOKS=['foundations','pydantic','agentic-ai','rag']
LABEL={'read':'Read properly','skimmed':'Looked through','ignored':'Ignored (lock, log, config)','new':'NEW upstream: not read'}

# ---------- repo files ----------
led={b:json.load(open(f'{ROOT}/books/{b}/sources.json'))['files'] for b in BOOKS}
commit=json.load(open(f'{ROOT}/books/agentic-ai/sources.json'))['commit']
tracked=subprocess.run(['git','-C',REPO,'ls-files','-z'],capture_output=True,text=True).stdout.split('\0')
tracked=[t for t in tracked if t]
head=subprocess.run(['git','-C',REPO,'rev-parse','--short','HEAD'],capture_output=True,text=True).stdout.strip()
rows=[]
for p in tracked:
    st=None; cited=[]
    for b in BOOKS:
        e=led[b].get(p)
        if e:
            st=e['status']
            cited+= [f'{b}:{c}' for c in e.get('cited_in',[])]
    rows.append((p,st or 'new',cited))
by_top=collections.OrderedDict()
for p,st,c in sorted(rows):
    top=p.split('/')[0] if '/' in p else '(repo root)'
    by_top.setdefault(top,[]).append((p,st,c))

# ---------- chapters' URL citations ----------
text=''
for f in glob.glob(f'{ROOT}/books/*/chapters/*.md'): text+=open(f).read()+'\n'
def chapters_citing(pattern):
    out=set()
    for f in glob.glob(f'{ROOT}/books/*/chapters/*.md'):
        if re.search(pattern,open(f).read()): out.add(os.path.basename(os.path.dirname(os.path.dirname(f)))+':'+os.path.basename(f)[:-3])
    return sorted(out)

# ---------- LangChain docs ----------
ds=json.load(open(f'{ROOT}/books/agentic-ai/docs_sources.json'))
lc_read={'oss/python/langchain/'+x for x in ds['read_in_full']}
EXCL={'oss/python/langchain/ui','oss/python/langchain/deep-agent-from-scratch',
      'oss/python/langchain/multi-agent/subagents-personal-assistant','oss/python/langchain/multi-agent/handoffs-customer-support',
      'oss/python/langchain/multi-agent/router-knowledge-base','oss/python/langchain/multi-agent/skills-sql-assistant'}
RELEVANT_UNREAD={'oss/python/concepts/products','oss/python/concepts/providers-and-models','oss/python/concepts/memory','oss/python/concepts/context',
 'oss/python/concepts/human-in-the-loop','oss/python/migrate/langchain-v1','oss/python/migrate/langchain-mcp-adapters','oss/python/releases/langchain-v1',
 'oss/python/releases/changelog','oss/python/versioning','oss/python/common-errors','oss/python/langchain/get-help'}
def lc_status(path):
    if path in lc_read: return 'Read in full'
    if path.startswith('oss/python/langchain/frontend/') or path in EXCL: return 'Excluded by you'
    if path in RELEVANT_UNREAD: return 'NOT READ (relevant to the LangChain book)'
    if '/langgraph' in path or 'langgraph' in path.split('/')[-1]: return 'Not started (LangGraph lectures not begun)'
    if path.startswith(('oss/python/deepagents','langsmith/','oss/openwiki','build-overview')): return 'Other product (Deep Agents, Managed Deep Agents, OpenWiki)'
    return 'Reference or community (not planned)'
lc=[]
for line in open(f'{D}/langchain_docs.txt'):
    path,title=line.rstrip('\n').split('|',1)
    lc.append((path,title,lc_status(path)))
lc_sections=[('LangChain section: core, middleware, advanced, tutorials',lambda p:p.startswith('oss/python/langchain/')),
 ('Concepts, migration, releases and errors (LangChain-related)',lambda p:p in RELEVANT_UNREAD or p in ('oss/python/langgraph/case-studies','oss/python/releases/langgraph-v1','oss/python/migrate/langgraph-v1','oss/python/migrate/langgraph-supervisor','oss/python/reference/overview','oss/python/release-policy','oss/python/security-policy','use-these-docs','oss/python/learn')),
 ('LangGraph',lambda p:'langgraph' in p and not p.startswith('oss/python/migrate') and p not in ('oss/python/langgraph/case-studies','oss/python/releases/langgraph-v1')),
 ('Deep Agents, Managed Deep Agents, OpenWiki, Build overview',lambda p:p.startswith(('oss/python/deepagents','langsmith/','oss/openwiki','build-overview'))),
 ('Integrations',lambda p:p.startswith('oss/python/integrations')),
 ('Contributing',lambda p:p.startswith('oss/python/contributing'))]

# ---------- MCP docs ----------
mcp=[]
for line in open(f'{D}/mcp_docs.txt'):
    grp,title,url=line.rstrip('\n').split('|')
    st='Read in full' if url.endswith('getting-started/intro') else 'NOT READ'
    mcp.append((grp,title,url,st))

# ---------- Pydantic docs ----------
PYD_READ={'Alias','Configuration','Dataclasses','Fields','JSON Schema','Models','Performance tips','Settings Management','Serialization','Strict Mode','Type Adapter','Types','Unions','Validators'}
VERIFIED_URL=lambda slug: slug.startswith('concepts/') or slug in ('errors/errors','examples/pydantic_ai')
pyd=[]
for line in open(f'{D}/pydantic_docs.txt'):
    grp,title,slug=line.rstrip('\n').split('|')
    st='NOT READ'
    if grp=='Concepts' and title in PYD_READ: st='Read in full' if title!='Settings Management' else 'Read (about 96%)'
    if (grp,title) in (('Errors','Error Handling'),('Examples','Agent libraries (Pydantic AI)')): st='Read in full'
    if title=='Why use Pydantic Validation?': st='Probably read: the /get-started landing page I read has this section, not confirmed to be the same page'
    if grp in ('API reference','People'): st='NOT READ (reference; not planned unless you want it)'
    pyd.append((grp,title,slug,st))

# ---------- write ----------
L=[]
A=L.append
A('# Coverage inventory: every file and every documentation page\n')
A(f'Generated {datetime.date.today().isoformat()} by `build/inventory.py`. Course repo at `{head}` (the ledger was taken at `{commit}`). Nothing here is rounded or estimated: each row is one file or one page.\n')
A('**Status words.** *Read properly*: read start to finish. *Looked through*: parts read, or turned into text and scanned; the notes use its main points. *Ignored*: lock files, logs, config (not content). *NOT READ*: not opened. *Used in*: chapters that link to the file as a source (`book:chapter`); empty means no chapter links to it.\n')
# summary
cnt=collections.Counter(st for _,st,_ in rows)
A('## Summary\n')
A('| Source | Items | Read properly / in full | Looked through | Not read | Other |')
A('|---|---:|---:|---:|---:|---|')
A(f"| Course repo files (all {len(rows)} tracked) | {len(rows)} | {cnt['read']} | {cnt['skimmed']} | {cnt['new']} | {cnt['ignored']} ignored (lock, log, config) |")
lcc=collections.Counter(s for _,_,s in lc)
unread_rel=lcc['NOT READ (relevant to the LangChain book)']
lcsec=[x for x in lc if x[0].startswith('oss/python/langchain/')]
A(f"| LangChain docs: all {len(lc)} Python pages | {len(lc)} | {lcc['Read in full']} | 0 | {unread_rel} relevant, unread | {lcc['Excluded by you']} excluded by you; {lcc['Not started (LangGraph lectures not begun)']} LangGraph (not started); {lcc['Other product (Deep Agents, Managed Deep Agents, OpenWiki)']} other products; {lcc['Reference or community (not planned)']} reference/community |")
mc=collections.Counter(s for *_,s in mcp)
A(f"| MCP docs: {len(mcp)} pages (docs 26, specification 31, extensions 9, community 33, roadmap 1) | {len(mcp)} | {mc['Read in full']} | 0 | {mc['NOT READ']} | none excluded yet |")
pc=collections.Counter(s.split(' (')[0].split(':')[0] for *_,s in pyd)
pread=sum(1 for *_,s in pyd if s.startswith('Read'))
A(f"| Pydantic docs: {len(pyd)} pages | {len(pyd)} | {pread} | 0 | {sum(1 for *_,s in pyd if s=='NOT READ')} teaching pages unread | {sum(1 for *_,s in pyd if s.startswith('NOT READ (ref'))} API-reference/people pages not planned; 1 unconfirmed |")
A('')
A('One more upstream file appeared after the ledger was taken: `classes_transcription_summary/23 - 27 Sep - MCP In LangChain.md` (class 23, 286 lines). It is not read yet.\n')

A('### Repo files by folder\n')
A('| Folder | Files | Read properly | Looked through | Ignored | What is inside (sub-folders) |'); A('|---|---:|---:|---:|---:|---|')
for top,items in by_top.items():
    c=collections.Counter(st for _,st,_ in items)
    subs=sorted({x[0].split('/')[1] for x in items if x[0].count('/')>=2})
    A(f"| {top} | {len(items)} | {c['read']} | {c['skimmed']} | {c['ignored']} | {'; '.join(subs)[:230]} |")
A('')
A('Contents: [1 Repo files](#1-course-repo-files) · [2 LangChain docs](#2-langchain-documentation-all-234-python-pages) · [3 MCP docs](#3-mcp-documentation) · [4 Pydantic docs](#4-pydantic-documentation) · [5 Other material](#5-other-material-you-provided)\n')

A('## 1. Course repo files\n')
A(f'All {len(rows)} files tracked in `mayank953/Live-Class-2026`, grouped by top-level folder.\n')
for top,items in by_top.items():
    c=collections.Counter(st for _,st,_ in items)
    A(f"### {top} ({len(items)} files: {c['read']} read properly, {c['skimmed']} looked through, {c['ignored']} ignored{', '+str(c['new'])+' new' if c['new'] else ''})\n")
    A('| File | Status | Used in |'); A('|---|---|---|')
    for p,st,cited in items:
        short=p[len(top)+1:] if '/' in p else p
        A(f"| `{short}` | {LABEL[st]} | {', '.join(cited)} |")
    A('')

A('## 2. LangChain documentation, all 234 Python pages\n')
A('From the docs index (`docs.langchain.com/_llms/agent-development-lifecycle/build/python.txt`, fetched 31 Oct 2026). Paths are under `https://docs.langchain.com/`. The same page can appear under two products in the site menu (for example middleware), so it is listed once.\n')
used=set()
for name,fn in lc_sections:
    items=[x for x in lc if fn(x[0]) and x[0] not in used]
    for x in items: used.add(x[0])
    c=collections.Counter(s for _,_,s in items)
    A(f"### {name} ({len(items)} pages: {c['Read in full']} read)\n")
    A('| Page | Path | Status | Linked from |'); A('|---|---|---|---|')
    for path,title,st in items:
        cit=', '.join(chapters_citing(re.escape('docs.langchain.com/'+path)+r'(?![\w/-])'))
        A(f'| {title} | `{path}` | {st} | {cit} |')
    A('')
rest=[x for x in lc if x[0] not in used]
assert not rest, rest

A('## 3. MCP documentation\n')
A('From `modelcontextprotocol.io/llms.txt`, docs version **2026-07-28** (fetched 31 Oct 2026). The first two groups are the core; extensions and community are listed so nothing is hidden.\n')
for g in dict.fromkeys(x[0] for x in mcp):
    items=[x for x in mcp if x[0]==g]
    A(f"### {g} ({len(items)} pages: {sum(1 for x in items if x[3]=='Read in full')} read)\n")
    A('| Page | URL | Status | Linked from |'); A('|---|---|---|---|')
    for _,title,url,st in items:
        cit=', '.join(chapters_citing(re.escape(url.replace('https://',''))+r'(?![\w/-])'))
        A(f'| {title} | {url} | {st} | {cit} |')
    A('')

A('## 4. Pydantic documentation\n')
A('From `pydantic.dev/docs/validation/latest/llms.txt` (91 pages, fetched 31 Oct 2026). Links are shown only where I verified the address; the rest are listed by title.\n')
for g in dict.fromkeys(x[0] for x in pyd):
    items=[x for x in pyd if x[0]==g]
    A(f"### {g} ({len(items)} pages: {sum(1 for x in items if x[3].startswith('Read'))} read)\n")
    A('| Page | Status | Linked from |'); A('|---|---|---|')
    for _,title,slug,st in items:
        if VERIFIED_URL(slug):
            url='https://pydantic.dev/docs/validation/latest/'+slug
            cit=', '.join(chapters_citing(re.escape('pydantic.dev/docs/validation/')+r'(?:latest|dev)/'+re.escape(slug)+r'(?![\w/-])'))
            A(f'| [{title}]({url}) | {st} | {cit} |')
        else: A(f'| {title} | {st} | |')
    A('')
A('### Read from outside the 91 pages\n')
A('| Page | Status | Linked from |'); A('|---|---|---|')
for t,u in [('Pydantic article: LLM intro','https://pydantic.dev/articles/llm-intro'),('FastAPI: Request Body','https://fastapi.tiangolo.com/tutorial/body/'),('FastAPI: Response Model','https://fastapi.tiangolo.com/tutorial/response-model/'),('FastAPI: Extra Models','https://fastapi.tiangolo.com/tutorial/extra-models/'),('FastAPI: Body - Updates','https://fastapi.tiangolo.com/tutorial/body-updates/'),('FastAPI: Query Parameter Models','https://fastapi.tiangolo.com/tutorial/query-param-models/')]:
    A(f"| [{t}]({u}) | Read in full | {', '.join(chapters_citing(re.escape(u.replace('https://','').rstrip('/'))))} |")
A('')

A('## 5. Other material you provided\n')
A('Not repo files and not the three documentation sets, but part of what was given. Status is what I did with it.\n')
A('### 5a. Craft page attachments (22 PDFs, 4 notebooks, 1 diagram file, 10 Colabs, 5 videos)\n')
A('The earlier count of "40" was approximate; this is the full list from the page on 31 Oct 2026.\n')
A('| Item | Craft entry | Status |'); A('|---|---|---|')
craft=[
('AI_Industry_Handbook_2026_Latest.pdf','Home','Skipped on purpose (marked not for redistribution; business handout)'),
('Class-1---PythonAI.pdf','Class 1','Text extracted (repo copy)'),
('Agentic-3-0.pdf','Class 2','Text extracted (repo copy)'),
('Class-3-4.pdf','Classes 3 and 4','Text extracted (repo copy)'),
('Untitled-scene (3).pdf','12 July','Text extracted (repo copy under a similar name)'),
('Agentic-Python.pdf','12 July','Text extracted (repo copy)'),
('Langchain.pdf (22 MB)','18-19 July','Text extracted (repo copy)'),
('Langchain (2).pdf, Langchain (1).pdf (24 MB each)','25-26 July','Same name family as the repo copy; whether the files are byte-identical was not checked'),
('Langchain-2 (1).pdf, Langchain-2.pdf (1.3 MB each)','25-26 July','Text extracted (repo copy Langchain-2.pdf)'),
('Langchain-2 (2).pdf','1 Aug','Same name family as the repo copy; not checked byte for byte'),
('Runtime-HITL.pdf','22 Aug','Text extracted (repo copy)'),
('MCP-Lifecycle.pdf (1.4 MB)','MCP Starts','Text extracted (repo copy)'),
('MCP-Lifecycle.pdf (1.8 MB, second version)','MCP Starts','Read 31 Oct (not in the repo)'),
('Complete-MCP.pdf','MCP Starts','Text extracted (repo copy)'),
('MCP-Primitives.pdf','MCP Starts','Text extracted (repo copy)'),
('MCP-Server.pdf','MCP Starts','Read 31 Oct (not in the repo)'),
('MCP-Client.pdf','MCP Starts','Read 31 Oct (not in the repo)'),
('AI-Updater-Project.pdf','MCP Starts','Text extracted (repo copy)'),
('Xunova-JD-Senior-AI-Engineer.pdf','Job Opportunity','Skipped on purpose (job ad)'),
('Xunova-JD-Senior-Data-Scientist.pdf','Job Opportunity','Skipped on purpose (job ad)'),
('Revision_Parts_1-4.ipynb','25-26 July','Read from the repo copy'),
('Assignment_2_Agents_and_Prebuilt_Middleware.ipynb','16 Aug','Read from the repo copy'),
('Assignment_LangChain_Fundamentals_SOLUTIONS.ipynb','16 Aug','Read from the repo copy'),
('Runtime_and_HITL.ipynb','22 Aug','Read from the repo copy'),
('Runtime-HITL.excalidraw','22 Aug','NOT OPENED (its PDF export was read)'),
('Colab: Python Refresher and Pydantic','Class 2','Opened; compared with the repo notebook'),
('Colab: Pydantic From Scratch','Classes 3 and 4','Opened; compared with the repo notebook by title and opening cells'),
('Colab: Python and Agents','11 July','Opened and read'),
('Colab: verbose tool agent','12 July','Opened and read (contains a key; not copied)'),
('Colab: Langchain Collab (models, streaming)','18-19 July','Opened; compared with the repo notebook (contains keys; not copied)'),
('Colab: Langchain_Continue (CineBot)','25-26 July','Opened; compared with the repo notebook'),
('Colab: Student Reference, Structured Output and Tools','1 Aug','Opened; compared with the repo notebook'),
('Colab: Custom Middleware','16 Aug','Opened and read in full (no repo copy)'),
('Colab: Runtime and HITL','22 Aug','Opened; compared with the repo notebook'),
('Colab: MCP adapter notebook (Untitled2)','MCP Starts','Opened and read in full (no repo copy)'),
('Video: Class 1 setup (YouTube)','Class 1','NOT WATCHED'),
('Video: Class 1 second link (YouTube)','Class 1','NOT WATCHED'),
('Video: Class 2 (2:45 min)','Class 2','NOT WATCHED'),
('Video: Classes 3 and 4 (23:42 min)','Classes 3 and 4','NOT WATCHED'),
('Video: 25-26 July (20:12 min)','25-26 July','NOT WATCHED'),
]
for a,b,c in craft: A(f'| {a} | {b} | {c} |')
A('')
A('Other links on the Craft page: the "Mayank Doubt Solver" ChatGPT link (not opened), the GitHub repos (repo read; `patoles/agent-flow` README only), `x1xhlol/system-prompts-and-models-of-ai-tools` (not opened), Udemy, Mesh API and Kimi promotions (skipped on purpose), a local MCP Inspector link with a token in the URL (not opened; the token is not copied here).\n')
A('### 5b. Instructor sites\n')
A('| Site | Status |'); A('|---|---|')
for a,b in [('pydantic-with-mayank.netlify.app','Read in full'),('ai-terms-with-mayank.netlify.app','Read in full'),('context-with-mayank.netlify.app (4 tabs and script)','Read in full'),('python-agents-with-mayank.netlify.app','Read in full'),('mcp-lifecycle.netlify.app','Read in full'),('mcp-lifecycle-simulator.netlify.app','Read in full'),('mcp-legacy-vs-modern.netlify.app','Read in full'),('ai-automation-with-mayank.netlify.app: 7 guides (APIs; economics of subscription vs API; open source; MCP; RAG; production readiness; multi-agent)','Read in full'),('meridian-ai-course.netlify.app: modules 1 to 7 (about 500 slides)','Read in full (code boxes are not in the extracted text)'),('mini-contra.netlify.app','Opened: a small arcade-style game, not course material'),('resilient-marzipan-839ad0.netlify.app','Listed as "will not work" on Craft; not opened')]: A(f'| {a} | {b} |')
A('')
A('### 5c. Other repositories\n')
A('| Repo | Status |'); A('|---|---|')
A('| `mayank953/meridian-ai-learner` | README, code and a frontend digest read; the 17 backend tests were run; not every file read one by one |')
A('| `patoles/agent-flow` | README and folder layout only; source not read |')
A('')
open(f'{ROOT}/COVERAGE_INVENTORY.md','w').write('\n'.join(L))
print('ok',len(L))
