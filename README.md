# 河图洛书 Skill 3.0

> 河洛知识系统与通用问题解决操作系统：把“河图定体、洛书定用”转化为可分类、可决策、可执行、可验证、可回滚的现实工作流。

## 这不是万能答案机

任何真实需求都可以先进入同一套结构化入口，但本 Skill **不能保证解决所有问题**，也不把河图洛书包装成科学预测器。

它负责：

- 找清真正目标和问题边界。
- 拆解稳定结构、资源和依赖。
- 识别当前态势、主要矛盾与失衡。
- 生成多个策略并显示权衡。
- 把策略变成负责人、行动、指标和检查点。
- 根据结果继续、调整、回滚或升级。
- 将高影响问题路由给专业人员或现实服务。

专业工具和人员继续负责医疗、法律、实时金融数据、工程验证、危机处置和现实执行。

## 3.0 新增能力

### 通用需求分类

```bash
python3 scripts/knowledge_cli.py classify \
  "我要把一个AI工具做成能收费的产品，明确客户、功能、价格和上线计划" \
  --json
```

返回：

- 领域与问题类型。
- 命中的触发词。
- supported / assisted / restricted。
- Trust Gate 和专业接管要求。

### 河洛九步求解

```bash
python3 scripts/knowledge_cli.py solve --input examples/universal-solver-case.json --json
```

九步：

1. 立极：目标与成功标准。
2. 定界：范围、角色、权限和约束。
3. 定体：结构、资源和依赖。
4. 定势：事实、假设、阶段和未知。
5. 定衡：主要矛盾和对位指标。
6. 定策：备选方案和高杠杆动作。
7. 定行：负责人、交付物和检查点。
8. 定验：基线、指标、失败信号和停止条件。
9. 定变：继续、调整、回滚、升级或沉淀规则。

### 加权选项评估

```bash
python3 scripts/knowledge_cli.py evaluate-options --input decision.json --json
```

支持：

- max / min 两种方向。
- 0–10 评分。
- 权重归一化。
- 各标准贡献明细。
- 前两名差距和敏感性提示。

### 河洛知识检索与审计

```bash
python3 scripts/knowledge_cli.py lookup "刘牧" --json
python3 scripts/knowledge_cli.py luoshu-symmetries --json
python3 scripts/knowledge_cli.py audit-claim \
  "河图洛书能够百分百预测币价和疾病" --json
python3 scripts/knowledge_cli.py validate-kb --json
```

## 能应用到哪些真实领域

| 领域 | 典型问题 | 主要输出 |
|---|---|---|
| 个人选择 | 目标冲突、优先级、习惯 | 选项、下一步、复盘日 |
| 关系沟通 | 冲突、误解、边界 | 角色图、沟通方案、边界 |
| 学习研究 | 课程、考试、论文 | 知识地图、学习循环、证据计划 |
| 职业工作 | 求职、转行、绩效 | 差距图、路径、验证项目 |
| 项目交付 | 范围、延期、依赖 | WBS、负责人、里程碑、风险表 |
| 产品创新 | 用户、MVP、定价 | 问题定义、实验、路线图 |
| 商业战略 | 变现、客户、竞争 | 战略选择、权衡、指标、行动 |
| 组织管理 | 岗位、协作、审批 | 运行模型、职责、节奏、升级路径 |
| 内容营销 | 定位、获客、转化 | 信息层级、内容计划、实验 |
| AI 系统 | Agent、知识库、自动化 | 架构、路由、数据流、安全门 |
| 故障恢复 | 异常、漏洞、事故 | 止损、排查、恢复、复盘 |
| 日常状态 | 作息、专注、习惯 | 小实验、跟踪指标、复盘 |
| 资源规划 | 预算、成本、现金流 | 场景、限制、分配、监控 |
| 治理风险 | 权限、安全、合规 | 风险表、控制、责任人、监控 |
| 创意设计 | 品牌、故事、概念 | 方向、标准、原型计划 |

领域适配是现代 A 类方法论，不声称是古代河图洛书的固定原义。

## 高影响安全边界

以下请求不会由本 Skill 继续作确定性结论：

- 根据河洛诊断症状、决定治疗或药物。
- 根据数字预测币价、股价或生成买卖信号。
- 判定违法、胜败、刑责或法律责任。
- 处理自伤、暴力、家暴等紧急危机。
- 百分百断定个人吉凶、寿命、灾祸或命运。

分类器返回 `restricted` 和退出码 2，并给出专业接管方向。

## 知识证据分层

| 标签 | 含义 |
|---|---|
| P | 经典或原始文本 |
| H | 可核查历史研究 |
| T | 后世传统解释与接受史 |
| M | 可重复计算的数学事实 |
| A | 现代方法论或应用假设 |
| U | 未核实、争议或证据不足 |

河图传统配属、宋代图式史、洛书幻方数学和现代系统建模不会被混为同一种证据。

## 安装

先校验源码包：

```bash
python3 scripts/run_checks.py
```

查看安装内容，不写文件：

```bash
python3 scripts/install.py --dry-run
```

安装到 Codex 默认 Skill 目录：

```bash
python3 scripts/install.py
```

替换已有安装并保留安全备份：

```bash
python3 scripts/install.py --force
```

安装器使用固定文件清单、SHA-256 清单和原子目录切换，不执行来源、暂存、目标或备份中的任何脚本。

## 项目结构

```text
hetu-luoshu/
├── SKILL.md
├── data/
│   ├── knowledge-base.json
│   ├── application-domains.json
│   └── problem-patterns.json
├── references/
│   ├── universal-problem-solving.md
│   ├── domain-adapters.md
│   ├── decision-and-experiment.md
│   ├── execution-and-feedback.md
│   ├── high-impact-routing.md
│   └── ...
├── scripts/
│   ├── knowledge_cli.py
│   ├── validate_models.py
│   ├── quality_check.py
│   ├── run_checks.py
│   └── install.py
├── tests/
└── examples/
```

## 验证

```bash
python3 scripts/run_checks.py
```

验证覆盖：

- 河图五组、奇偶和天地总数。
- 洛书幻方、对位和八种对称。
- 知识库来源和主张追溯。
- 高影响主张拦截。
- 通用领域与问题类型分类。
- 九步求解输出合同。
- 加权选项评估。
- 安装、备份、恢复和符号链接防护。

## 上游与许可

本项目保留并发展 `gnipbao/dao-skill` 的归根、设计、生成、评估、返观和自化能力。派生代码采用 MIT License，具体归属见 `THIRD_PARTY_NOTICES.md`。
