from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data/knowledge-base.json'; DOMAINS=ROOT/'data/application-domains.json'; PATTERNS=ROOT/'data/problem-patterns.json'; LUOSHU=((4,9,2),(3,5,7),(8,1,6))
def read_json(p:Path):
 d=json.loads(p.read_text(encoding='utf-8'))
 if not isinstance(d,dict):raise ValueError(f'{p.name} root must be object')
 return d
def load_knowledge():
 d=read_json(DATA);validate_knowledge(d);return d
def validate_knowledge(d):
 if d.get('schema_version')!=2:raise ValueError('schema_version must be 2')
 s=d.get('sources');t=d.get('terms');c=d.get('claims')
 if not isinstance(s,list) or len(s)<8 or not isinstance(t,list) or len(t)<20 or not isinstance(c,list) or len(c)<25:raise ValueError('knowledge counts are insufficient')
 si={x.get('id') for x in s if isinstance(x,dict)};ci=set()
 for x in c:
  if not isinstance(x,dict) or not isinstance(x.get('id'),str) or x['id'] in ci:raise ValueError('invalid claim')
  ci.add(x['id'])
  if x.get('evidence') not in {'P','H','T','M','A','U'} or x.get('confidence') not in {'high','medium','low','contested'} or not isinstance(x.get('source_ids'),list) or not x['source_ids'] or not set(x['source_ids'])<=si:raise ValueError('invalid claim metadata')
 for x in t:
  if not isinstance(x,dict) or not isinstance(x.get('claim_ids'),list) or not set(x['claim_ids'])<=ci:raise ValueError('invalid term')
def load_catalogs():
 d=read_json(DOMAINS).get('domains');p=read_json(PATTERNS).get('patterns')
 if not isinstance(d,list) or not isinstance(p,list):raise ValueError('invalid catalogs')
 return d,p
def norm(s):return ''.join(str(s).lower().split())
def term_payload(q,d):
 nq=norm(q);term=None
 for x in d['terms']:
  names=[x.get('term','')]+list(x.get('aliases',[]))
  if any(nq==norm(n) or nq in norm(n) or norm(n) in nq for n in names):term=x;break
 if not term:return None
 cm={x['id']:x for x in d['claims']};ids=term['claim_ids']
 return {'query':q,'term':term['term'],'aliases':term.get('aliases',[]),'category':term.get('category'),'summary':term.get('summary'),'evidence':term.get('evidence',cm[ids[0]]['evidence']),'claim_ids':ids,'claims':[cm[i] for i in ids]}
def rotate(g):return tuple(tuple(g[len(g)-1-r][c] for r in range(len(g))) for c in range(len(g)))
def reflect(g):return tuple(tuple(reversed(r)) for r in g)
def luoshu_symmetries():
 out=[];g=LUOSHU
 for _ in range(4):
  for x in (g,reflect(g)):
   if x not in out:out.append(x)
  g=rotate(g)
 return out
def line_sums(grid:Iterable[Iterable[int]]):
 g=[list(r) for r in grid];n=len(g);return [sum(r) for r in g]+[sum(g[r][c] for r in range(n)) for c in range(n)]+[sum(g[i][i] for i in range(n)),sum(g[i][n-1-i] for i in range(n))]
def is_magic_square(grid):
 g=[list(r) for r in grid];return len(g)==3 and all(len(r)==3 for r in g) and sorted(v for r in g for v in r)==list(range(1,10)) and line_sums(g)==[15]*8 and g[1][1]==5
RULES=[('absolute-origin','WARN',('唯一源头','所有中华文化','所有中华文明')),('archaeology-overclaim','WARN',('考古证明伏羲','直接传下来')),('science-causation','WARN',('证明现代物理','科学定律','量子证明')),('medical-diagnosis','FAIL',('诊断','什么病','吃什么药','用药','处方','治疗','胸痛')),('financial-prediction','FAIL',('币价','股价','买卖信号','收益保证','预测市场','预测明日','涨跌')),('legal-conclusion','FAIL',('胜诉','败诉','判刑','违法结论','法律责任')),('deterministic-divination','FAIL',('百分百吉凶','寿命','灾祸','确定命运','必然发财'))]
def audit_claim(text):
 codes=[];issues=[];gate='PASS'
 for code,severity,words in RULES:
  if any(w in text for w in words):
   codes.append(code);issues.append({'code':code,'severity':severity})
   if severity=='FAIL':gate='FAIL'
   elif gate=='PASS':gate='WARN'
 return {'claim':text,'trust_gate':gate,'risk_codes':codes,'issues':issues,'recommended_rewrite':'改为带证据等级、范围和不确定性的表述。' if codes else '未命中已知风险，仍需正常查证。'}
def select(text,items,fallback):
 scored=[]
 for i,x in enumerate(items):
  m=[str(v) for v in x.get('triggers',[]) if str(v).lower() in text.lower()];scored.append((len(m),-i,x,m))
 score,_,item,m=max(scored,key=lambda z:(z[0],z[1]))
 if score==0:item=next((x for x in items if x.get('id')==fallback),items[0]);m=[]
 return item,m,score
def classify_request(text):
 ds,ps=load_catalogs();d,dm,dc=select(text,ds,'general-complex-problem');p,pm,pc=select(text,ps,'clarify');a=audit_claim(text);restricted=a['trust_gate']=='FAIL';assisted=d.get('id') in {'wellbeing-routine','finance-resource-planning','governance-risk'} and not restricted
 return {'request':text,'domain':{'id':d['id'],'name':d['name'],'matched_triggers':dm,'score':dc,'required_inputs':d.get('required_inputs',[]),'outputs':d.get('outputs',[]),'boundaries':d.get('boundaries',[])},'problem_type':{'id':p['id'],'name':p['name'],'matched_triggers':pm,'score':pc,'question':p.get('question'),'outputs':p.get('outputs',[])},'support_level':'restricted' if restricted else ('assisted' if assisted else 'supported'),'trust_gate':a['trust_gate'],'handoff_required':restricted,'risk_codes':a['risk_codes'],'evidence_label':'A','classification_note':'现代目录路由，不是传统河洛固定原义。'}
