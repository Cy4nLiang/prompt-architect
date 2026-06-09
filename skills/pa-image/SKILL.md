---
name: pa-image
description: 图像生成 prompt 优化。把"想要一张什么图"的模糊需求编译成精准的图像生成 prompt——确定主体/外观/动作/构图/光线/风格/画幅/保真约束与排除项，区分文生图(text-to-image)与图生图(参考图保真)，并按目标厂商(OpenAI gpt-image-2 / Google Gemini·Nano Banana Pro / 即梦·Seedream / Midjourney / Stable Diffusion·Flux·ComfyUI)的约定适配 negative prompt、画幅写法、参考图与权重语法。当用户要生成/优化图片、做电商图/海报/插画/lookbook/模特上身图、或问"用哪个模型、图片 prompt 怎么写"时使用。
---

# pa-image · 图像生成 prompt 优化

> `pa-optimize` 的图像专用版：把 IR 编译成图像生成 prompt，并**按目标厂商适配**。
> 文本 prompt 的"输出契约=schema"，在图像里换成**主体保真 + 构图/光线/风格 + 画幅 + 排除项**；
> 而 negative prompt、参考图、画幅写法**各厂商完全不同**——选错厂商或写法，再好的描述也白费。

## 适用场景（不只是电商）
适用于**任何图片需求**：海报 / Banner / 社媒配图 / 插画 / 商品图 / 模特上身 / PPT 封面 / 头像等。"主体"只是一个填空项，换成你的产品/画面即可——本 skill 与具体品牌无关。

## 在网页版 / App 里怎么用（不会写代码时）
最省事：用网页版工具 `../../docs/prompt-builder.html` 填空出 prompt。手动时记住三件事：
1. **要复刻某张图**（商品/印花/脸/logo）→ 在网页版直接**上传那张参考图**，并写一句"保持它与参考图完全一致，只改背景/姿势"；
2. **画幅**→ 在工具界面**选比例**（3:4/1:1/16:9），不用记尺寸数字；
3. 下文的 `images.edit / IPAdapter / --ar / seed` 等是给开发/进阶用户的，网页版用户可忽略。

## 为什么单独一个 skill（与文本 prompt 的关键区别）
- 输出是**给图像模型**的文本，不是给 LLM 的指令；"约束输出空间"= 锁主体保真 + 排除项。
- **negative prompt 不通用**：SD/Midjourney 有独立负面；gpt-image-2/Gemini 没有，必须写进正文。
- **保真靠参考图**：要复刻"这件具体的衣服/这张脸/这个 logo"，纯文生图做不到，必须图生图/参考图/虚拟试穿。
- **画幅是受限枚举**：每家合法尺寸/写法不同（见矩阵）。

## 图像 prompt 解剖（10 要素，逐项填，缺则标注或用默认）
1. **主体 Subject**：是谁/是什么（模特画像、商品、角色）
2. **外观 Appearance**：发型/肤色/年龄/材质/颜色——要保真的部分点名
3. **动作/姿态 Action/Pose**：站姿/动态/表情
4. **构图/景别 Composition**：全身/半身/特写、机位、角度
5. **环境/背景 Environment**：白底/场景/虚化
6. **光线 Lighting**：棚拍柔光/golden-hour/硬光
7. **风格/媒介 Style/Medium**：写实摄影/插画/3D；镜头(85mm)
8. **技术/画质 Technical**：高清、景深、true-to-life color
9. **画幅 Aspect**：按厂商合法值
10. **保真约束 + 排除项**：哪些必须与参考一致；不要出现什么

## 两条主轴（先定这两条，再写词）
- **文生图 vs 图生图**：要复刻具体主体 → 必须图生图/参考图（强度可调）；只要"风格类似" → 文生图够。
- **negative 支持？**：支持(SD/MJ) → 排除项进负面；不支持(gpt-image-2/Gemini/多数即梦流程) → 排除项写进正文。

## 步骤
1. **接 IR**：从 `pa-deconstruct` 拿主体/风格/用途/保真要求（没有就先补一轮解构）。
2. **判主轴**：要不要保真具体主体？→ 图生图 + 参考图。
3. **选厂商**：按需求查 [reference/vendor-matrix.md](reference/vendor-matrix.md)（要复刻商品/印花、要指令编辑、中文海报、纯美学、还是要完全可控），用户没指定就给 2 个推荐 + 理由。
4. **按该厂商约定编译**：套下方模板，按矩阵处理 negative(进正文 or 独立)、画幅(合法值)、参考图与权重语法。
5. **保真 + 排除**：把"必须一致"的主体特征点名 `reproduce exactly, do not alter`；排除项按厂商落位。
6. **自检闭环**（precise-retrieval 的图像版）：出图后核对保真点(印花/脸/色/版型)，漂移就重抽（提高参考强度 / 重申 do-not-alter / 换更强保真厂商）。
7. **可复用**：把会变的做成 `{{占位符}}`（主体/场景/画幅），产出可批量的模板。

## 通用图像 prompt 模板（厂商无关骨架，再按矩阵适配）
```text
[主体] a <subject with key appearance>, <action/pose>, <expression>.
[保真] reproduce <the garment/face/logo> exactly from the reference — do not change
       color, shape, text, or layout; keep all text/graphics crisp.
[构图] <full-body / waist-up / close-up>, <angle>, subject centered.
[环境] <white seamless studio bg / outdoor scene>, <depth of field>.
[光线] <soft shadowless softbox / warm golden-hour>.
[风格] photorealistic e-commerce/editorial photography, 85mm look, true-to-life color.
[排除] <仅当厂商无 negative 时写这里：no added text, no watermark, no extra logo,
       natural undistorted hands, no mannequin/hanger>.
[画幅] <按厂商合法值>.
```
三铁律沿用：主体描述 / 保真约束 / 排除项**分块写**；参考图绑定优先于文字描述；画幅用合法值。

## 输出契约
- `optimized_image_prompt`：按目标厂商写好的 prompt（+ 该厂商的参数：size/--ar、negative、参考图与强度、保真参数）。
- `vendor_choice`：选了哪家 + 一句理由 + 备选。
- `fidelity_checklist`：出图后要核对的 2–4 个保真点。
- 若需机器级精确（必须 100% 复刻 logo/印花）→ 在 rationale 里点名"用 ComfyUI 虚拟试穿更稳"，不假装文生图能做到。

厂商差异与逐家改写见 [reference/vendor-matrix.md](reference/vendor-matrix.md)。IR 字段见 [../prompt-architect/reference/ir-schema.md](../prompt-architect/reference/ir-schema.md)。

## 产出 HTML 结果页
完成后，把 `kind:"image"` + `intent / optimized_image_prompt(放入 prompts) / vendor_choice(放入 vendor) / fidelity_checklist(放入 checklist) / rationale` 写成结果 JSON，用 `../prompt-architect/scripts/render_result.py` 渲染成 HTML 供查看与检查（结构见 prompt-architect 的「产出 HTML 结果页」）。
