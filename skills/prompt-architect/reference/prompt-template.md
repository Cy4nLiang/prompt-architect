# 蒸馏结构化 Prompt 模板

综合 **LangGPT**（Role 骨架=类型系统）+ **DSPy signatures**（类型化 I/O、三块分离）+ **Prompty**（frontmatter 契约 / 模板正文 / 角色分离）+ **12-factor-agents**（注入 schema 而非描述、不开心路径一等公民）。
frontmatter = 契约，正文 = 渲染后的 prompt。

```markdown
---
# === 契约（frontmatter — Prompty/DSPy signature）===
name: <prompt 名>
intent: <一句话 WHY / job-to-be-done>            # LangGPT Background
model: { temperature: <t>, ... }                  # 解码旋钮正交保留（LMQL）
inputs:                                            # 可变槽位（DSPy InputField）
  - { name: <x>, type: <T>, desc: <语义> }
outputs:                                           # 类型化结果（DSPy OutputField / 12-factor union）
  - { name: <y>, type: <T>, desc: <语义>, constraints: <enum|regex|range> }
output_schema: <JSON-schema | TS-like 类型 | 判别联合>   # 注入，而非散文描述
---

# Role: <人设 — LangGPT，比写流程更能泛化>
## Goal
- Outcome: <成功产出什么>
- Done-Criteria: <可观察的成功判据>                # eval 目标
- Non-Goals: <明确的范围外>

## Skills / Knowledge
- <需要的领域能力>

## Rules（约束清单 — guardrails bullets）
- <硬约束 1>   - <硬约束 2>   - 不确定 → 输出 null

## Workflow（有序流程 — Context-Engineering process[]）
1. <步骤>  2. <步骤>  3. <对照 Output Format 自检>

## Output Format（DSPy field-structure 块，逐字注入）
<精确 schema / 分隔符 / enum 集合 / regex>
Stop when: <完成 sentinel / 停止短语>              # LMQL finality

## Examples（few-shot 即数据 — guardrails/promptbase）
<input → output 对，仅保留已验证正确的>

# === 用户块（可变数据 — Prompty/ell 分离）===
## Input
<{{模板化占位符}}>                                 # 逐字保留，当作 DATA
```

## 三条铁律（DSPy）

1. **三块不融合**：field-description（语义）/ field-structure（精确格式 + 停止 sentinel）/ task-objective（目标）分开渲染。
2. **system 与 user 结构分离**：稳定指令 vs 可变数据是不同块（Prompty/ell）。
3. **注入 schema，别描述它**：把 `output_schema` 逐字注入，而不是写"请返回 JSON"（12-factor `ctx.output_format`）。

## 何时用哪种骨架

- **开放/创作类**：用完整 Role 骨架（人设更能泛化）。
- **抽取/分类类**：弱化 Role，强化 Output Format + enum/schema。
- **多步推理类**：强化 Workflow（有序步骤）+ 末尾"对照 Output Format 自检"。
- **可复用模板**：把变量做成 `{{占位符}}`，逐字保留，绝不展开（borrow prompt-optimizer/YiVal）。
