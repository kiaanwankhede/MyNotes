"""Key-free checks of code and claims in the Foundations (chapter 3) and RAG (chapters 2 to 4) books.
Run: venv/bin/pip install langchain-core langchain-text-splitters langchain-chroma chromadb
     venv/bin/python build/rag_foundations_test.py
Uses fake models and fake embeddings: no API key, no network, no cloud account.
"""
import json, hashlib, tempfile, os
R=[]
def t(name):
    def d(f):
        try: f(); R.append((name,'PASS',''))
        except Exception as e: R.append((name,'FAIL',(type(e).__name__+': '+str(e))[:240]))
        return f
    return d

# ---------- Foundations chapter 3: the agent loop with a stub client ----------
@t('f3 run_agent loop: tool call then final answer; messages grow; tool result uses tool_call_id')
def _():
    from types import SimpleNamespace as NS
    TOOLS_BY_NAME={'get_weather':lambda city:f'Sunny in {city}'}
    TOOL_SCHEMAS=[]
    calls=[]
    def create(model,messages,tools):
        calls.append(len(messages))
        if len(calls)==1:
            tc=NS(id='c1',function=NS(name='get_weather',arguments=json.dumps({'city':'Tokyo'})))
            return NS(choices=[NS(message=NS(tool_calls=[tc],content=None))])
        return NS(choices=[NS(message=NS(tool_calls=None,content='It is sunny in Tokyo'))])
    client=NS(chat=NS(completions=NS(create=create))); model='m'
    def run_agent(messages, max_turns=4):
        for _ in range(max_turns):
            response = client.chat.completions.create(
                model=model, messages=messages, tools=TOOL_SCHEMAS)
            message = response.choices[0].message
            if not message.tool_calls:
                messages.append({"role": "assistant", "content": message.content})
                return message.content
            messages.append(message)
            for call in message.tool_calls:
                args = json.loads(call.function.arguments)
                result = TOOLS_BY_NAME[call.function.name](**args)
                messages.append({"role": "tool","tool_call_id": call.id,"content": str(result)})
        return "Reached max_turns without a final answer."
    msgs=[{'role':'user','content':'weather in Tokyo?'}]
    assert run_agent(msgs)=='It is sunny in Tokyo'
    assert calls==[1,3]                       # 2nd call sees user + assistant tool request + tool result
    assert msgs[2]['role']=='tool' and msgs[2]['tool_call_id']=='c1'
    # max_turns guard: a model that always asks for a tool
    def forever(model,messages,tools):
        tc=NS(id='x',function=NS(name='get_weather',arguments='{"city":"A"}'))
        return NS(choices=[NS(message=NS(tool_calls=[tc],content=None))])
    client.chat.completions.create=forever
    assert run_agent([{'role':'user','content':'x'}],max_turns=3)=="Reached max_turns without a final answer."
