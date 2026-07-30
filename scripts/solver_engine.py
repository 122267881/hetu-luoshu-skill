from __future__ import annotations
from knowledge_core import classify_request,load_catalogs
def num(v,label,lo=0,hi=10):
 if not isinstance(v,(int,float)) or isinstance(v,bool) or not lo<=float(v)<=hi:raise ValueError(f'{label} must be {lo}-{hi}')
 return float(v)
def evaluate_options(data):
 cs=data.get('criteria');opts=data.get('options')
 if not isinstance(cs,list) or not cs or not isinstance(opts,list) or len(opts)<2:raise ValueError('criteria and at least two options required')
 cc=[];tw=0
 for c in cs:
  if not isinstance(c,dict) or c.get('direction') not in {'max','min'}:raise ValueError('direction must be max/min')
  n=str(c.get('name','')).strip();w=num(c.get('weight'),'weight',.000001,1e9)
  if not n:raise ValueError('criterion name required')
  cc.append((n,w,c['direction']));tw+=w
 rank=[]
 for o in opts:
  if not isinstance(o,dict) or not isinstance(o.get('scores'),dict):raise ValueError('invalid option')
  total=0;parts=[]
  for n,w,d in cc:
   raw=num(o['scores'].get(n),n);norm=raw if d=='max' else 10-raw;part=norm*w/tw;total+=part;parts.append({'criterion':n,'direction':d,'raw_score':raw,'normalized_score':norm,'weight':w,'contribution':round(part,4)})
  rank.append({'name':str(o.get('name','')).strip(),'score':round(total,4),'contributions':parts})
 rank.sort(key=lambda x:x['score'],reverse=True);gap=round(rank[0]['score']-rank[1]['score'],4)
 return {'method':'direction-aware weighted score','scale':'0-10','ranking':rank,'winner':rank[0]['name'],'top_gap':gap,'sensitivity_warning':'前两名差距较小，排名可能对权重敏感。' if gap<.75 else '当前差距不小，但结果仍依赖输入评分；改变关键权重前应重新计算。','evidence_label':'A','boundary':'模型组织权衡，不证明现实结果。'}
def arr(v):return [str(x) for x in v] if isinstance(v,list) else []
def handoffs(codes):
 m={'medical-diagnosis':'医疗专业人员或紧急医疗服务','financial-prediction':'持牌金融专业人员与实时数据','legal-conclusion':'合格法律专业人员','deterministic-divination':'保留文化研究，不作现实裁决'};return [m[x] for x in codes if x in m]
