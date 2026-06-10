#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一次 prompt 优化的结果渲染成 HTML 结果页，供查看与检查。
用法: python3 render_result.py <result.json> [output.html]
result.json 契约见 prompt-architect/reference/render-protocol.md。
支持：参考图展示(images)、批量复制、每条 prompt 的中英对比视窗(content + content_zh)、
多候选 grid 对比(candidates：strategy/hypothesis/tradeoff/score/recommended)、
页面语言切换(lang: "zh" 默认 | "en" 全英结果页)。"""
import json, html, sys, os

def e(s): return html.escape(str(s), quote=True)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 render_result.py <result.json> [output.html]"); sys.exit(1)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "优化结果.html")
    out_abs = os.path.abspath(out)
    out_dir = os.path.dirname(out_abs)

    kind = data.get("kind", "text")
    lang = data.get("lang", "zh")          # "zh"(默认) | "en"——全英结果页
    ZH = {
        "kind": {"image": "文生图", "video": "视频", "text": "文字"},
        "page_title_suffix": "优化结果", "badge_suffix": "优化结果 · 查看与检查",
        "sec_raw": "① 你的原始请求", "sec_imgs": "参考图（输入）",
        "sec_intent": "② 我解构出的意图（先核对抓得对不对）",
        "kv_why": "真实目的", "kv_sc": "成功判据", "kv_ng": "不做(Non-Goals)", "kv_in": "输入(变量)", "kv_out": "输出(字段)",
        "sec_vendor": "③ 推荐模型 & 怎么用", "adv": "进阶/参数（不会写代码可忽略）",
        "sec_shots": "🎬 分镜计划（每镜仅 1 种运镜）",
        "shot_cols": [("shot","镜头"),("duration","时长"),("framing","景别"),("camera","运镜"),("action","内容"),("audio","音频/台词"),("transition","转场")],
        "sec_audio": "🔊 音频与对白（音频字段不留空）",
        "ak_music": "音乐 Music", "ak_amb": "环境音 Ambience", "ak_sfx": "音效 SFX", "ak_dlg": "对白 Dialogue", "ak_note": "说明",
        "sec_assets": "📎 参考素材职责分配（每个素材唯一职责）", "asset_cols": ["素材", "职责", "引用语法"],
        "sec_prompts": "④ 优化后的 Prompt（共 {n} 条 · 复制即用）",
        "copy_all": "📋 复制全部 Prompt", "copy_all_en_sfx": "（英文）", "copy_all_zh": "📋 复制全部（中文）",
        "col_en": "🅰 英文（喂给 gpt-image-2 / MJ / Nano）", "col_zh": "🈶 中文（读懂/修改/喂给即梦）",
        "cmp_tag": "中英对比", "copy": "复制", "copy_btn": "📋 复制",
        "sec_cands": "④ 候选方案对比（{n} 个候选 · 各押一种结构策略 · 都能用，按场景选）",
        "cands_hint": '每个候选是一种<b>结构性押注</b>：strategy 是押的策略，"代价"是它牺牲的东西。★ 为 pa-eval 综合得分最高者，但落选方案在特定场景可能更合适。',
        "rec": "★ pa-eval 推荐", "hyp": "假设：", "trade": "⚖ 代价：", "zh_alt": "中文平行版", "copy_all_cands": "📋 复制全部候选",
        "sec_chk": "⑤ 质量检查清单（逐条核对）", "sec_rat": "⑥ 改了什么 / 为什么",
        "sec_redo": "⑦ 不达标 → 重发指令（勾掉没过的项 → 复制去让 AI 重做）",
        "redo_hint": '在上面 ⑤ 里把<b>没达标的检查项取消勾选</b>，这里会自动拼出一段"请针对这些点重做"的话术。',
        "copy_redo": "📋 复制重发指令",
        "footer": "由 prompt-architect skill 生成 · 复制上面的 prompt 粘到你的 AI 工具里使用",
        "toast": "已复制 ✓", "copied": "✓ 已复制",
        "redo_ok": "✅ 全部检查项已达标，无需重发。",
        "redo_lead_image": "上面生成的图有以下几点没达标。请沿用同一张参考图与原 prompt 重新生成，保持产品/主体与参考图完全一致，仅针对以下问题修正后重出：",
        "redo_lead_video": "上面生成的视频有以下几点没达标。请沿用同一组参考素材与原 prompt，保持角色/产品与参考一致、分镜结构不变，仅针对以下问题修正后重出：",
        "redo_lead_text": "上面的产出有以下几点没达标。请沿用原 prompt 与结构，仅针对以下问题修正后重新输出，其余保持不变：",
        "redo_tail": "其余已达标的部分保持不变。",
    }
    EN = {
        "kind": {"image": "image", "video": "video", "text": "text"},
        "page_title_suffix": "optimization result", "badge_suffix": "optimization result · review & check",
        "sec_raw": "① Your original request", "sec_imgs": "Reference images (input)",
        "sec_intent": "② The intent I extracted (verify this first)",
        "kv_why": "Real goal", "kv_sc": "Success criteria", "kv_ng": "Non-goals", "kv_in": "Inputs (variables)", "kv_out": "Outputs (fields)",
        "sec_vendor": "③ Recommended model & how to use it", "adv": "Advanced / parameters (skip if you don't code)",
        "sec_shots": "🎬 Shot plan (one camera move per shot)",
        "shot_cols": [("shot","Shot"),("duration","Duration"),("framing","Framing"),("camera","Camera"),("action","Action"),("audio","Audio / dialogue"),("transition","Transition")],
        "sec_audio": "🔊 Audio & dialogue (never leave audio unspecified)",
        "ak_music": "Music", "ak_amb": "Ambience", "ak_sfx": "SFX", "ak_dlg": "Dialogue", "ak_note": "Note",
        "sec_assets": "📎 Reference asset roles (one unique role per asset)", "asset_cols": ["Asset", "Role", "Syntax"],
        "sec_prompts": "④ Optimized prompts ({n} · copy-ready)",
        "copy_all": "📋 Copy all prompts", "copy_all_en_sfx": " (EN)", "copy_all_zh": "📋 Copy all (ZH)",
        "col_en": "🅰 English (for gpt-image / MJ / Nano)", "col_zh": "🈶 Chinese (read/edit, or for Seedream)",
        "cmp_tag": "EN/ZH", "copy": "Copy", "copy_btn": "📋 Copy",
        "sec_cands": "④ Candidate comparison ({n} candidates · one structural bet each · pick by scenario)",
        "cands_hint": 'Each candidate is a <b>structural bet</b>: "strategy" is the bet, "tradeoff" is what it sacrifices. ★ marks the judge\'s top pick — runners-up may still fit specific scenarios better.',
        "rec": "★ judge's pick", "hyp": "Hypothesis: ", "trade": "⚖ Tradeoff: ", "zh_alt": "Chinese version", "copy_all_cands": "📋 Copy all candidates",
        "sec_chk": "⑤ Quality checklist (tick through)", "sec_rat": "⑥ What changed & why",
        "sec_redo": "⑦ Not up to standard → redo instruction (untick failed items, copy, send back)",
        "redo_hint": "Untick the <b>failed items in ⑤</b> above — a ready-to-send rework instruction is assembled here automatically.",
        "copy_redo": "📋 Copy redo instruction",
        "footer": "Generated by the prompt-architect skill · copy the prompts above into your AI tool",
        "toast": "Copied ✓", "copied": "✓ Copied",
        "redo_ok": "✅ All checklist items passed — nothing to redo.",
        "redo_lead_image": "The generated image misses the points below. Re-generate with the same reference image and prompt, keep the subject identical to the reference, and fix only these issues:",
        "redo_lead_video": "The generated video misses the points below. Re-generate with the same reference assets and prompt, keep characters/products consistent and the shot structure unchanged, and fix only these issues:",
        "redo_lead_text": "The output misses the points below. Keep the original prompt and structure, fix only these issues, and re-output:",
        "redo_tail": "Keep everything that already passed unchanged.",
    }
    L = EN if lang == "en" else ZH
    kind_label = L["kind"].get(kind, L["kind"]["text"])
    title = data.get("title", "Prompt 优化结果" if lang != "en" else "Prompt optimization result")

    def section(t, body): return f'<section><h2>{e(t)}</h2>{body}</section>'

    # ① 原始请求
    raw = data.get("raw_request", "")
    raw_html = section(L["sec_raw"], f'<div class="raw">{e(raw)}</div>') if raw else ""

    # 参考图（输入）
    imgs = data.get("images", [])
    img_html = ""
    if imgs:
        tags = []
        for p in imgs:
            src = p if os.path.isabs(p) else os.path.join(os.getcwd(), p)
            try: rel = os.path.relpath(src, out_dir)
            except Exception: rel = p
            cap = os.path.basename(p)
            tags.append(f'<figure><img src="{e(rel)}" alt="{e(cap)}" loading="lazy"/><figcaption>{e(cap)}</figcaption></figure>')
        img_html = section(L["sec_imgs"], f'<div class="refimgs">{"".join(tags)}</div>')

    # ② 意图
    intent = data.get("intent", {}); sig = data.get("signature", {})
    parts = []
    def kv(k, vhtml): parts.append(f'<div class="kv"><span class="k">{e(k)}</span><span class="v">{vhtml}</span></div>')
    if intent.get("why"): kv(L["kv_why"], e(intent["why"]))
    if intent.get("success_criteria"): kv(L["kv_sc"], "<ul>"+"".join(f"<li>{e(x)}</li>" for x in intent["success_criteria"])+"</ul>")
    if intent.get("non_goals"): kv(L["kv_ng"], "<ul>"+"".join(f"<li>{e(x)}</li>" for x in intent["non_goals"])+"</ul>")
    if sig.get("inputs"): kv(L["kv_in"], "<ul>"+"".join(f"<li>{e(x)}</li>" for x in sig["inputs"])+"</ul>")
    if sig.get("outputs"): kv(L["kv_out"], "<ul>"+"".join(f"<li>{e(x)}</li>" for x in sig["outputs"])+"</ul>")
    intent_html = section(L["sec_intent"], "".join(parts)) if parts else ""

    # ③ 推荐模型（图）
    vendor = data.get("vendor"); vendor_html = ""
    if vendor:
        vendor_html = section(L["sec_vendor"],
            f'<div class="vendor"><div class="vn">{e(vendor.get("name",""))}</div>'
            + (f'<div class="howto">{e(vendor.get("howto",""))}</div>' if vendor.get("howto") else "")
            + (f'<details class="adv"><summary>{L["adv"]}</summary><div>{e(vendor.get("params",""))}</div></details>' if vendor.get("params") else "")
            + '</div>')

    # 视频专用区块：分镜计划 / 音频与对白 / 参考素材职责
    shot_plan = data.get("shot_plan", []); shot_html = ""
    if shot_plan:
        cols = L["shot_cols"]
        used = [(k,lab) for k,lab in cols if any(s.get(k) for s in shot_plan)]
        head = "".join(f"<th>{e(lab)}</th>" for _,lab in used)
        body = "".join("<tr>"+"".join(f"<td>{e(s.get(k,''))}</td>" for k,_ in used)+"</tr>" for s in shot_plan)
        shot_html = section(L["sec_shots"], f'<table class="plan"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>')

    aspec = data.get("audio_spec"); audio_html = ""
    if aspec:
        ap = []
        def akv(k, v): ap.append(f'<div class="kv"><span class="k">{e(k)}</span><span class="v">{v}</span></div>')
        if aspec.get("music"): akv(L["ak_music"], e(aspec["music"]))
        if aspec.get("ambience"): akv(L["ak_amb"], e(aspec["ambience"]))
        if aspec.get("sfx"): akv(L["ak_sfx"], e(aspec["sfx"]))
        if aspec.get("dialogue"):
            lines = "".join(f'<li><b>{e(d.get("speaker",""))}</b>{("（"+e(d["tone"])+"）") if d.get("tone") else ""}: "{e(d.get("line",""))}"</li>' for d in aspec["dialogue"])
            akv(L["ak_dlg"], f"<ul>{lines}</ul>")
        if aspec.get("note"): akv(L["ak_note"], e(aspec["note"]))
        if ap: audio_html = section(L["sec_audio"], "".join(ap))

    asset_plan = data.get("asset_plan", []); asset_html = ""
    if asset_plan:
        body = "".join(f'<tr><td>{e(a.get("asset",""))}</td><td>{e(a.get("role",""))}</td><td><code>{e(a.get("syntax",""))}</code></td></tr>' for a in asset_plan)
        ac = L["asset_cols"]
        asset_html = section(L["sec_assets"],
            f'<table class="plan"><thead><tr><th>{ac[0]}</th><th>{ac[1]}</th><th>{ac[2]}</th></tr></thead><tbody>{body}</tbody></table>')

    # ④ 优化后 prompt —— 批量复制 + 每条中英对比
    prompts = data.get("prompts", [])
    has_zh = any(p.get("content_zh") for p in prompts)
    cards, all_en, all_zh = [], [], []
    for i, p in enumerate(prompts):
        label = p.get("label", f"Prompt {i+1}")
        note = f'<div class="pnote">{e(p["note"])}</div>' if p.get("note") else ""
        en = p.get("content", ""); zh = p.get("content_zh", "")
        all_en.append(f"### {label}\n{en}")
        if zh: all_zh.append(f"### {label}\n{zh}")
        if zh:
            body = (
                '<div class="cmp">'
                f'<div class="col"><div class="colh"><span>{L["col_en"]}</span>'
                f'<button class="copy mini" data-t="p{i}e">{L["copy"]}</button></div><pre id="p{i}e">{e(en)}</pre></div>'
                f'<div class="col"><div class="colh"><span>{L["col_zh"]}</span>'
                f'<button class="copy mini" data-t="p{i}z">{L["copy"]}</button></div><pre id="p{i}z">{e(zh)}</pre></div>'
                '</div>')
            head = f'<div class="ph"><span class="plabel">{e(label)}</span><span class="cmptag">{L["cmp_tag"]}</span></div>'
        else:
            body = f'<pre id="p{i}e">{e(en)}</pre>'
            head = f'<div class="ph"><span class="plabel">{e(label)}</span><button class="copy" data-t="p{i}e">{L["copy_btn"]}</button></div>'
        cards.append(f'<div class="pcard">{head}{note}{body}</div>')

    batch = '<div class="batch">'
    batch += f'<button class="copy big" data-t="allEn">{L["copy_all"]}{L["copy_all_en_sfx"] if has_zh else ""}</button>'
    if has_zh: batch += f'<button class="copy big alt" data-t="allZh">{L["copy_all_zh"]}</button>'
    batch += '</div>'
    hidden = f'<pre id="allEn" hidden>{e((chr(10)*2).join(all_en))}</pre>'
    if has_zh: hidden += f'<pre id="allZh" hidden>{e((chr(10)*2).join(all_zh))}</pre>'
    prompts_html = section(L["sec_prompts"].format(n=len(prompts)), batch + hidden + "".join(cards)) if cards else ""

    # ④' 多候选 grid 对比（candidates —— 每个候选一种结构押注，标 tradeoff 与得分）
    cands = data.get("candidates", [])
    cand_html = ""
    if cands:
        ccards, call = [], []
        for i, c in enumerate(cands):
            label = c.get("label", f"候选 {chr(65+i)}")
            call.append(f"### {label}\n{c.get('content','')}")
            badges = ""
            if c.get("recommended"): badges += f'<span class="rec">{L["rec"]}</span>'
            if c.get("strategy"): badges += f'<span class="strat">{e(c["strategy"])}</span>'
            sc = c.get("score")
            if sc is not None:
                sc_txt = f"{sc:.2f}" if isinstance(sc, (int, float)) else str(sc)
                badges += f'<span class="score">{e(sc_txt)}</span>'
            meta = ""
            if c.get("hypothesis"): meta += f'<div class="chyp">{L["hyp"]}{e(c["hypothesis"])}</div>'
            if c.get("tradeoff"): meta += f'<div class="ctrade">{L["trade"]}{e(c["tradeoff"])}</div>'
            zh = c.get("content_zh", "")
            body = f'<pre id="c{i}">{e(c.get("content",""))}</pre>'
            if zh: body += f'<details class="czh"><summary>{L["zh_alt"]}</summary><pre id="c{i}z">{e(zh)}</pre></details>'
            ccards.append(
                f'<div class="ccard{" best" if c.get("recommended") else ""}">'
                f'<div class="ch"><span class="plabel">{e(label)}</span>{badges}'
                f'<button class="copy mini" data-t="c{i}">{L["copy"]}</button></div>'
                f'{meta}{body}</div>')
        cbatch = f'<div class="batch"><button class="copy big" data-t="allCand">{L["copy_all_cands"]}</button></div>'
        chidden = f'<pre id="allCand" hidden>{e((chr(10)*2).join(call))}</pre>'
        cand_html = section(L["sec_cands"].format(n=len(cands)),
            f'<p class="hint">{L["cands_hint"]}</p>'
            + cbatch + chidden + f'<div class="cgrid">{"".join(ccards)}</div>')

    # ⑤ 检查清单
    chk = data.get("checklist", [])
    if chk:
        rows = "".join(f'<label class="ci"><input type="checkbox" class="qc"{" checked" if c.get("pass") else ""}/><span>{e(c.get("item",""))}</span></label>' for c in chk)
        checklist_html = section(L["sec_chk"],
            f'<div class="chkbar"><div class="track"><div class="fill" id="cf"></div></div><span id="cp"></span></div><div class="chk">{rows}</div>')
    else: checklist_html = ""

    # ⑥ rationale
    rat = data.get("rationale", [])
    rat_html = section(L["sec_rat"], "<ul class='rat'>"+"".join(f"<li>{e(x)}</li>" for x in rat)+"</ul>") if rat else ""

    # ⑦ 不达标 → 重发指令（闭环）：随检查清单勾选动态生成
    redo_html = section(L["sec_redo"],
        f'<p class="hint">{L["redo_hint"]}</p>'
        f'<div class="out"><button class="copy" data-t="redo">{L["copy_redo"]}</button><pre id="redo"></pre></div>') if chk else ""

    order = raw_html + img_html + intent_html + vendor_html + shot_html + audio_html + asset_html + cand_html + prompts_html + checklist_html + rat_html + redo_html

    CSS = """