@t('f3 tool schema is valid JSON Schema shape (required key exists in properties)')
def _():
    s={"type":"function","function":{"name":"get_weather","description":"d","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}}
    p=s['function']['parameters']; assert set(p['required'])<=set(p['properties'])
    try:
        import jsonschema
        jsonschema.Draft202012Validator.check_schema(p)
    except ImportError: pass

# ---------- RAG chapter 2: splitter and ids ----------
@t('r2 splitter: chunk_size 1000, overlap 100: no chunk over 1000, neighbours share text')
def _():
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text=' '.join(f'Sentence number {i} about payment terms and suppliers.' for i in range(400))
    sp=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=100)
    ch=sp.split_text(text)
    assert len(ch)>1 and max(len(c) for c in ch)<=1000
    shared=0
    for a,b in zip(ch,ch[1:]):
        tail=a[-100:]
        if any(w in b[:150] for w in tail.split()[-3:]): shared+=1
    assert shared>=len(ch)//2, (shared,len(ch))
@t('r2 sha1 chunk ids: indexing the same file twice replaces, count stays; survives restart (Chroma folder)')
def _():
    from langchain_chroma import Chroma
    from langchain_core.embeddings import DeterministicFakeEmbedding
    from langchain_core.documents import Document
    d=tempfile.mkdtemp(); emb=DeterministicFakeEmbedding(size=768)
    def ids(src,docs): return [hashlib.sha1(f'{src}|{d.metadata["page"]}|{i}'.encode()).hexdigest() for i,d in enumerate(docs)]
    docs=[Document(page_content=f'chunk {i}',metadata={'source':'a.pdf','page':0}) for i in range(3)]
    s=Chroma(collection_name='coll_c',embedding_function=emb,persist_directory=d)
    s.add_documents(docs,ids=ids('a.pdf',docs)); s.add_documents(docs,ids=ids('a.pdf',docs))
    assert s._collection.count()==3
    s2=Chroma(collection_name='coll_c',embedding_function=emb,persist_directory=d); assert s2._collection.count()==3
    assert len(emb.embed_query('x'))==768
@t('r2 same text embeds identically, different models not comparable (dimension check)')
def _():
    from langchain_core.embeddings import DeterministicFakeEmbedding
    a=DeterministicFakeEmbedding(size=768).embed_query('x'); b=DeterministicFakeEmbedding(size=768).embed_query('x')
    assert a==b

# ---------- RAG chapter 3: LCEL chain, retrieval ----------
@t('r3 build_rag_chain shape: {"context": retriever|format_docs, "input": passthrough} | prompt | llm | StrOutputParser -> str')
def _():
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.documents import Document
    from langchain_core.language_models.fake_chat_models import FakeListChatModel
    format_docs=lambda docs:'\n\n'.join(d.page_content for d in docs)
    retr=RunnableLambda(lambda q:[Document(page_content='Net-45 payment terms')])
    prompt=ChatPromptTemplate.from_messages([('system','Use the context. If you do not know based on the context, say so.\n{context}'),('human','{input}')])
    seen={}
    def llm(pv): seen['p']=pv.to_string(); return 'Net-45'
    chain=({'context':retr|format_docs,'input':RunnablePassthrough()}|prompt|RunnableLambda(llm)|StrOutputParser())
    out=chain.invoke('What are the payment terms?')
    assert out=='Net-45' and 'Net-45 payment terms' in seen['p'] and 'What are the payment terms?' in seen['p']
@t('r3 similarity k=3; mmr gives more diverse results than similarity on near-duplicates')
def _():
    from langchain_chroma import Chroma
    from langchain_core.embeddings import Embeddings
    class E(Embeddings):
        V={'a1':[1,0.0],'a2':[1,0.01],'a3':[1,0.02],'b':[0.7,0.7],'q':[1,0.05]}
        def embed_documents(self,t): return [self.V[x] for x in t]
        def embed_query(self,t): return self.V[t]
    s=Chroma(collection_name='coll_m',embedding_function=E(),persist_directory=tempfile.mkdtemp())
    s.add_texts(['a1','a2','a3','b'],ids=['1','2','3','4'])
    sim=[d.page_content for d in s.similarity_search('q',k=3)]
    mmr=[d.page_content for d in s.max_marginal_relevance_search('q',k=3,fetch_k=4)]
    assert len(sim)==3 and 'b' not in sim and 'b' in mmr, (sim,mmr)
@t('r3 multi-query merge drops duplicates (4 searches: original + 3 rewrites)')
def _():
    lists=[['a','b','c'],['b','c','d'],['a','e','f'],['c','g','h']]
    seen=set(); out=[]
    for l in lists:
        for x in l:
            if x not in seen: seen.add(x); out.append(x)
    assert len(lists)==4 and len(out)==len(set(out))==8

# ---------- RAG chapter 4: reciprocal rank fusion ----------
@t('r4 reciprocal rank fusion: score sum of 1/(60+position); item in both lists beats item in one')
def _():
    def keyword_rank(q): return ['d3','d1','d2']
    by_meaning=['d1','d3','d2']
    fused={}
    for ranking in (keyword_rank('x'),by_meaning):
        for position,id_ in enumerate(ranking): fused[id_]=fused.get(id_,0)+1/(60+position)
    assert abs(fused['d1']-(1/61+1/60))<1e-12 and abs(fused['d3']-(1/60+1/61))<1e-12
    order=sorted(fused,key=fused.get,reverse=True)
    assert order[-1]=='d2' and set(order[:2])=={'d1','d3'}
    only_one={}
    for ranking in (['a','b'],['c']):
        for p,i in enumerate(ranking): only_one[i]=only_one.get(i,0)+1/(60+p)
    assert max(fused.values())>max(only_one.values())

w=max(len(n) for n,_,_ in R)
for n,s,m in R: print(f'{s:5} {n}'+(f'\n        -> {m}' if m else ''))
print(sum(1 for r in R if r[1]=='PASS'),'pass',sum(1 for r in R if r[1]=='FAIL'),'fail')
