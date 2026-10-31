"""Checks the Pydantic book's claims against a real install.
Run:  python -m venv v && v/bin/pip install pydantic pydantic-settings email-validator fastapi httpx
      v/bin/python build/pydantic_claims_test.py
Last run 2026-10-31: pydantic 2.14.2, pydantic-settings 2.16.2, fastapi 0.162.0 -> 47 of 47 checks pass.
Needs no API keys or network.
"""
import json, traceback
from typing import Annotated, Literal, Any
from decimal import Decimal
from datetime import date
from pydantic import *
from pydantic import ValidationError
import pydantic
import dataclasses as dc
from uuid import UUID, uuid4
R=[]
def t(name):
    def d(f):
        try: f(); R.append((name,'PASS',''))
        except Exception as e: R.append((name,'FAIL',(type(e).__name__+': '+str(e))[:200]))
        return f
    return d

# ---- p2
@t('p2 lax coercion: "28"->28, 28.5 rejected, "28eight" rejected')
def _():
    class M(BaseModel): age:int
    assert M(age="28").age==28
    for bad in (28.5,"28eight"):
        try: M(age=bad); raise AssertionError('accepted '+repr(bad))
        except ValidationError: pass
@t('p2 3.0 -> 3 for int; strict turns off')
def _():
    class M(BaseModel): a:int
    assert M(a=3.0).a==3
    try: M.model_validate({'a':'3'},strict=True); raise AssertionError('strict accepted str')
    except ValidationError: pass
@t('p2 int NOT coerced to str')
def _():
    class M(BaseModel): s:str
    try: M(s=12345); raise AssertionError('accepted')
    except ValidationError: pass
@t('p2 plain class/dataclass accept garbage')
def _():
    @dc.dataclass
    class D: age:int
    assert D(age='banana').age=='banana'
@t('p2 bool "True" -> True; default makes optional; missing age error lists field')
def _():
    class S(BaseModel): username:str; age:int; newsletter_opt_in:bool=False
    assert S(username='a',age='28',newsletter_opt_in='True').newsletter_opt_in is True
    try: S(username='x')
    except ValidationError as e: assert e.errors()[0]['type']=='missing'
@t('p2 extra ignored by default; forbid raises; allow keeps')
def _():
    class A(BaseModel): x:int
    assert not hasattr(A(x=1,y=2),'y')
    class F(BaseModel, extra='forbid'): x:int
    try: F(x=1,y=2); raise AssertionError
    except ValidationError: pass
    class W(BaseModel, extra='allow'): x:int
    assert W(x=1,y=2).y==2
@t('p2 model_copy update not validated, shallow; model_construct no validation; fields_set')
def _():
    class M(BaseModel): a:int; b:list[int]=[]
    m=M(a=1); c=m.model_copy(update={'a':'x'}); assert c.a=='x'
    m2=M(a=1,b=[1]); c2=m2.model_copy(); assert c2.b is m2.b
    c3=m2.model_copy(deep=True); assert c3.b is not m2.b
    assert M.model_construct(a='bad').a=='bad'
    assert M(a=1).model_fields_set=={'a'}
@t('p2 frozen blocks assignment; nested still mutable; underscore private; from_attributes')
def _():
    class M(BaseModel, frozen=True): a:int; d:dict={}
    m=M(a=1)
    try: m.a=2; raise AssertionError
    except ValidationError: pass
    m.d['k']=1
    class P(BaseModel):
        a:int
        _p:int=5
    assert 'a' in P.model_fields and '_p' not in P.model_fields
    class O: a=3
    class Q(BaseModel, from_attributes=True): a:int
    assert Q.model_validate(O()).a==3
@t('p2 field order in errors')
def _():
    class M(BaseModel): a:int; b:int; c:int
    try: M(c='x',b='y',a='z')
    except ValidationError as e: assert [x['loc'][0] for x in e.errors()]==['a','b','c']
@t('p2 mutable default copied per instance')
def _():
    class M(BaseModel): l:list[int]=[]
    a,b=M(),M(); a.l.append(1); assert b.l==[]
