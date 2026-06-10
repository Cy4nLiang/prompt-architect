# 渲染协议：结果 JSON → HTML 结果页

**HTML 结果页是套件的默认交付方式**。在对话里完成「引导填信息 → 优化」后，把结果渲染成一个 HTML 文件给用户查看和检查——而不是只在对话里贴一段文字，也不是做成"填表单的网页工具"。流程：

1. 对话中按 `pa-deconstruct` 引导用户补齐信息（缺啥问啥，≤3 个问题）。
2. 用 `pa-optimize` / `pa-image` / `pa-video` 产出优化后的 prompt。
3. 写一个结果 JSON，运行渲染脚本生成 HTML，并把 `open <路径>` 给用户。

## 脚本调用（以 SKILL.md 实际所在目录定位，勿硬编码安装路径）

渲染脚本固定位于 prompt-architect skill 目录下的 `scripts/render_result.py`。
**不要硬编码 `.claude/skills/...` 或 `~/.claude/skills/...` 等具体安装路径**——套件可能装在项目级或其他位置。定位规则：

- 在 prompt-architect 内：以**当前实际加载的 SKILL.md 所在目录**为根，脚本即 `<该目录>/scripts/render_result.py`；
- 在子 skill（pa-*）内：从**自身 SKILL.md 实际所在目录**走兄弟路径 `../prompt-architect/scripts/render_result.py`（同步脚本保证整套同目录安装）。

```bash
python3 <prompt-architect 实际目录>/scripts/render_result.py <result.json> docs/优化结果-<slug>.html
```

## 结果 JSON 契约（按需填，缺的省略）

```json
{
  "kind": "text | image | video",
  "lang": "zh(默认) | en——en 时整页 UI（节标题/按钮/重发话术）切英文，供英文用户交付",
  "title": "周报生成器 / 商品白底主图 / 带货短视频 …",
  "raw_request": "用户原话",
  "images": ["/abs/path/参考图.jpg"],
  "intent": { "why": "真实目的", "success_criteria": ["…"], "non_goals": ["…"] },
  "signature": { "inputs": ["字段: 说明"], "outputs": ["字段: 说明"] },
  "prompts": [ { "label": "正面主图", "content": "优化后的完整 prompt", "content_zh": "中文平行版(可选)", "note": "可选说明" } ],
  "candidates": [ { "label": "候选 A · persona-driven", "strategy": "persona-driven", "hypothesis": "用强人设声线改善语感判据", "tradeoff": "风格张力强 / 信息密度低", "content": "完整候选 prompt", "content_zh": "中文平行版(可选)", "score": 0.86, "recommended": true } ],
  "vendor": { "name": "OpenAI gpt-image-2", "howto": "上传参考图+粘贴+选比例", "params": "进阶参数" },
  "shot_plan": [ { "shot": "1", "duration": "0-5s", "framing": "medium close-up", "camera": "slow push-in", "action": "动作要点", "audio": "该镜头音频/台词", "transition": "match cut" } ],
  "audio_spec": { "music": "BGM 风格", "ambience": "环境音", "sfx": "音效", "dialogue": [ { "speaker": "说话人", "line": "逐字台词", "tone": "情绪" } ], "note": "厂商无原生音频时注明需后期配" },
  "asset_plan": [ { "asset": "图1", "role": "人物锚定", "syntax": "@图1" } ],
  "checklist": [ { "item": "Signature 存在", "pass": true } ],
  "rationale": ["改了什么 / 为什么"]
}
```

## 页面结构与填写要点

HTML 结果页含：原始请求 → **参考图展示（`images`，图像类）** → 解构出的意图（先核对抓得对不对）→（图像）推荐模型与用法 → 优化后 prompt（**批量复制全部** + 每条单独复制；若给了 `content_zh` 则渲染**中英对比视窗**：英文喂 gpt-image-2/MJ/Nano、中文便于读懂/修改或喂即梦）→ 质量检查清单（可勾选）→ 变更理由。

- **多候选路径**（pa-optimize 3 候选 / pa-image 3 变体 / pa-video 2 候选）：用 `candidates` 键代替 `prompts`——页面渲染**多方案 grid 对比**，每卡标注 strategy 徽章、hypothesis、tradeoff（必填——用户要知道每个方案牺牲了什么）与 pa-eval 得分，`recommended: true` 的 winner 高亮描边；单候选路径继续用 `prompts`。
- 图像类务必填 `images`（参考图绝对路径）让用户在页面里直接看到产品。
- 图像 prompt 建议同时给 `content`（英文）+ `content_zh`（中文），开启中英对比。
- 视频类按需填 `shot_plan` / `audio_spec` / `asset_plan`（单镜头、无声、纯文生时省略对应块）；参考素材同样放 `images`。
- 文本类把 `intent / signature / optimized_prompt(放入 prompts) / checklist_result(放入 checklist) / change_rationale(放入 rationale)` 映射进上述键。
