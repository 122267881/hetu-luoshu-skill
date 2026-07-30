# 河洛通用问题解决操作系统 3.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 把河图洛书 Skill 2.0 升级为能够统一接收、分类、建模、决策、执行、验证和复盘真实需求的 3.0 通用问题解决系统。

**Architecture:** 在既有 `knowledge_cli.py` 中增加三个确定性命令：`classify` 负责领域、问题类型和高影响路由；`evaluate-options` 负责带方向的加权权衡；`solve` 负责生成河洛九步闭环。领域与问题类型继续由 JSON 数据驱动，Skill 文档负责触发、边界和输出合同，安装器与质量检查器固定纳入全部 3.0 资产。

**Tech Stack:** Python 3.9+ 标准库、JSON、unittest、Markdown、现有安全安装器。

## Global Constraints

- 不新增第三方运行时依赖。
- 不把河洛象数解释成科学因果、确定性预测或万能答案。
- 医疗诊断、个性化高风险金融指令、法律定论、危机处置和确定性命理必须路由为 `restricted`。
- 所有现代问题解决映射标记为 A 类证据。
- 继续通过既有安装安全、知识库、数学模型和 Skill 合同回归测试。
- `SKILL.md` 保持 500 行以内。

---

### Task 1: 领域与问题类型分类器

**Files:**
- Modify: `scripts/knowledge_cli.py`
- Test: `tests/test_universal_solver.py`

**Interfaces:**
- Consumes: `data/application-domains.json`, `data/problem-patterns.json`, 用户自然语言。
- Produces: `classify_request(text: str) -> dict[str, object]`，CLI `classify <text> [--json]`。

- [x] **Step 1: 运行现有失败测试**

Run: `python3 -m unittest tests.test_universal_solver.UniversalSolverTests.test_classify_routes_product_request tests.test_universal_solver.UniversalSolverTests.test_high_impact_request_is_routed_not_solved_as_certainty -v`
Expected: FAIL，因为 `classify` 子命令尚不存在。

- [x] **Step 2: 实现数据加载和触发评分**

实现 `load_catalog()`，校验两个 JSON 的 `schema_version == 1`、ID 唯一、数组字段结构正确；按触发词命中数选择领域与问题类型，并使用 `general-complex-problem` 与 `clarify` 作为无命中回退。

- [x] **Step 3: 实现高影响路由**

复用 `audit_claim()`；命中 FAIL 时输出 `support_level=restricted`、`trust_gate=FAIL`、`handoff_required=true` 并返回退出码 2。普通请求输出 `supported`；需要真实数据或专业执行但不禁止分析的领域输出 `assisted`。

- [x] **Step 4: 运行分类测试**

Run: `python3 -m unittest tests.test_universal_solver.UniversalSolverTests.test_classify_routes_product_request tests.test_universal_solver.UniversalSolverTests.test_high_impact_request_is_routed_not_solved_as_certainty -v`
Expected: PASS。

### Task 2: 加权选项评估器

**Files:**
- Modify: `scripts/knowledge_cli.py`
- Test: `tests/test_universal_solver.py`

**Interfaces:**
- Consumes: JSON 文件，含 `criteria[{name,weight,direction}]` 与 `options[{name,scores}]`。
- Produces: `evaluate_options(data: dict[str, object]) -> dict[str, object]`，CLI `evaluate-options --input PATH [--json]`。

- [x] **Step 1: 运行现有失败测试**

Run: `python3 -m unittest tests.test_universal_solver.UniversalSolverTests.test_option_evaluator_uses_weighted_tradeoffs -v`
Expected: FAIL，因为 `evaluate-options` 子命令尚不存在。

- [x] **Step 2: 实现输入校验与方向归一化**

要求标准权重为正数、方向仅允许 `max|min`、每个选项必须包含全部标准的 0-10 数值。`max` 使用原分数，`min` 使用 `10-score`，按权重和归一化为 0-10 总分。

- [x] **Step 3: 生成排序和敏感性提示**

按总分降序输出；第一、第二名差距小于 0.75 时提示排名对权重敏感，否则提示当前排序相对稳定。保留每项标准的贡献明细。

- [x] **Step 4: 运行评估测试**

Run: `python3 -m unittest tests.test_universal_solver.UniversalSolverTests.test_option_evaluator_uses_weighted_tradeoffs -v`
Expected: PASS，`定制服务` 排名第一。

### Task 3: 河洛九步现实问题解决引擎

**Files:**
- Modify: `scripts/knowledge_cli.py`
- Test: `tests/test_universal_solver.py`
- Modify: `examples/universal-solver-case.json`

**Interfaces:**
- Consumes: JSON case，至少含非空 `goal`；可含 `context/domain/problem_type/constraints/resources/stakeholders/success_metrics`。
- Produces: `solve_case(case: dict[str, object]) -> dict[str, object]`，CLI `solve --input PATH [--json]`。