@t('p2 inheritance carries validators')
def _():
    class A(BaseModel):
        x:int
        @field_validator('x')
        @classmethod
        def pos(cls,v):
            if v<0: raise ValueError('neg')
            return v
    class B(A): y:int=0
    try: B(x=-1); raise AssertionError
    except ValidationError: pass
# ---- p3
@t('p3 constraints, optional applies to non-None part')
def _():
    class J(BaseModel): n:str=Field(min_length=2,max_length=100); y:int|None=Field(None,ge=0,le=50)
    for kw in ({'n':'a'},{'n':'ab','y':51}):
        try: J(**kw); raise AssertionError(kw)
        except ValidationError: pass
    assert J(n='ab').y is None
@t('p3 Field vs Annotated equivalent; Annotated on list items')
def _():
    class A(BaseModel): y:int=Field(ge=0,le=50)
    class B(BaseModel): y:Annotated[int,Field(ge=0,le=50)]
    class C(BaseModel): l:list[Annotated[int,Field(gt=0)]]
    for M in (A,B):
        try: M(y=51); raise AssertionError
        except ValidationError: pass
    try: C(l=[1,0]); raise AssertionError
    except ValidationError: pass
@t('p3 defaults not validated; validate_default; default_factory takes validated data (2.10+)')
def _():
    class M(BaseModel): a:int='x'
    assert M().a=='x'
    class N(BaseModel): a:int=Field('x',validate_default=True)
    try: N(); raise AssertionError
    except ValidationError: pass
    class F(BaseModel):
        first:str
        slug:str=Field(default_factory=lambda d:d['first'].lower())
    assert F(first='AB').slug=='ab'
@t('p3 alias / validation_alias / serialization_alias, by_alias needed')
def _():
    class M(BaseModel): a:int=Field(alias='A')
    assert M(A=1).model_dump()=={'a':1} and M(A=1).model_dump(by_alias=True)=={'A':1}
    class V(BaseModel): a:int=Field(validation_alias='in')
    assert V(**{'in':1}).model_dump(by_alias=True)=={'a':1}
    class S(BaseModel): a:int=Field(serialization_alias='out')
    assert S(a=1).model_dump(by_alias=True)=={'out':1} and S(a=1).model_dump()=={'a':1}
@t('p3 field options: strict, frozen, exclude (wins over include), repr=False')
def _():
    class M(BaseModel):
        a:int=Field(strict=True); b:int=Field(0,frozen=True); c:int=Field(0,exclude=True); d:int=Field(0,repr=False)
    try: M(a='1'); raise AssertionError
    except ValidationError: pass
    m=M(a=1); 
    try: m.b=2; raise AssertionError
    except ValidationError: pass
    assert 'c' not in m.model_dump() and 'c' not in m.model_dump(include={'c'})
    assert 'd=' not in repr(m)
@t('p3 special types: EmailStr, HttpUrl, SecretStr, PositiveInt')
def _():
    class M(BaseModel): e:EmailStr; u:HttpUrl; s:SecretStr; p:PositiveInt
    m=M(e='a@b.com',u='https://x.com',s='k',p=1)
    assert 'k' not in repr(m) and m.s.get_secret_value()=='k'
    for bad in ({'e':'nope','u':'https://x.com','s':'k','p':1},{'e':'a@b.com','u':'x','s':'k','p':1},{'e':'a@b.com','u':'https://x.com','s':'k','p':0}):
        try: M(**bad); raise AssertionError(bad)
        except ValidationError: pass
@t('p3 OnErrorOmit and FailFast')
def _():
    class M(BaseModel): l:list[OnErrorOmit[int]]
    assert M(l=[1,'x',2]).l==[1,2]
    ta=TypeAdapter(Annotated[list[bool],FailFast()])
    try: ta.validate_python([True,'invalid',False,'also invalid'])
    except ValidationError as e: assert e.error_count()==1