def solve_case(case):
 goal=case.get('goal')
 if not isinstance(goal,str) or not goal.strip():raise ValueError('goal is required and must be non-empty')
 cl=classify_request(goal+' '+str(case.get('context','')));ds,ps=load_catalogs();dm={x['id']:x for x in ds};pm={x['id']:x for x in ps}
 if case.get('domain'):
  if case['domain'] not in dm:raise ValueError('unknown domain')
  d=dm[case['domain']];cl['domain'].update({'id':d['id'],'name':d['name'],'outputs':d.get('outputs',[]),'boundaries':d.get('boundaries',[])})
 if case.get('problem_type'):
  if case['problem_type'] not in pm:raise ValueError('unknown problem_type')
  p=pm[case['problem_type']];cl['problem_type'].update({'id':p['id'],'name':p['name'],'question':p.get('question'),'outputs':p.get('outputs',[])})
 constraints=arr(case.get('constraints'));resources=arr(case.get('resources'));people=arr(case.get('stakeholders'));metrics=arr(case.get('success_metrics'));missing=[f for f in cl['domain'].get('required_inputs',[]) if f not in case and f not in {'goal','context'}];hs=handoffs(cl['risk_codes'])
 base={'framework':'河洛九步现实问题解决引擎','goal':goal,'domain':cl['domain'],'problem_type':cl['problem_type'],'support_level':cl['support_level'],'trust_gate':cl['trust_gate'],'handoff_required':cl['support_level']=='restricted','professional_handoffs':hs,'assumptions':[],'missing_inputs':missing,'evidence_label':'A'}
 if cl['support_level']=='restricted':return {**base,'nine_step_loop':[],'execution_plan':[],'verification':{},'rollback':{},'boundary':'高影响问题停止确定性求解并转交专业系统。'}
 steps=[('establish-center','立极','固定一个中心目标。',{'goal':goal,'success_metrics':metrics or ['定义可观察结果'],'non_goals':['不以建议数量代替结果']}),('set-boundary','定界','确定范围、责任和约束。',{'context':case.get('context',''),'stakeholders':people,'constraints':constraints,'domain_boundaries':cl['domain'].get('boundaries',[])}),('map-body','定体','识别结构、资源和依赖。',{'resources':resources,'core_components':cl['domain'].get('outputs',[]),'invariants':cl['domain'].get('boundaries',[])}),('read-situation','定势','区分事实、假设和未知。',{'known_context':case.get('context',''),'missing_inputs':missing,'assumptions':[],'stage':cl['problem_type']['name']}),('balance-tensions','定衡','识别主要矛盾。',{'tensions':['速度 vs 质量','短期验证 vs 长期能力','价值 vs 成本风险'],'decision_anchor':metrics[0] if metrics else goal}),('choose-strategy','定策','生成最小可验证策略。',{'problem_question':cl['problem_type'].get('question'),'recommended_strategy':'先建立最小闭环取得真实反馈，再扩大投入。','alternatives':['补证据','小范围试点','分阶段实施']}),('define-action','定行','明确负责人、交付物和检查点。',{'owner':people[0] if people else '需求负责人','review_owner':people[-1] if people else '独立复核者','primary_resource':resources[0] if resources else '现有资源','deliverables':cl['domain'].get('outputs',[])}),('define-verification','定验','定义基线、指标和停止条件。',{'metrics':metrics or ['目标相关核心指标'],'baseline':'执行前记录当前状态','evidence_threshold':'至少一个外部可观察结果','failure_signals':['没有真实反馈','关键约束被破坏','投入增加但指标不改善']}),('adapt-and-learn','定变','按反馈继续、调整或回滚。',{'continue_if':'指标改善且边界未破坏','adjust_if':'部分改善但出现新瓶颈','rollback_if':'指标恶化或边界突破','learning_asset':'把成功或失败规则写入案例与测试'})]
 loop=[{'id':a,'name':b,'purpose':c,'content':d} for a,b,c,d in steps];owner=people[0] if people else '需求负责人';review=people[-1] if people else '独立复核者';outs=cl['domain'].get('outputs',[])
 plan=[{'step':1,'action':'冻结目标、标准、范围和非目标','owner':owner,'deliverable':'一页问题定义','checkpoint':'参与者使用同一目标'},{'step':2,'action':'补齐关键输入并验证假设','owner':owner,'deliverable':'事实与未知清单','checkpoint':'消除一个方向性不确定性'},{'step':3,'action':'执行最小闭环试点','owner':owner,'deliverable':outs[0] if outs else '最小可验证产物','checkpoint':'获得真实反馈'},{'step':4,'action':'按指标复盘并决定下一步','owner':review,'deliverable':'决策记录','checkpoint':'决策可追溯到证据'}]
 verification={'baseline':'执行前记录当前状态','metrics':metrics or ['目标相关指标'],'pass_condition':'至少一个核心指标达标且未突破约束','failure_signals':['指标无改善','证据无法复现','成本风险超限','依赖长期不满足'],'review_cadence':'每个里程碑后复盘','independent_review':review};rollback={'trigger':'指标恶化、边界突破、假设证伪或继续投入净价值为负','actions':['停止扩大投入','恢复稳定状态','保留证据','选择更小方案或专业接管'],'preserve':['原始数据','决策记录','成功不变量','未解决风险']}
 return {**base,'nine_step_loop':loop,'execution_plan':plan,'verification':verification,'rollback':rollback,'boundary':'提供结构化分析与执行闭环，不保证解决所有问题。'}