- [x] **Step 1: 运行现有失败测试**

Run: `python3 -m unittest tests.test_universal_solver.UniversalSolverTests.test_solve_outputs_complete_helu_nine_step_loop tests.test_universal_solver.UniversalSolverTests.test_solve_rejects_empty_goal -v`
Expected: FAIL，因为 `solve` 子命令尚不存在且空 goal 未按合同返回 3。

- [x] **Step 2: 实现输入合同与自动路由**

缺失或空白 `goal` 抛出 `ValueError("goal is required and must be non-empty")`。未显式给出 domain/problem_type 时，使用分类器从 goal 与 context 推断；显式 ID 必须在目录中存在。

- [x] **Step 3: 生成九步结构**

固定输出九步 ID：`establish-center`、`set-boundary`、`map-body`、`read-situation`、`balance-tensions`、`choose-strategy`、`define-action`、`define-verification`、`adapt-and-learn`。每步包含 purpose、inputs、outputs 和基于 case 的具体内容。

- [x] **Step 4: 生成执行、验证与回滚合同**

输出 `execution_plan`、`verification`、`rollback`、`assumptions`、`missing_inputs`、`professional_handoffs`，并标记 `evidence_label=A`。高影响 FAIL 的 case 不生成确定性方案，只输出接管路径。

- [x] **Step 5: 运行 solve 测试**

Run: `python3 -m unittest tests.test_universal_solver.UniversalSolverTests.test_solve_outputs_complete_helu_nine_step_loop tests.test_universal_solver.UniversalSolverTests.test_solve_rejects_empty_goal -v`
Expected: PASS。

### Task 4: Skill 3.0 合同、发现和文档

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`
- Modify: `agents/openai.yaml`
- Modify: `CHANGELOG.md`
- Modify: `test-prompts.json`
- Modify: `scripts/quality_check.py`

**Interfaces:**
- Consumes: 新增 CLI 和 3.0 参考资产。
- Produces: 可发现的“通用问题入口”触发说明、河洛九步输出合同、高影响专业接管合同。

- [x] **Step 1: 运行现有 Skill 合同失败测试**

Run: `python3 -m unittest tests.test_universal_solver.UniversalSolverTests.test_skill_explicitly_denies_omniscience_claim -v`
Expected: FAIL，因为 Skill 仍为 2.0 且缺少四个 3.0 标记。

- [x] **Step 2: 升级 Skill 主合同**

标题改为 `# 河图洛书 · Skill 3.0`；说明“所有问题可进入统一入口，但不能保证解决所有问题”；新增通用问题入口、河洛九步现实问题解决引擎、专业接管、分类/求解/选项评估命令和 3.0 参考链接。

- [x] **Step 3: 更新发现元数据与 README**

扩展 description、short_description、default_prompt，覆盖真实需求、决策、诊断、计划、执行、优化、复盘与治理，但仍要求显式调用。README 首屏说明定位、适用领域、命令和安全边界。

- [x] **Step 4: 更新质量检查和提示回归**

把所有 3.0 数据、参考、示例和测试加入 `REQUIRED_FILES`，更新 3.0 markers，并在 `test-prompts.json` 增加通用求解、高影响接管、选项权衡和跨域拆解案例。

- [x] **Step 5: 运行 Skill 合同与质量检查**

Run: `python3 -m unittest tests.test_universal_solver.UniversalSolverTests.test_skill_explicitly_denies_omniscience_claim -v && python3 scripts/quality_check.py .`
Expected: PASS。

### Task 5: 安装载荷与完整回归

**Files:**
- Modify: `scripts/install.py`
- Test: `tests/test_install.py`
- Modify: `docs/validation-report-v3.txt`
- Create: `docs/file-list-v3.txt`
- Create: `docs/file-manifest-v3.sha256`

**Interfaces:**
- Consumes: 完整 3.0 文件集合。
- Produces: 安装后仍可独立运行全部检查的固定载荷。

- [x] **Step 1: 将 3.0 文件加入安装清单**

加入 `data/application-domains.json`、`data/problem-patterns.json`、五个 3.0 reference、两个 3.0 example、`tests/test_universal_solver.py`；排除缓存和运行报告以外的临时文件。

- [x] **Step 2: 运行完整检查**

Run: `python3 scripts/run_checks.py`
Expected: 所有质量、模型、知识和 30 个单元测试通过。

- [x] **Step 3: 独立安装复测**

Run: `python3 scripts/install.py --target <temp>/skills/hetu-luoshu --state-dir <temp>/state`，随后在安装目录运行 `python3 scripts/run_checks.py`。
Expected: 安装成功，安装副本全部检查通过。

- [x] **Step 4: 生成发布证据**

记录版本、文件数量、测试数量、命令结果、未执行的全局安装/推送动作和回滚策略；生成固定文件清单与 SHA-256 清单。