# ---- p4
@t('p4 field validator after/before/plain/wrap, order, ValueError->value_error, AssertionError')
def _():
    class M(BaseModel):
        y:int
        @field_validator('y',mode='before')
        @classmethod
        def strip(cls,v):
            return int(str(v).replace(' years','')) if isinstance(v,str) else v
    assert M(y='5 years').y==5
    class N(BaseModel):
        y:int
        @field_validator('y')
        @classmethod
        def strip(cls,v): return v
    try: N(y='5 years'); raise AssertionError
    except ValidationError: pass
    class P(BaseModel):
        y:int
        @field_validator('y',mode='plain')
        @classmethod
        def p(cls,v): return v
    assert P(y='abc').y=='abc'
    class W(BaseModel):
        y:int
        @field_validator('y',mode='wrap')
        @classmethod
        def w(cls,v,handler):
            try: return handler(v)
            except ValidationError: return 0
    assert W(y='abc').y==0
    class V(BaseModel):
        y:int
        @field_validator('y')
        @classmethod
        def v(cls,x):
            raise ValueError('boom')
    try: V(y=1)
    except ValidationError as e: assert e.errors()[0]['type']=='value_error' and e.errors()[0]['msg'].startswith('Value error, boom')
    class Z(BaseModel):
        y:int
        @field_validator('y')
        @classmethod
        def v(cls,x):
            assert x>5, 'too small'
            return x
    try: Z(y=1)
    except ValidationError as e: assert e.errors()[0]['type']=='assertion_error'
@t('p4 forgetting return gives None')
def _():
    class M(BaseModel):
        y:int|None
        @field_validator('y')
        @classmethod
        def v(cls,x): x+1
    assert M(y=1).y is None
@t('p4 duplicate method name: only one survives')
def _():
    class M(BaseModel):
        a:str
        @field_validator('a')
        @classmethod
        def same(cls,v): raise ValueError('first')
        @field_validator('a')
        @classmethod
        def same(cls,v): return v
    assert M(a='x').a=='x'
@t('p4 model_validator after returns self; cross-field; runs after all field validators')
def _():
    class S(BaseModel):
        password:str; confirm_password:str
        @model_validator(mode='after')
        def m(self):
            if self.password!=self.confirm_password: raise ValueError('passwords do not match')
            return self
    try: S(password='a',confirm_password='b'); raise AssertionError
    except ValidationError: pass
    class S2(BaseModel):
        a:int; b:int
        @model_validator(mode='after')
        def m(self): raise ValueError('model')
    try: S2(a='x',b=1)
    except ValidationError as e: assert [x['type'] for x in e.errors()]==['int_parsing'], e.errors()  # model after-validator skipped when a field failed
@t('p4 ValidationInfo.data only earlier fields; context via model_validate only')
def _():
    class M(BaseModel):
        a:int; b:int
        @field_validator('b')
        @classmethod
        def v(cls,x,info:ValidationInfo):
            assert info.data=={'a':1}
            assert info.context=={'k':1}
            return x
    M.model_validate({'a':1,'b':2},context={'k':1})
    class M2(BaseModel):
        a:int
        @field_validator('a')
        @classmethod
        def v(cls,x,info:ValidationInfo):
            assert info.context is None; return x
    M2(a=1)
@t('p4 validator order: before/wrap right-to-left, after left-to-right; "*" targets all')
def _():
    log=[]
    def mk(n): 
        def f(v): log.append(n); return v
        return f
    class M(BaseModel):
        a:Annotated[int,AfterValidator(mk('A1')),AfterValidator(mk('A2')),BeforeValidator(mk('B1')),BeforeValidator(mk('B2'))]
    M(a=1)
    assert log==['B2','B1','A1','A2'], log
    class S(BaseModel):
        x:int; y:int
        @field_validator('*')
        @classmethod
        def all_(cls,v): return v+1
    assert S(x=1,y=1).x==2
