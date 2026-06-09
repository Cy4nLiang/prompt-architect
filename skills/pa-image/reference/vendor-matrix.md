# 图像生成厂商优化方案矩阵

> 数据截至 2026-06，各家迭代快，**最终以官方最新文档为准**。
> 核心结论：**选错厂商比写错 prompt 更致命**——先按"要不要复刻具体主体 / 要不要可控 / 中英文 / 美学还是合规"选厂商，再按该家约定写词。

## 一、能力矩阵

| 厂商 / 模型 | 图生图 / 参考图 | negative prompt | 画幅写法 | 参考/权重语法 | 保真特长 | prompt 风格 | 商标/内容策略 | 最适合 |
|---|---|---|---|---|---|---|---|---|
| **OpenAI · gpt-image-2** | ✅ `images.edit`，多参考图 | ❌ 无 → 排除项写进正文 | `size="WxH"`，W/H 均 ÷16，比例 1:3~3:1 | 无权重语法，自然语言；**不要传 input_fidelity**(自动高保真) | 指令遵循最强、文字渲染好 | 长自然语言 | 严，商标/名人可能拒绝或改写 | 电商图、带指令的精确编辑、合规要求高 |
| **Google · Nano Banana Pro**(gemini-3-pro-image) | ✅ 多至 ~14 张参考图、多轮对话编辑 | ❌ 无 → 自然语言描述排除 | 参数/自然语言指定，原生 4K | 自然语言，多图融合("把 A 的衣服穿到 B 上") | **主体/角色一致性 #1**、物理材质光照、4K | 对话式自然语言 | 较严，带 SynthID 水印 | 跨图一致性、多参考融合、对话迭代、产品/角色 |
| **即梦 · Seedream 5**(字节) | ✅ 参考图/垫图，多至 ~10 张融合，强度可调 | 部分流程有"排除"，多数靠正文 | 预设比例(1:1/3:4/16:9 等) | 中文原生，参考强度滑杆 | 参考保真强、**中文文字渲染**、海报排版 | 中文自然语言 | 国内合规口径 | 中文海报/电商、国内平台、批量出图 |
| **Midjourney v7** | 仅"图像提示"(图 URL)+ `--iw`；`--cref`角色 / `--sref`风格 | ✅ `--no xxx` | `--ar 3:4` 等 | `--iw`(图权重) `--cref`(角色一致) `--sref`(风格一致) `--stylize` `--chaos` | **美学/氛围最强**；但**无法精确复刻 logo/印花/具体衣服** | 短语+关键词+参数 | 不复刻商标 | lookbook 氛围、海报美学、灵感探索 |
| **Stable Diffusion / Flux + ComfyUI** | ✅ img2img / ControlNet / IPAdapter / **虚拟试穿(IDM-VTON,CatVTON)** | ✅ 真·独立负面(SD)；Flux 偏自然语言 | 任意尺寸 | `(token:1.3)` 权重、ControlNet 约束、LoRA、seed 可复现 | **像素级保真 + 完全可控 + 可复现**（虚拟试穿直接贴衣服像素，不重画） | SD=tag 堆叠；Flux=自然语言 | 本地无策略限制(责任在用户) | 必须 100% 复刻商品/印花、批量、可复现、工作流自动化 |

## 二、怎么选（决策指引）

| 你的首要诉求 | 选 | 理由 |
|---|---|---|
| **100% 复刻某件具体商品/印花/logo** | ComfyUI 虚拟试穿(IDM-VTON/CatVTON) > Nano Banana Pro / Seedream 多参考 | 试穿是贴像素不重画；重绘式模型对商标可能改写 |
| 带指令的精确编辑 + 强一致性 | Nano Banana Pro 或 gpt-image-2 | 指令遵循 + 主体一致性最强 |
| 中文海报 / 国内电商 / 中文文字 | 即梦 Seedream | 中文原生 + 文字渲染 + 合规 |
| 纯美学 / lookbook 氛围（不要求精确复刻） | Midjourney v7 | 美学天花板，但别指望复刻 logo |
| 完全可控 / 可复现 / 批量自动化 | SD / Flux + ComfyUI | 负面 + ControlNet + LoRA + seed |
| 合规优先（避免商标麻烦） | gpt-image-2 / Nano Banana | 策略严，但更"安全" |

**电商模特上身这类（既要保真又要量产）**：首选 **Nano Banana Pro / gpt-image-2**（参考图 + 指令）做主图；**ComfyUI 虚拟试穿**做"印花必须分毫不差"的兜底；**Midjourney** 只做场景氛围 lookbook。

> 网页/App 用户读法：表里的 API/工作流术语（images.edit、IPAdapter、ControlNet、LoRA、seed、--iw）是给开发/进阶用户的；你只需关心「图生图/参考图、有没有 negative、画幅怎么选、中英文」四列，其余在网页版里都是"上传图 + 选比例 + 填描述"。

## 三、同一条 prompt 如何按厂商改写（示例：模特上身电商图，主体可替换为任意产品/画面）

把通用 prompt 落到各家时只改这几处：

- **OpenAI gpt-image-2**：排除项写进正文（无 negative）；`images.edit(image=[ref...], size="1152x1536", quality="high")`；不传 input_fidelity。
- **Nano Banana Pro**：上传参考图 + 自然语言"keep the garment identical to the reference, change only the model/scene"；多轮里可继续"换个姿势/换场景"保持一致。
- **即梦 Seedream**：用中文 prompt + 上传衣服图作参考(强度调到既保印花又能换上身)；选 3:4。
- **Midjourney v7**：`画面描述 --ar 3:4 --no text,watermark,extra logo --stylize 100`；衣服图作 image prompt + `--iw 2`（但仍可能改印花，慎用于精确复刻）。
- **SD/Flux + ComfyUI**：正面 prompt + **独立 negative**（`text, watermark, extra logo, deformed hands, mannequin`）；衣服走 **IPAdapter/虚拟试穿**锁定 region；`(garment graphic:1.2)` 加权；固定 seed 复现。

## 四、通用纪律（所有厂商都成立）
- 要复刻具体主体 → **永远优先参考图/图生图**，文字描述只是补充。
- **negative 不存在的家**，把排除项写进正文（"no added text, undistorted hands…"）。
- **画幅用合法值**，别写模型不认的比例。
- 动作越大 / 越多参考融合 → 保真越易漂移：精确复刻图选小动作、主体正对镜头。
- **出图后必做保真自检**，漂移就重抽或升级到更强保真的厂商（这是 precise-retrieval 的图像版闭环）。