:root{--bg:#0a0e16;--card:#131b2a;--card2:#172033;--line:#26334a;--line2:#33425c;--ink:#e6edf6;--ink2:#aab7cc;--ink3:#6f8099;--acc:#7c9cff;--acc2:#46e0d0;--grad:linear-gradient(100deg,#7c9cff,#46e0d0);--mono:"SF Mono",ui-monospace,Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(1000px 500px at 80% -10%,#16213a44,#0a0e16 60%),var(--bg);color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:980px;margin:0 auto;padding:34px 22px 80px}
h1{font-size:24px;margin:0 0 4px;font-weight:800}h1 .g{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.badge{display:inline-block;font-size:11px;font-family:var(--mono);color:var(--acc2);border:1px solid var(--line2);border-radius:999px;padding:2px 10px;margin-bottom:18px}
section{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:16px 18px;margin-bottom:14px}
h2{font-size:15px;margin:0 0 12px;color:var(--acc2);font-weight:700}
.raw{color:var(--ink2);font-size:14px;background:#0e1726;border:1px solid var(--line);border-radius:9px;padding:11px 13px;white-space:pre-wrap}
.refimgs{display:flex;gap:12px;flex-wrap:wrap}
.refimgs figure{margin:0;background:#0e1726;border:1px solid var(--line);border-radius:10px;padding:8px;text-align:center}
.refimgs img{max-height:220px;max-width:100%;border-radius:7px;display:block}
.refimgs figcaption{color:var(--ink3);font-size:11px;margin-top:6px;font-family:var(--mono)}
.kv{display:grid;grid-template-columns:96px 1fr;gap:10px;padding:6px 0;border-top:1px solid var(--line)}
.kv:first-child{border-top:none}.kv .k{color:var(--ink3);font-size:12.5px;font-family:var(--mono)}.kv .v{font-size:14px}
.kv ul,.rat{margin:0;padding-left:18px}.kv li,.rat li{margin:2px 0;font-size:13.6px;color:var(--ink2)}
.batch{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:14px}
.pcard{background:#0e1726;border:1px solid var(--line);border-radius:11px;overflow:hidden;margin-bottom:12px}
.pcard:last-child{margin-bottom:0}
.ph{display:flex;align-items:center;gap:10px;padding:11px 13px}
.plabel{font-weight:700;font-size:14px}.cmptag{margin-left:auto;font-size:11px;font-family:var(--mono);color:var(--acc2);border:1px solid var(--line2);border-radius:999px;padding:2px 8px}
.pnote{color:var(--ink3);font-size:12.5px;padding:0 13px 8px}
.cmp{display:grid;grid-template-columns:1fr 1fr;gap:0}
@media(max-width:760px){.cmp{grid-template-columns:1fr}}
.cmp .col{border-top:1px solid var(--line)}
.cmp .col:nth-child(2){border-left:1px solid var(--line)}
@media(max-width:760px){.cmp .col:nth-child(2){border-left:none}}
.colh{display:flex;align-items:center;gap:8px;padding:8px 12px;background:#0c1421}
.colh span{font-size:11.5px;color:var(--ink2)}
.copy{background:#16213a;border:1px solid var(--line2);color:var(--ink);font-size:12.5px;padding:5px 12px;border-radius:8px;cursor:pointer;font-family:var(--mono)}
.copy:hover{border-color:var(--acc);color:#fff}.copy.ok{border-color:var(--acc2);color:var(--acc2)}
.copy.mini{margin-left:auto;padding:3px 10px;font-size:11.5px}
.ph .copy{margin-left:auto}
.copy.big{padding:8px 15px;font-size:13px}.copy.big.alt{background:#0c1421}
pre{margin:0;background:#070b12;border-top:1px solid var(--line);padding:14px;overflow-x:auto;font-family:var(--mono);font-size:12.2px;line-height:1.55;color:#cdd9ea;white-space:pre-wrap;word-break:break-word}
.cmp pre{border-top:none}
.plan{border-collapse:collapse;width:100%;font-size:13px}
.plan th,.plan td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.plan thead th{color:var(--ink3);font-size:12px;font-family:var(--mono);font-weight:600}
.plan td{color:var(--ink2)}
.vendor .vn{font-weight:700;font-size:15px;margin-bottom:6px}
.howto{background:#0f2128;border:1px solid #1f5a52;border-radius:9px;padding:10px 12px;color:#bdf0e8;font-size:13px;line-height:1.6}
.adv{margin-top:9px}.adv summary{cursor:pointer;color:var(--ink3);font-size:12px;font-family:var(--mono)}.adv div{color:var(--ink2);font-size:12px;font-family:var(--mono);margin-top:6px;white-space:pre-wrap}
.chkbar{display:flex;align-items:center;gap:12px;margin-bottom:10px}.track{flex:1;height:8px;background:#0e1726;border:1px solid var(--line);border-radius:999px;overflow:hidden}.fill{height:100%;width:0;background:var(--grad);transition:.3s}#cp{font-family:var(--mono);font-size:12px;color:var(--ink2)}
.ci{display:flex;gap:9px;align-items:flex-start;padding:6px 0;border-top:1px solid var(--line);font-size:13.5px;color:var(--ink2)}.ci:first-child{border-top:none}.ci input{margin-top:3px;accent-color:#46e0d0}
.cgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.ccard{background:#0e1726;border:1px solid var(--line);border-radius:11px;overflow:hidden;display:flex;flex-direction:column}
.ccard.best{border-color:var(--acc2);box-shadow:0 0 0 1px var(--acc2)}
.ch{display:flex;align-items:center;gap:7px;padding:10px 12px;flex-wrap:wrap}
.rec{font-size:10.5px;font-family:var(--mono);color:#04201c;background:var(--acc2);border-radius:999px;padding:2px 8px;font-weight:700}
.strat{font-size:10.5px;font-family:var(--mono);color:var(--acc);border:1px solid var(--line2);border-radius:999px;padding:2px 8px}
.score{font-size:10.5px;font-family:var(--mono);color:var(--ink2);border:1px solid var(--line2);border-radius:999px;padding:2px 8px}
.ch .copy{margin-left:auto}
.chyp{color:var(--ink2);font-size:12px;padding:0 12px 4px;line-height:1.5}
.ctrade{color:#e8c07a;font-size:12px;padding:0 12px 8px;line-height:1.5}
.ccard pre{flex:1}
.czh{border-top:1px solid var(--line)}.czh summary{cursor:pointer;color:var(--ink3);font-size:11.5px;font-family:var(--mono);padding:7px 12px}.czh pre{border-top:1px solid var(--line)}
.toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--acc2);color:#04201c;font-weight:700;padding:9px 18px;border-radius:10px;font-size:13px;opacity:0;transition:.25s;pointer-events:none}.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.hint{color:var(--ink3);font-size:12px;margin:0 0 10px;line-height:1.6}.hint b{color:var(--ink2)}
.out{position:relative}.out .copy{position:absolute;top:9px;right:9px}.out pre{min-height:64px}
footer{color:var(--ink3);font-size:12px;margin-top:18px;text-align:center}
"""
    JS = """
var tt,toast=document.getElementById('toast');
function st(){toast.classList.add('show');clearTimeout(tt);tt=setTimeout(function(){toast.classList.remove('show');},1200);}
document.querySelectorAll('.copy').forEach(function(b){b.addEventListener('click',function(){var el=document.getElementById(b.getAttribute('data-t'));if(!el)return;var t=el.innerText;navigator.clipboard.writeText(t).then(function(){var o=b.textContent;b.textContent=I18N.copied;b.classList.add('ok');st();setTimeout(function(){b.textContent=o;b.classList.remove('ok');},1400);},function(){var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');st();}catch(e){}document.body.removeChild(ta);});});});
var qc=document.querySelectorAll('.qc'),cf=document.getElementById('cf'),cp=document.getElementById('cp');
var redoEl=document.getElementById('redo');
function buildRedo(){
  if(!redoEl)return;
  var fails=[];qc.forEach(function(c){if(!c.checked){var s=c.parentNode.querySelector('span');if(s)fails.push(s.textContent);}});
  if(!fails.length){redoEl.textContent=I18N.redo_ok;return;}
  var lead = (KIND==='image') ? I18N.lead_image : (KIND==='video') ? I18N.lead_video : I18N.lead_text;
  redoEl.textContent = lead + '\\n' + fails.map(function(f){return '- '+f;}).join('\\n') + '\\n\\n' + I18N.redo_tail;
}
function upd(){if(!qc.length)return;var n=0;qc.forEach(function(c){if(c.checked)n++;});if(cf)cf.style.width=(n/qc.length*100)+'%';if(cp)cp.textContent=n+' / '+qc.length;buildRedo();}
qc.forEach(function(c){c.addEventListener('change',upd);});upd();
"""
    I18N = {"copied": L["copied"], "redo_ok": L["redo_ok"], "lead_image": L["redo_lead_image"],
            "lead_video": L["redo_lead_video"], "lead_text": L["redo_lead_text"], "redo_tail": L["redo_tail"]}
    badge_sep = " " if lang == "en" else ""
    HTML = (
        f'<!doctype html><html lang="{"en" if lang == "en" else "zh-CN"}"><head><meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
        f'<title>{e(title)} · {L["page_title_suffix"]}</title><style>{CSS}</style></head><body><div class="wrap">'
        f'<h1><span class="g">{e(title)}</span></h1>'
        f'<span class="badge">prompt-architect · {kind_label}{badge_sep}{L["badge_suffix"]}</span>'
        + order
        + f'<footer>{L["footer"]}</footer>'
        f'</div><div class="toast" id="toast">{L["toast"]}</div>'
        f'<script>var KIND={json.dumps(kind)},I18N={json.dumps(I18N, ensure_ascii=False)};{JS}</script></body></html>'
    )
    os.makedirs(out_dir, exist_ok=True)
    open(out_abs, "w", encoding="utf-8").write(HTML)
    print(out_abs)

if __name__ == "__main__":
    main()