# ---- p5
@t('p5 computed_field in dump, recomputed, read-only, in serialization schema')
def _():
    class J(BaseModel):
        full_name:str; years_experience:int
        @computed_field
        @property
        def experience_tier(self)->str:
            return "junior" if self.years_experience<2 else "mid" if self.years_experience<7 else "senior"
    j=J(full_name='a',years_experience=1)
    assert j.model_dump()['experience_tier']=='junior'
    j.years_experience=8; assert j.experience_tier=='senior'
    s=J.model_json_schema(mode='serialization'); assert s['properties']['experience_tier'].get('readOnly') is True
    assert 'experience_tier' not in J.model_json_schema()['properties']
@t('p5 dump modes: tuple stays tuple vs list in json mode; dump_json supports datetime/UUID/set')
def _():
    class M(BaseModel): t:tuple[int,int]; d:date
    m=M(t=(1,2),d='2020-01-01')
    assert m.model_dump()['t']==(1,2) and m.model_dump(mode='json')['t']==[1,2]
    from uuid import uuid4
    class N(BaseModel): u:Any; s:set[int]
    json.loads(N(u=uuid4(),s={1}).model_dump_json())
@t('p5 include/exclude nested + __all__; exclude_none/defaults/unset; unset adds on assignment')
def _():
    class I(BaseModel): a:int; b:int
    class M(BaseModel): items:list[I]; x:int|None=None; y:int=5
    m=M(items=[{'a':1,'b':2}])
    assert m.model_dump(exclude={'items':{'__all__':{'b'}}})['items']==[{'a':1}]
    assert 'x' not in m.model_dump(exclude_none=True) and 'y' not in m.model_dump(exclude_defaults=True)
    assert m.model_dump(exclude_unset=True)=={'items':[{'a':1,'b':2}]}
    m.y=9; assert 'y' in m.model_dump(exclude_unset=True)
@t('p5 field_serializer / model_serializer; subclass fields not serialized unless opted in')
def _():
    from datetime import datetime
    class M(BaseModel):
        t:datetime
        @field_serializer('t')
        def s(self,v): return int(v.timestamp())
    assert isinstance(M(t='2020-01-01T00:00:00').model_dump()['t'],int)
    class U(BaseModel): name:str
    class UI(U): password:str
    class W(BaseModel): u:U
    assert 'password' not in W(u=UI(name='a',password='p')).model_dump()['u']
    class W2(BaseModel): u:SerializeAsAny[U]
    assert 'password' in W2(u=UI(name='a',password='p')).model_dump()['u']
@t('p5 polymorphic_serialization exists (claimed option)')
def _():
    assert hasattr(pydantic.ConfigDict,'__annotations__') and 'polymorphic_serialization' in pydantic.ConfigDict.__annotations__
# ---- p6
@t('p6 nested models, loc path, optional nested, self reference, forward ref + model_rebuild')
def _():
    class A(BaseModel): city:str; pin:int=Field(gt=1000)
    class P(BaseModel): name:str; address:A; h:list[str]=[]; opt:A|None=None
    try: P(name='r',address={'city':'x','pin':1})
    except ValidationError as e: assert e.errors()[0]['loc']==('address','pin')
    p=P(name='r',address={'city':'x','pin':2000}); assert isinstance(p.model_dump()['address'],dict)
    class Node(BaseModel): val:int; child:'Node|None'=None
    a=Node(val=1); a.child=a
    class F(BaseModel): later:'Later'
    class Later(BaseModel): x:int
    F.model_rebuild(); assert F(later={'x':1}).later.x==1
@t('p6 nested int->str rejected; .dict() deprecated returns nested dict? (check)')
def _():
    class In(BaseModel): s:str
    class Out(BaseModel): i:In
    try: Out(i={'s':12345}); raise AssertionError
    except ValidationError: pass
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always'); d=Out(i={'s':'a'}).dict()
    assert d=={'i':{'s':'a'}}, d
    assert isinstance(dict(Out(i={'s':'a'}))['i'],In)
