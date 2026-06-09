# Prompt 质量检查清单

由 `pa-optimize` 在产出前运行的门禁，每项标注来源框架。**全过 = 该 prompt 可发布**。
未过项要么修，要么在 `change_rationale` 里说明为何豁免。

## 意图 & 契约
- [ ] **Signature 存在** — 识别出类型化 inputs + 类型化 outputs，而非散文（DSPy）
- [ ] **WHY 已捕获** — 底层 job-to-be-done、成功判据、Non-Goals 已陈述（LangGPT）
- [ ] **输出形态已分类** — scalar/choice/list/object/union 已选；开放式问法在合适处收敛为 enum（guidance, outlines, 12-factor）
- [ ] **不开心路径已建模** — "无答案/无法满足"是类型化结果，而非被迫瞎猜（instructor Maybe, 12-factor）
- [ ] **假设已浮现并确认** — 无阻塞性开放问题残留（Context-Engineering, LangGPT）

## 结构 & 渲染
- [ ] **system 与 user 分离** — 稳定指令 vs 可变数据是不同块（Prompty, ell, promptflow）
- [ ] **三块不融合** — field-description / field-structure / objective 分开渲染（DSPy）
- [ ] **约束写成清单** — 而非埋在散文里（guardrails）
- [ ] **变量已模板化** — `{{占位符}}` 逐字保留，prompt 可复用（prompt-optimizer, YiVal）
- [ ] **可追溯 + 奥卡姆** — 每条子句都映射到某个目标/约束；无 prompt 臃肿（LangGPT）

## 输出强制
- [ ] **输出契约被注入** — 而非描述；显式 schema/enum/regex 在场（BAML, instructor, 12-factor）
- [ ] **完成是显式的** — stop sentinel / "何时算完" 已指定（LMQL）
- [ ] **选了最紧可行约束** — 按模型能力：约束解码 > provider schema > 校验-reask（outlines, instructor, mirascope）
- [ ] **Few-shot 锚点（条件项）** — 若格式非平凡 → 配示例 + 不确定规则 + 示例已验证正确；格式平凡（scalar/prose）则 N/A（guardrails, promptbase）

## 安全 & 评测
- [ ] **用户文本围成 DATA** — 无法注入/覆盖角色标记或指令（prompt-optimizer, Prompty, promptflow）
- [ ] **意图被保留** — 改写没有改变用户要求的行为（promptfoo）
- [ ] **eval 可检查** — 成功由 rubric/judge `{reason,pass,score}` 衡量，而非凭感觉（promptfoo, DSPy, YiVal）
- [ ] **变更理由已记录** — 每处变更附假设以便审计（promptfoo, AdalFlow）
