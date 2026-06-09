---
name: pa-optimize
description: 把意图表示 IR 编译成精准、结构化的 prompt。用 Role/Goal/Rules/Workflow/OutputFormat 骨架渲染，遵循三块分离、注入 schema 而非描述、few-shot 即数据、变量模板化、可追溯剪枝；若带有上一轮反馈则执行 critic→rewriter 两段最小编辑（保留 best/rejected 记忆、回归即回退）。产出可直接使用的 prompt + 变更理由。当 IR 已就绪需要产出可用 prompt、或用户要"改写/优化/精修/迭代"已有 prompt 时使用。
---

# pa-optimize · 改写 / 脚手架

> 套件的 "Adapter + TGDOptimizer"：把 IR 契约渲染成结构化 prompt；若有历史尝试，则做一次 critic→rewriter。
> 借鉴 DSPy Adapter、LangGPT 骨架、AdalFlow 槽位语法、BAML schema 注入、guardrails 约束清单、TextGrad 角色分离、promptfoo 假设。

## 触发
- IR 有完整 `signature` + `intent` 且无阻塞 `open_questions`；
- 或 intent=`iterate` 且 IR 中已有 prior `optimized_prompt` + `eval_feedback`（由 `pa-precise-retrieval` 在 eval 失败时回写）。

## 步骤（改写路径）

1. **选骨架** — 套用蒸馏结构化 prompt 模板：system 块（Role/Goal/Rules/Workflow/OutputFormat）+ user 块（数据槽位）。见 [../prompt-architect/reference/prompt-template.md](../prompt-architect/reference/prompt-template.md)。
2. **三块分离，绝不融合**（DSPy）：field-description（语义）/ field-structure（精确格式 + 停止 sentinel）/ task-objective。
3. **分解后再组合**（guidance / Context-Engineering）：把复杂输出拆成独立指定的子部分，再拼回。
4. **约束写成 bullet 清单**（guardrails `validator.to_prompt`），别埋进散文。
5. **few-shot 即数据**（guardrails / promptbase / DSPy demos）：挂已验证正确的 input→output 对，并加显式不确定规则（"不确定就返回 null"）。
6. **注入输出契约**（BAML / instructor）：把 `output_contract.schema` 逐字作为主指令注入；优先紧凑 TS-like / JSON-schema，而非"请返回 JSON"。
7. **模板化变量**（prompt-optimizer / YiVal）：保留 `{{占位符}}` 为可复用槽位，逐字保留，绝不展开。
8. **可追溯 + 奥卡姆剪枝**（LangGPT）：删掉任何无法映射到某个目标/约束的子句，防 prompt 臃肿。

## 步骤（迭代路径，带反馈时）

执行**两段 critic→rewriter**（TextGrad / AdalFlow 角色硬分离）：
1. **critic**：只产出一段"文本梯度"——当前 prompt 哪里失败、与期望差什么，**不改写**。
2. **rewriter**：只应用**一种**最小编辑法（新增 / 加示例 / 改写替换 / 删除），不大改。
3. 保留 best-so-far + failed-attempts 记忆（YiVal OPRO）；**re-eval 回归就回退**（TextGrad/AdalFlow validation-gate）。
4. 重复反馈时强制更大改动，避免在同一处打转。

## 输出契约
- `optimized_prompt`：role-tagged 消息（system + user），含输出格式/schema 块、约束清单、≤K 个 few-shot 对、保留的 `{{占位符}}`、停止 sentinel；无开头废话、无多余代码围栏（prompt-optimizer）。
- `change_rationale`（promptfoo 假设）：列出改了什么、为什么，每条可追溯到 IR 的某个目标。
- **意图保留**是硬约束：改写**不得改变**用户要求的行为（promptfoo `OPTIMIZE_PROMPT` 铁律）。

## 发布门禁
产出前对照 [../prompt-architect/reference/quality-checklist.md](../prompt-architect/reference/quality-checklist.md) 逐项过；
未过项要么修，要么在 `change_rationale` 注明豁免理由。

## 何时交棒
若 `output_contract.shape ≠ scalar`（即 choice/list/object/discriminated_union）或 intent=`extract` → 交棒 `pa-precise-retrieval` 做强制与 eval 门禁。

## 产出 HTML 结果页
完成后，把 `intent / signature / optimized_prompt / checklist_result / change_rationale` 写成结果 JSON，用 `../prompt-architect/scripts/render_result.py` 渲染成 HTML 供用户查看与检查（结构见 prompt-architect 的「产出 HTML 结果页」）。