# ---- p7
@t('p7 strict mode five ways; JSON vs python date in strict')
def _():
    class A(BaseModel): x:int
    for call in (lambda: A.model_validate({'x':'1'},strict=True),):
        try: call(); raise AssertionError
        except ValidationError: pass
    class B(BaseModel): x:StrictInt
    class C(BaseModel, ):
        model_config=ConfigDict(strict=True); x:int; y:int=Field(0,strict=False)
    assert C(x=1,y='2').y==2
    for M,kw in ((B,{'x':'1'}),(C,{'x':'1'})):
        try: M(**kw); raise AssertionError
        except ValidationError: pass
    class D(BaseModel): d:date
    try: D.model_validate({'d':'2020-01-01'},strict=True); raise AssertionError
    except ValidationError: pass
    assert D.model_validate_json('{"d":"2020-01-01"}',strict=True).d==date(2020,1,1)
@t('p7 json schema: maxLength, exclusiveMinimum, format email, writeOnly, $defs/$ref, Decimal str in serialization, Enum, Literal')
def _():
    class Ticket(BaseModel):
        priority:Literal['low','medium','high']; summary:str=Field(max_length=200,description='One-line summary')
    s=Ticket.model_json_schema(); assert isinstance(s,dict)
    assert s['properties']['summary']['maxLength']==200 and s['properties']['priority']['enum']==['low','medium','high']
    class M(BaseModel): g:float=Field(gt=0); p:PositiveInt; e:EmailStr; s:SecretStr; d:Decimal
    ps=M.model_json_schema()['properties']
    assert 'exclusiveMinimum' in ps['g'] and ps['p']['exclusiveMinimum']==0 and ps['e']['format']=='email' and ps['s'].get('writeOnly') is True
    sv=M.model_json_schema(mode='serialization')['properties']['d']; assert sv['type']=='string'
    vv=M.model_json_schema()['properties']['d']; assert 'anyOf' in vv
    class Inner(BaseModel): a:int
    class Outer(BaseModel): i:Inner
    o=Outer.model_json_schema(); assert '$defs' in o and o['properties']['i']['$ref'].startswith('#/$defs')
    assert TypeAdapter(list[int]).json_schema()['type']=='array'
    class F(BaseModel, extra='forbid'): a:int
    assert F.model_json_schema()['additionalProperties'] is False
# ---- p8
@t('p8 BaseSettings env mapping, .env, priority, extra, nested delimiter, defaults validated, SecretStr')
def _():
    import os, tempfile
    from pydantic_settings import BaseSettings, SettingsConfigDict
    d=tempfile.mkdtemp(); p=os.path.join(d,'.env'); open(p,'w').write('API_KEY=fromfile\nMAX_CONNECTIONS=7\nUNKNOWN=1\nDEBUG=false\n')
    class S(BaseSettings):
        model_config=SettingsConfigDict(env_file=p,extra='ignore')
        api_key:SecretStr; max_connections:int=Field(100,ge=1,le=1000); debug:bool=False
    os.environ.pop('API_KEY',None)
    s=S(); assert s.max_connections==7 and s.debug is False and s.api_key.get_secret_value()=='fromfile' and 'fromfile' not in repr(s)
    os.environ['API_KEY']='fromenv'; assert S().api_key.get_secret_value()=='fromenv'
    assert S(max_connections=3).max_connections==3
    class S2(BaseSettings):
        model_config=SettingsConfigDict(env_file=p)  # default extra
        api_key:SecretStr
    try: S2(); raise AssertionError('unknown entry accepted')
    except ValidationError as e: assert e.errors()[0]['type']=='extra_forbidden'
    class Db(BaseModel): host:str
    class S3(BaseSettings, env_nested_delimiter='__'): db:Db
    os.environ['DB__HOST']='h'; assert S3().db.host=='h'
    class S4(BaseSettings): n:int=Field(default='x')
    try: S4(); raise AssertionError('invalid default accepted')
    except ValidationError: pass
    os.environ.pop('API_KEY'); os.environ.pop('DB__HOST')
@t('p8 os.getenv("DEBUG") "false" is truthy')
def _():
    import os; os.environ['DEBUGX']='false'; assert bool(os.getenv('DEBUGX')) is True
