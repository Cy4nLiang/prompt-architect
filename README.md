# prompt-architect

> 一套 Claude Code agent-skill 套件：把「模糊请求 → 真实意图 → 精准结构化 prompt → 可查看检查的 HTML 结果页」落地。
> 同时覆盖**文字优化**与**文生图优化**，运营/产品/不懂代码的同学也能用。

核心理念（蒸馏自对 GitHub 上 20 个 top prompt-engineering 框架的源码级分析）：
**prompt 不是被写出来的散文，而是从「类型化 I/O 契约」编译出的产物——人拥有意图，循环拥有措辞。**

---

## 安装

**方式一：脚本一键装（推荐）**
```bash
./install.sh            # 装到全局 ~/.claude/skills/（所有项目可用）
./install.sh --project  # 装到当前项目 ./.claude/skills/（仅本项目）
```

**方式二：手动复制**
```bash
cp -R skills/* ~/.claude/skills/          # 全局
# 或
cp -R skills/* /your/project/.claude/skills/   # 单项目
```

装好后重开 Claude Code，对它说 `用 prompt-architect 优化…` 即可。

---

## 怎么用

1. 在 Claude Code 里说出需求：
   - `用 prompt-architect 优化：我想要了解最新的 X`
   - `用 prompt-architect 帮我把这个商品放进真实场景：/path/to/product.jpg`
2. 它会**引导你补几个关键信息**（缺啥问啥，≤3 个问题）。
3. 产出一个 **HTML 结果页**（含：原始请求 → 参考图 → 意图核对 → 推荐模型&用法 → 优化后 Prompt〔批量复制 + 中英对比 + 单条复制〕→ 质量检查清单〔可勾选〕→ 变更理由 → **不达标一键重发指令**）。打开即可查看、复制、逐条检查。

> 不会写代码的同学：先读 `skills/prompt-architect/reference/ops-onboarding.md`（运营上手指南）。

---

## 结构

```
skills/
├── prompt-architect/            ← 入口路由 + 共享资源
│   ├── SKILL.md                 ← 路由：围栏输入→判意图→分派；含「产出 HTML 结果页」规范
│   ├── reference/
│   │   ├── ir-schema.md         ← 意图表示 IR（套件共享的数据契约）
│   │   ├── prompt-template.md   ← 蒸馏出的结构化 prompt 模板
│   │   ├── quality-checklist.md ← prompt 质量检查清单
│   │   └── ops-onboarding.md    ← 运营同事上手指南
│   └── scripts/
│       └── render_result.py     ← 结果渲染器：JSON → HTML 结果页
├── pa-deconstruct/SKILL.md      ← 意图挖掘（解构真实目的，强制类型化 Signature）
├── pa-optimize/SKILL.md         ← 改写/脚手架（编译成结构化 prompt）
├── pa-precise-retrieval/SKILL.md← 精准取数（约束/schema/校验-reask）
└── pa-image/                    ← 文生图优化
    ├── SKILL.md
    └── reference/vendor-matrix.md   ← 厂商选择矩阵（gpt-image-2/Nano Banana/即梦/MJ/SD）

docs/
└── prompt-engineering-knowledge.html  ← 知识库：20 框架的架构与核心理论
```

**流水线**：`pa-deconstruct`（产出 IR）→ `pa-optimize` / `pa-image`（消费 IR、产出 prompt）→ `pa-precise-retrieval`（图像/精确场景强制保真）→ `render_result.py`（渲染 HTML 结果页）。各子 skill 也可被单独触发。

---

## 文生图：厂商怎么选

| 诉求 | 选 |
|---|---|
| 必须 100% 复刻具体商品/印花/logo | ComfyUI 虚拟试穿 ＞ Nano Banana Pro / 即梦 多参考 |
| 指令精确编辑 + 强一致性 | Nano Banana Pro / gpt-image-2 |
| 中文海报 / 国内电商 | 即梦 Seedream |
| 纯美学 lookbook | Midjourney v7 |
| 完全可控 / 可复现 / 批量 | SD / Flux + ComfyUI |

详见 `skills/pa-image/reference/vendor-matrix.md`。

---

## 想了解原理

打开 `docs/prompt-engineering-knowledge.html` —— 8 范式 / 12 原则 / 标准管线 / 12 设计模式 / 20 框架逐项目卡片。

---

*由 Claude Code 生成与维护。*
