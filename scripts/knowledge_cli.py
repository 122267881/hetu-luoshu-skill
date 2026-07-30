#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from knowledge_core import *
from solver_engine import evaluate_options,solve_case
def grid(g):return '\n'.join(' '.join(map(str,r)) for r in g)
def model(subject):return f'''# {subject} · 河图洛书体用建模模板\n\n## 河图之体\n核心目标：\n五组关键要素与启动/完成条件：\n稳定依赖：\n\n## 洛书之用\n中五立极：核心决策原则\n四正与四隅：\n对位制衡：\n\n## 现实变量\n- 变量：\n- 当前基线：\n\n## 验证指标\n- 核心指标：\n- 目标值：\n\n## 失败信号\n- 指标恶化或无法复现\n\n## 停止条件\n- 连续两个周期无改善时停止并复盘\n\n> 证据标签 A：现代分析框架，不是确定性预测。'''
def out(x):print(json.dumps(x,ensure_ascii=False,indent=2))
def parser():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
 for n,arg in [('lookup','query'),('audit-claim','text'),('classify','text')]:
  a=s.add_parser(n);a.add_argument(arg);a.add_argument('--json',action='store_true')
 a=s.add_parser('luoshu-symmetries');a.add_argument('--json',action='store_true');a=s.add_parser('validate-kb');a.add_argument('--json',action='store_true');a=s.add_parser('model-template');a.add_argument('subject')
 for n in ('evaluate-options','solve'):
  a=s.add_parser(n);a.add_argument('--input',required=True,type=Path);a.add_argument('--json',action='store_true')
 return p
def main():
 a=parser().parse_args()
 try:
  if a.cmd=='lookup':
   x=term_payload(a.query,load_knowledge())
   if not x:print('Term not found',file=sys.stderr);return 1
   out(x) if a.json else print(f"{x['term']}\n{x['summary']}\n证据：{x['evidence']}\n主张：{', '.join(x['claim_ids'])}");return 0
  if a.cmd=='audit-claim':
   x=audit_claim(a.text);out(x) if a.json else print(f"Trust Gate: {x['trust_gate']}\n风险：{', '.join(x['risk_codes']) or 'none'}");return 2 if x['trust_gate']=='FAIL' else 0
  if a.cmd=='luoshu-symmetries':
   gs=luoshu_symmetries();x={'count':len(gs),'all_magic':all(is_magic_square(g) for g in gs),'grids':gs};out(x) if a.json else print('\n\n'.join(grid(g) for g in gs));return 0
  if a.cmd=='validate-kb':
   d=load_knowledge();ds,ps=load_catalogs();x={'passed':True,'sources':len(d['sources']),'terms':len(d['terms']),'claims':len(d['claims']),'symmetries':len(luoshu_symmetries()),'domains':len(ds),'patterns':len(ps)};out(x) if a.json else print(f"Knowledge base: PASS\nsources={x['sources']} terms={x['terms']} claims={x['claims']} symmetries={x['symmetries']} domains={x['domains']} patterns={x['patterns']}");return 0
  if a.cmd=='model-template':print(model(a.subject));return 0
  if a.cmd=='classify':
   x=classify_request(a.text);out(x) if a.json else print(f"领域：{x['domain']['name']}\n问题类型：{x['problem_type']['name']}\n支持等级：{x['support_level']}\nTrust Gate：{x['trust_gate']}");return 2 if x['support_level']=='restricted' else 0
  if a.cmd=='evaluate-options':
   x=evaluate_options(read_json(a.input));out(x) if a.json else print('\n'.join(f"{i+1}. {o['name']}: {o['score']}" for i,o in enumerate(x['ranking'])));return 0
  if a.cmd=='solve':
   x=solve_case(read_json(a.input));out(x) if a.json else print(f"{x['framework']}\n目标：{x['goal']}\n支持等级：{x['support_level']}");return 2 if x['support_level']=='restricted' else 0
 except (OSError,ValueError,json.JSONDecodeError) as e:print(str(e),file=sys.stderr);return 3
if __name__=='__main__':raise SystemExit(main())