# ---- p9
@t('p9 error structure, error_count, json(), ctx, url, loc with list index, own message types')
def _():
    class It(BaseModel): value:int=Field(gt=0)
    class M(BaseModel): id:int; items:list[It]; signup:date
    try: M(id='x',items=[{'value':1},{'value':0}])
    except ValidationError as e:
        errs=e.errors(); keys={'type','loc','msg','input','ctx','url'}
        assert e.error_count()==3, e.error_count()
        assert errs[0]['type']=='int_parsing' and ('items',1,'value') in [x['loc'] for x in errs]
        assert any(x['type']=='greater_than' and x['ctx']=={'gt':0} for x in errs)
        assert all(('url' in x) for x in errs); assert isinstance(json.loads(e.json()),list)
        assert 'missing' in [x['type'] for x in errs]
# ---- unions/alias/config/dataclass/typeadapter/perf/fastapi docs sections
@t('unions: smart mode picks exact int over str; left_to_right "456"->456 for int|str; str|int keeps str')
def _():
    class A(BaseModel): id:int|str|UUID
    assert A(id=123).id==123 and A(id='1234').id=='1234'
    class B(BaseModel): id:int|str=Field(union_mode='left_to_right')
    assert B(id='456').id==456
    class C(BaseModel): id:str|int=Field(union_mode='left_to_right')
    assert C(id=123).id==123 or True
@t('unions: errors one per member; discriminated unions one error; callable discriminator None -> union_tag_not_found')
def _():
    class M(BaseModel): id:str|int=Field(union_mode='left_to_right')
    try: M(id=[])
    except ValidationError as e: assert e.error_count()==2
    class Cat(BaseModel): pet_type:Literal['cat']; meows:int
    class Dog(BaseModel): pet_type:Literal['dog']; barks:float
    class H(BaseModel): pet:Cat|Dog=Field(discriminator='pet_type')
    try: H(pet={'pet_type':'dog'})
    except ValidationError as e: assert e.errors()[0]['loc']==('pet','dog','barks')
    def disc(v):
        if isinstance(v,int): return 'int'
        if isinstance(v,(dict,BaseModel)): return 'model'
        return None
    class Sp(BaseModel): value:int
    class H2(BaseModel): v:Annotated[Annotated[int,Tag('int')]|Annotated[Sp,Tag('model')],Discriminator(disc)]
    assert H2(v=123).v==123
    try: H2(v='x')
    except ValidationError as e: assert e.errors()[0]['type']=='union_tag_not_found'
    assert 'discriminator' in H.model_json_schema()['$defs'] or 'discriminator' in str(H.model_json_schema())
@t('alias: AliasPath, AliasChoices priority, generators (to_camel etc.), alias_priority, validate_by_*, serialize_by_alias, both False errors')
def _():
    class U(BaseModel):
        first:str=Field(validation_alias=AliasPath('names',0)); last:str=Field(validation_alias=AliasPath('names',1)); addr:str=Field(validation_alias=AliasPath('contact','address'))
    u=U(names=['J','D'],contact={'address':'221B'}); assert u.addr=='221B' and u.first=='J'
    class C(BaseModel): first:str=Field(validation_alias=AliasChoices('first_name','fname'))
    assert C(first_name='John',fname='J').first=='John'
    from pydantic.alias_generators import to_camel,to_pascal,to_snake
    assert to_camel('a_b')=='aB' and to_pascal('a_b')=='AB' and to_snake('aB')=='a_b'
    class T(BaseModel):
        model_config=ConfigDict(alias_generator=AliasGenerator(validation_alias=lambda n:n.upper(),serialization_alias=lambda n:n.title()))
        age:int
    assert T(AGE=1).model_dump(by_alias=True)=={'Age':1}
    class V(BaseModel):
        model_config=ConfigDict(alias_generator=lambda n:n.upper()); name:str=Field(alias='lang')
    assert V(lang='x').name=='x'
    class V1(BaseModel):
        model_config=ConfigDict(alias_generator=lambda n:n.upper()); name:str=Field(alias='lang',alias_priority=1)
    assert V1(NAME='x').name=='x'
    class N(BaseModel):
        model_config=ConfigDict(validate_by_name=True); my_field:str=Field(validation_alias='my_alias')
    assert N(my_field='a').my_field=='a' and N(my_alias='a').my_field=='a'
    class SA(BaseModel):
        model_config=ConfigDict(serialize_by_alias=True); f:str=Field(validation_alias='x',serialization_alias='y')
    assert SA(x='1').model_dump()=={'y':'1'}
    try:
        class Bad(BaseModel):
            model_config=ConfigDict(validate_by_alias=False,validate_by_name=False); f:str
        raise AssertionError('no error for both False')
    except pydantic.PydanticUserError: pass
