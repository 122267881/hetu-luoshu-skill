# 河图洛书 Skill 3.0 验证报告

验证日期：2026-07-30
版本：3.0.0

## 覆盖范围

- 河图与洛书数理模型。
- 10 个来源、25 个术语、30 条可追溯主张。
- 16 个现实应用领域和 10 种问题类型。
- 通用问题分类、高影响路由、加权决策和河洛九步求解。
- 外部内容无指令权、医疗/金融/法律/危机/命理边界。
- 安装、替换、备份、恢复、哈希、路径与符号链接安全。

## TDD 证据

3.0 初始基线中，`classify`、`solve` 和 `evaluate-options` 子命令不存在，通用求解测试失败；实现后同一组测试通过，并完成全量回归。

## 源码目录完整检查

```text
==> quality
Quality check passed.
==> models
hetu: PASS
luoshu: PASS
==> knowledge
Knowledge base: PASS
sources=10 terms=25 claims=30 symmetries=8 domains=16 patterns=10
==> tests
test_dry_run_does_not_create_target (test_install.InstallerTests.test_dry_run_does_not_create_target) ... ok
test_install_and_restore_manifest_backup (test_install.InstallerTests.test_install_and_restore_manifest_backup) ... ok
test_installed_package_runs_full_checks (test_install.InstallerTests.test_installed_package_runs_full_checks) ... ok
test_rejects_nested_state_and_target (test_install.InstallerTests.test_rejects_nested_state_and_target) ... ok
test_restore_rejects_arbitrary_directory_and_never_executes_script (test_install.InstallerTests.test_restore_rejects_arbitrary_directory_and_never_executes_script) ... ok
test_symlinked_source_directory_is_rejected (test_install.InstallerTests.test_symlinked_source_directory_is_rejected) ... ok
test_claim_auditor_flags_absolute_and_high_impact_claims (test_knowledge_system.KnowledgeSystemTests.test_claim_auditor_flags_absolute_and_high_impact_claims) ... ok
test_cli_lookup_returns_structured_term (test_knowledge_system.KnowledgeSystemTests.test_cli_lookup_returns_structured_term) ... ok
test_every_luoshu_symmetry_remains_magic (test_knowledge_system.KnowledgeSystemTests.test_every_luoshu_symmetry_remains_magic) ... ok
test_knowledge_base_claims_are_traceable (test_knowledge_system.KnowledgeSystemTests.test_knowledge_base_claims_are_traceable) ... ok
test_luoshu_has_eight_unique_dihedral_symmetries (test_knowledge_system.KnowledgeSystemTests.test_luoshu_has_eight_unique_dihedral_symmetries) ... ok
test_model_template_is_measurable_not_divinatory (test_knowledge_system.KnowledgeSystemTests.test_model_template_is_measurable_not_divinatory) ... ok
test_v2_required_assets_exist (test_knowledge_system.KnowledgeSystemTests.test_v2_required_assets_exist) ... ok
test_hetu_pairs_differ_by_five (test_models.ModelTests.test_hetu_pairs_differ_by_five) ... ok
test_hetu_totals (test_models.ModelTests.test_hetu_totals) ... ok
test_luoshu_magic_constant (test_models.ModelTests.test_luoshu_magic_constant) ... ok
test_luoshu_opposites (test_models.ModelTests.test_luoshu_opposites) ... ok
test_external_content_has_no_instruction_authority (test_skill_contract.SkillContractTests.test_external_content_has_no_instruction_authority) ... ok
test_meta_engine_retains_dao_capabilities (test_skill_contract.SkillContractTests.test_meta_engine_retains_dao_capabilities) ... ok
test_quality_contract (test_skill_contract.SkillContractTests.test_quality_contract) ... ok
test_safety_cases_exist (test_skill_contract.SkillContractTests.test_safety_cases_exist) ... ok
test_classify_routes_product_request (test_universal_solver.UniversalSolverTests.test_classify_routes_product_request) ... ok
test_domain_catalog_has_broad_real_world_coverage (test_universal_solver.UniversalSolverTests.test_domain_catalog_has_broad_real_world_coverage) ... ok
test_high_impact_request_is_routed_not_solved_as_certainty (test_universal_solver.UniversalSolverTests.test_high_impact_request_is_routed_not_solved_as_certainty) ... ok
test_option_evaluator_uses_weighted_tradeoffs (test_universal_solver.UniversalSolverTests.test_option_evaluator_uses_weighted_tradeoffs) ... ok
test_problem_patterns_cover_full_lifecycle (test_universal_solver.UniversalSolverTests.test_problem_patterns_cover_full_lifecycle) ... ok
test_skill_explicitly_denies_omniscience_claim (test_universal_solver.UniversalSolverTests.test_skill_explicitly_denies_omniscience_claim) ... ok
test_solve_outputs_complete_helu_nine_step_loop (test_universal_solver.UniversalSolverTests.test_solve_outputs_complete_helu_nine_step_loop) ... ok
test_solve_rejects_empty_goal (test_universal_solver.UniversalSolverTests.test_solve_rejects_empty_goal) ... ok
test_v3_required_assets_exist (test_universal_solver.UniversalSolverTests.test_v3_required_assets_exist) ... ok

----------------------------------------------------------------------
Ran 30 tests in 12.757s

OK
All checks passed.
```