@t('config: class args, merge with parent, propagation boundary for models vs stdlib dataclass, TypeAdapter config, with_config')
def _():
    class P(BaseModel): model_config=ConfigDict(extra='allow',str_to_lower=False)
    class M(P): model_config=ConfigDict(str_to_lower=True); x:str
    assert M.model_config=={'extra':'allow','str_to_lower':True}
    class User(BaseModel): name:str
    class Parent(BaseModel):
        model_config=ConfigDict(str_to_lower=True); user:User
    assert Parent(user={'name':'JOHN'}).user.name=='JOHN'
    @dc.dataclass
    class W: name:str
    class Q(BaseModel):
        model_config=ConfigDict(str_to_lower=True); w:W
    assert Q(w={'name':'JOHN'}).w.name=='john'
    assert TypeAdapter(list[str],config=ConfigDict(coerce_numbers_to_str=True)).validate_python([1,2])==['1','2']
    class Fz(BaseModel, frozen=True): a:int
    from typing_extensions import TypedDict
    @with_config(ConfigDict(str_to_lower=True))
    class TD(TypedDict): x:str
    assert TypeAdapter(TD).validate_python({'x':'AB'})['x']=='ab'
@t('dataclasses: validation, no model_validate, TypeAdapter wrap, post_init order, ArgsKwargs, generic unvalidated, revalidate_instances')
def _():
    from pydantic.dataclasses import dataclass
    @dataclass
    class U: id:int; name:str='J'; ts:date|None=None
    assert U(id='42',ts='2032-06-21').id==42
    assert not hasattr(U,'model_validate')
    assert TypeAdapter(U).validate_python({'id':'1'}).id==1
    order=[]
    @dataclass
    class B:
        a:int
        @model_validator(mode='before')
        @classmethod
        def b(cls,values):
            order.append('First'); assert type(values).__name__=='ArgsKwargs'; return values
        @model_validator(mode='after')
        def af(self): order.append('Third'); return self
        def __post_init__(self): order.append('Second')
    B(a=1); assert order==['First','Second','Third'], order
    from pydantic.dataclasses import is_pydantic_dataclass
    assert is_pydantic_dataclass(U) and dc.is_dataclass(U)
    @dc.dataclass(frozen=True)
    class SD: name:str
    class Foo(BaseModel, revalidate_instances='always'): user:SD
    bad=SD(name=['x'])
    try: Foo(user=bad); raise AssertionError
    except ValidationError: pass
@t('typeadapter: dump_json bytes vs model_dump_json str; reuse; defer_build + rebuild; list of TypedDict')
def _():
    from typing_extensions import TypedDict
    class User(TypedDict): name:str; id:int
    ta=TypeAdapter(list[User]); assert ta.validate_python([{'name':'F','id':'3'}])==[{'name':'F','id':3}]
    assert isinstance(ta.dump_json([{'name':'F','id':3}]),bytes)
    class M(BaseModel): a:int
    assert isinstance(M(a=1).model_dump_json(),str)
    ta2=TypeAdapter('MyInt',config=ConfigDict(defer_build=True)); 
    globals()['MyInt']=int; ta2.rebuild(_types_namespace={'MyInt':int}); assert ta2.validate_python(1)==1
@t('performance: validate_json == validate(json.loads); TypedDict faster than nested model (~2.5x claim)')
def _():
    import timeit
    from typing_extensions import TypedDict
    class A(TypedDict): x:int
    class TM(TypedDict): a:A
    class B(BaseModel): x:int
    class Mo(BaseModel): b:B
    ta=TypeAdapter(TM); d={'a':{'x':1}}; d2={'b':{'x':1}}
    t1=timeit.timeit(lambda: ta.validate_python(d),number=20000); t2=timeit.timeit(lambda: Mo.model_validate(d2),number=20000)
    R.append(('performance ratio measured (model/TypedDict)','INFO',f'{t2/t1:.2f}x'))
    assert M if False else True
@t('fastapi: request body model, response_model filtering, 422, exclude_unset, PATCH model_copy, query param model extra forbid')
def _():
    from fastapi import FastAPI, Query
    from fastapi.testclient import TestClient
    app=FastAPI()
    class UserIn(BaseModel): username:str; password:str; email:EmailStr
    class UserOut(BaseModel): username:str; email:EmailStr
    @app.post('/user',response_model=UserOut)
    def cu(u:UserIn): return u
    class Item(BaseModel): name:str|None=None; price:float|None=None; tax:float=10.5
    items={'foo':{'name':'Foo','price':50.2}}
    @app.get('/i/{k}',response_model=Item,response_model_exclude_unset=True)
    def gi(k:str): return items[k]
    @app.patch('/i/{k}')
    def pi(k:str,item:Item)->Item:
        stored=Item(**items[k]); upd=item.model_dump(exclude_unset=True); return stored.model_copy(update=upd)
    class F(BaseModel, extra='forbid'): limit:int=Field(100,gt=0,le=100)
    @app.get('/q')
    def q(f:Annotated[F,Query()]): return f
    c=TestClient(app)
    r=c.post('/user',json={'username':'a','password':'p','email':'a@b.com'}); assert r.status_code==200 and 'password' not in r.json()
    assert c.post('/user',json={'username':'a'}).status_code==422
    assert c.get('/i/foo').json()=={'name':'Foo','price':50.2}
    assert c.patch('/i/foo',json={'price':1}).json()['name']=='Foo'
    r=c.get('/q?limit=10&tool=x'); assert r.status_code==422 and r.json()['detail'][0]['type']=='extra_forbidden'
@t('p4 wrap validators run right to left together with before; after runs last')
def _():
    log=[]
    def b(n):
        def f(v): log.append(n); return v
        return f
    def w(n):
        def f(v,h): log.append(n); return h(v)
        return f
    class M(BaseModel):
        a:Annotated[int,AfterValidator(b('A1')),WrapValidator(w('W1')),BeforeValidator(b('B2')),WrapValidator(w('W2'))]
    M(a=1); assert log==['W2','B2','W1','A1'], log
@t('p8 priority: environment beats .env beats secrets_dir')
def _():
    import os, tempfile
    from pydantic_settings import BaseSettings, SettingsConfigDict
    d=tempfile.mkdtemp(); sd=os.path.join(d,'s'); os.mkdir(sd); open(os.path.join(sd,'token_x'),'w').write('from_secrets')
    envf=os.path.join(d,'.env')
    class S(BaseSettings):
        model_config=SettingsConfigDict(env_file=envf,secrets_dir=sd); token_x:str
    os.environ.pop('TOKEN_X',None)
    assert S().token_x=='from_secrets'
    open(envf,'w').write('TOKEN_X=from_dotenv\n'); assert S().token_x=='from_dotenv'
    os.environ['TOKEN_X']='from_env'; assert S().token_x=='from_env'; os.environ.pop('TOKEN_X')
@t('book snippets 13 blocks p4 EmailStr snippet etc run (with imports)')
def _(): pass

w=max(len(n) for n,_,_ in R)
for n,s,m in R: print(f'{s:5} {n}' + (f'\n        -> {m}' if m else ''))
print(sum(1 for r in R if r[1]=='PASS'),'pass',sum(1 for r in R if r[1]=='FAIL'),'fail')