## 独立安装

```text
Installed 48 files to /tmp/tmp.EvZQUqATKs/skills/hetu-luoshu
```

## 安装副本完整检查

```text
==> quality
Quality check passed.
==> models
hetu: PASS
luoshu: PASS
==> knowledge
Knowledge base: PASS
sources=10 terms=25 claims=30 symmetries=8 domains=16 patterns=10
==> tests
test_dry_run_does_not_create_target (test_install.InstallerTests.test_dry_run_does_not_create_target) ... ok
test_install_and_restore_manifest_backup (test_install.InstallerTests.test_install_and_restore_manifest_backup) ... ok
test_installed_package_runs_full_checks (test_install.InstallerTests.test_installed_package_runs_full_checks) ... ok
test_rejects_nested_state_and_target (test_install.InstallerTests.test_rejects_nested_state_and_target) ... ok
test_restore_rejects_arbitrary_directory_and_never_executes_script (test_install.InstallerTests.test_restore_rejects_arbitrary_directory_and_never_executes_script) ... ok
test_symlinked_source_directory_is_rejected (test_install.InstallerTests.test_symlinked_source_directory_is_rejected) ... ok
test_claim_auditor_flags_absolute_and_high_impact_claims (test_knowledge_system.KnowledgeSystemTests.test_claim_auditor_flags_absolute_and_high_impact_claims) ... ok
test_cli_lookup_returns_structured_term (test_knowledge_system.KnowledgeSystemTests.test_cli_lookup_returns_structured_term) ... ok
test_every_luoshu_symmetry_remains_magic (test_knowledge_system.KnowledgeSystemTests.test_every_luoshu_symmetry_remains_magic) ... ok
test_knowledge_base_claims_are_traceable (test_knowledge_system.KnowledgeSystemTests.test_knowledge_base_claims_are_traceable) ... ok
test_luoshu_has_eight_unique_dihedral_symmetries (test_knowledge_system.KnowledgeSystemTests.test_luoshu_has_eight_unique_dihedral_symmetries) ... ok
test_model_template_is_measurable_not_divinatory (test_knowledge_system.KnowledgeSystemTests.test_model_template_is_measurable_not_divinatory) ... ok
test_v2_required_assets_exist (test_knowledge_system.KnowledgeSystemTests.test_v2_required_assets_exist) ... ok
test_hetu_pairs_differ_by_five (test_models.ModelTests.test_hetu_pairs_differ_by_five) ... ok
test_hetu_totals (test_models.ModelTests.test_hetu_totals) ... ok
test_luoshu_magic_constant (test_models.ModelTests.test_luoshu_magic_constant) ... ok
test_luoshu_opposites (test_models.ModelTests.test_luoshu_opposites) ... ok
test_external_content_has_no_instruction_authority (test_skill_contract.SkillContractTests.test_external_content_has_no_instruction_authority) ... ok
test_meta_engine_retains_dao_capabilities (test_skill_contract.SkillContractTests.test_meta_engine_retains_dao_capabilities) ... ok
test_quality_contract (test_skill_contract.SkillContractTests.test_quality_contract) ... ok
test_safety_cases_exist (test_skill_contract.SkillContractTests.test_safety_cases_exist) ... ok
test_classify_routes_product_request (test_universal_solver.UniversalSolverTests.test_classify_routes_product_request) ... ok
test_domain_catalog_has_broad_real_world_coverage (test_universal_solver.UniversalSolverTests.test_domain_catalog_has_broad_real_world_coverage) ... ok
test_high_impact_request_is_routed_not_solved_as_certainty (test_universal_solver.UniversalSolverTests.test_high_impact_request_is_routed_not_solved_as_certainty) ... ok
test_option_evaluator_uses_weighted_tradeoffs (test_universal_solver.UniversalSolverTests.test_option_evaluator_uses_weighted_tradeoffs) ... ok
test_problem_patterns_cover_full_lifecycle (test_universal_solver.UniversalSolverTests.test_problem_patterns_cover_full_lifecycle) ... ok
test_skill_explicitly_denies_omniscience_claim (test_universal_solver.UniversalSolverTests.test_skill_explicitly_denies_omniscience_claim) ... ok
test_solve_outputs_complete_helu_nine_step_loop (test_universal_solver.UniversalSolverTests.test_solve_outputs_complete_helu_nine_step_loop) ... ok
test_solve_rejects_empty_goal (test_universal_solver.UniversalSolverTests.test_solve_rejects_empty_goal) ... ok
test_v3_required_assets_exist (test_universal_solver.UniversalSolverTests.test_v3_required_assets_exist) ... ok

----------------------------------------------------------------------
Ran 30 tests in 12.049s

OK
All checks passed.
```

## 结论边界

这些结果证明发布包的确定性结构、脚本合同和回归测试通过；不证明河洛方法可以保证现实成功，也不替代具体领域的真实数据、专业判断、现实执行和长期效果验证。
