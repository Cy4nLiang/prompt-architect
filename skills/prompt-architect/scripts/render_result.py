#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一次 prompt 优化的结果渲染成 HTML 结果页，供查看与检查。
用法: python3 render_result.py <result.json> [output.html]
result.json 结构见 prompt-architect/SKILL.md 的「产出 HTML 结果页」一节。
支持：参考图展示(images)、批量复制、每条 prompt 的中英对比视窗(content + content_zh)。"""
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
    kind_label = "文生图" if kind == "image" else "文字"
    title = data.get("title", "Prompt 优化结果")

    def section(t, body): return f'<section><h2>{e(t)}</h2>{body}</section>'

    # ① 原始请求
    raw = data.get("raw_request", "")
    raw_html = section("① 你的原始请求", f'<div class="raw">{e(raw)}</div>') if raw else ""

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
        img_html = section("参考图（输入）", f'<div class="refimgs">{"".join(tags)}</div>')

    # ② 意图
    intent = data.get("intent", {}); sig = data.get("signature", {})
    parts = []
    def kv(k, vhtml): parts.append(f'<div class="kv"><span class="k">{e(k)}</span><span class="v">{vhtml}</span></div>')
    if intent.get("why"): kv("真实目的", e(intent["why"]))
    if intent.get("success_criteria"): kv("成功判据", "<ul>"+"".join(f"<li>{e(x)}</li>" for x in intent["success_criteria"])+"</ul>")
    if intent.get("non_goals"): kv("不做(Non-Goals)", "<ul>"+"".join(f"<li>{e(x)}</li>" for x in intent["non_goals"])+"</ul>")
    if sig.get("inputs"): kv("输入(变量)", "<ul>"+"".join(f"<li>{e(x)}</li>" for x in sig["inputs"])+"</ul>")
    if sig.get("outputs"): kv("输出(字段)", "<ul>"+"".join(f"<li>{e(x)}</li>" for x in sig["outputs"])+"</ul>")
    intent_html = section("② 我解构出的意图（先核对抓得对不对）", "".join(parts)) if parts else ""

    # ③ 推荐模型（图）
    vendor = data.get("vendor"); vendor_html = ""
    if vendor:
        vendor_html = section("③ 推荐模型 & 怎么用",
            f'<div class="vendor"><div class="vn">{e(vendor.get("name",""))}</div>'
            + (f'<div class="howto">{e(vendor.get("howto",""))}</div>' if vendor.get("howto") else "")
            + (f'<details class="adv"><summary>进阶/参数（不会写代码可忽略）</summary><div>{e(vendor.get("params",""))}</div></details>' if vendor.get("params") else "")
            + '</div>')

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
                f'<div class="col"><div class="colh"><span>🅰 英文（喂给 gpt-image-2 / MJ / Nano）</span>'
                f'<button class="copy mini" data-t="p{i}e">复制</button></div><pre id="p{i}e">{e(en)}</pre></div>'
                f'<div class="col"><div class="colh"><span>🈶 中文（读懂/修改/喂给即梦）</span>'
                f'<button class="copy mini" data-t="p{i}z">复制</button></div><pre id="p{i}z">{e(zh)}</pre></div>'
                '</div>')
            head = f'<div class="ph"><span class="plabel">{e(label)}</span><span class="cmptag">中英对比</span></div>'
        else:
            body = f'<pre id="p{i}e">{e(en)}</pre>'
            head = f'<div class="ph"><span class="plabel">{e(label)}</span><button class="copy" data-t="p{i}e">📋 复制</button></div>'
        cards.append(f'<div class="pcard">{head}{note}{body}</div>')

    batch = '<div class="batch">'
    batch += f'<button class="copy big" data-t="allEn">📋 复制全部 Prompt{"（英文）" if has_zh else ""}</button>'
    if has_zh: batch += '<button class="copy big alt" data-t="allZh">📋 复制全部（中文）</button>'
    batch += '</div>'
    hidden = f'<pre id="allEn" hidden>{e((chr(10)*2).join(all_en))}</pre>'
    if has_zh: hidden += f'<pre id="allZh" hidden>{e((chr(10)*2).join(all_zh))}</pre>'
    prompts_html = section(f"④ 优化后的 Prompt（共 {len(prompts)} 条 · 复制即用）", batch + hidden + "".join(cards)) if cards else ""

    # ⑤ 检查清单
    chk = data.get("checklist", [])
    if chk:
        rows = "".join(f'<label class="ci"><input type="checkbox" class="qc"{" checked" if c.get("pass") else ""}/><span>{e(c.get("item",""))}</span></label>' for c in chk)
        checklist_html = section("⑤ 质量检查清单（逐条核对）",
            f'<div class="chkbar"><div class="track"><div class="fill" id="cf"></div></div><span id="cp"></span></div><div class="chk">{rows}</div>')
    else: checklist_html = ""

    # ⑥ rationale
    rat = data.get("rationale", [])
    rat_html = section("⑥ 改了什么 / 为什么", "<ul class='rat'>"+"".join(f"<li>{e(x)}</li>" for x in rat)+"</ul>") if rat else ""

    # ⑦ 不达标 → 重发指令（闭环）：随检查清单勾选动态生成
    redo_html = section("⑦ 不达标 → 重发指令（勾掉没过的项 → 复制去让 AI 重做）",
        '<p class="hint">在上面 ⑤ 里把<b>没达标的检查项取消勾选</b>，这里会自动拼出一段"请针对这些点重做"的话术。</p>'
        '<div class="out"><button class="copy" data-t="redo">📋 复制重发指令</button><pre id="redo"></pre></div>') if chk else ""

    order = raw_html + img_html + intent_html + vendor_html + prompts_html + checklist_html + rat_html + redo_html

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
.vendor .vn{font-weight:700;font-size:15px;margin-bottom:6px}
.howto{background:#0f2128;border:1px solid #1f5a52;border-radius:9px;padding:10px 12px;color:#bdf0e8;font-size:13px;line-height:1.6}
.adv{margin-top:9px}.adv summary{cursor:pointer;color:var(--ink3);font-size:12px;font-family:var(--mono)}.adv div{color:var(--ink2);font-size:12px;font-family:var(--mono);margin-top:6px;white-space:pre-wrap}
.chkbar{display:flex;align-items:center;gap:12px;margin-bottom:10px}.track{flex:1;height:8px;background:#0e1726;border:1px solid var(--line);border-radius:999px;overflow:hidden}.fill{height:100%;width:0;background:var(--grad);transition:.3s}#cp{font-family:var(--mono);font-size:12px;color:var(--ink2)}
.ci{display:flex;gap:9px;align-items:flex-start;padding:6px 0;border-top:1px solid var(--line);font-size:13.5px;color:var(--ink2)}.ci:first-child{border-top:none}.ci input{margin-top:3px;accent-color:#46e0d0}
.toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--acc2);color:#04201c;font-weight:700;padding:9px 18px;border-radius:10px;font-size:13px;opacity:0;transition:.25s;pointer-events:none}.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.hint{color:var(--ink3);font-size:12px;margin:0 0 10px;line-height:1.6}.hint b{color:var(--ink2)}
.out{position:relative}.out .copy{position:absolute;top:9px;right:9px}.out pre{min-height:64px}
footer{color:var(--ink3);font-size:12px;margin-top:18px;text-align:center}
"""
    JS = """
var tt,toast=document.getElementById('toast');
function st(){toast.classList.add('show');clearTimeout(tt);tt=setTimeout(function(){toast.classList.remove('show');},1200);}
document.querySelectorAll('.copy').forEach(function(b){b.addEventListener('click',function(){var el=document.getElementById(b.getAttribute('data-t'));if(!el)return;var t=el.innerText;navigator.clipboard.writeText(t).then(function(){var o=b.textContent;b.textContent='✓ 已复制';b.classList.add('ok');st();setTimeout(function(){b.textContent=o;b.classList.remove('ok');},1400);},function(){var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');st();}catch(e){}document.body.removeChild(ta);});});});
var qc=document.querySelectorAll('.qc'),cf=document.getElementById('cf'),cp=document.getElementById('cp');
var redoEl=document.getElementById('redo');
function buildRedo(){
  if(!redoEl)return;
  var fails=[];qc.forEach(function(c){if(!c.checked){var s=c.parentNode.querySelector('span');if(s)fails.push(s.textContent);}});
  if(!fails.length){redoEl.textContent='✅ 全部检查项已达标，无需重发。';return;}
  var lead = (KIND==='image')
    ? '上面生成的图有以下几点没达标。请沿用同一张参考图与原 prompt 重新生成，保持产品/主体与参考图完全一致，仅针对以下问题修正后重出：'
    : '上面的产出有以下几点没达标。请沿用原 prompt 与结构，仅针对以下问题修正后重新输出，其余保持不变：';
  redoEl.textContent = lead + '\\n' + fails.map(function(f){return '- '+f;}).join('\\n') + '\\n\\n其余已达标的部分保持不变。';
}
function upd(){if(!qc.length)return;var n=0;qc.forEach(function(c){if(c.checked)n++;});if(cf)cf.style.width=(n/qc.length*100)+'%';if(cp)cp.textContent=n+' / '+qc.length;buildRedo();}
qc.forEach(function(c){c.addEventListener('change',upd);});upd();
"""
    HTML = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
        f'<title>{e(title)} · 优化结果</title><style>{CSS}</style></head><body><div class="wrap">'
        f'<h1><span class="g">{e(title)}</span></h1>'
        f'<span class="badge">prompt-architect · {kind_label}优化结果 · 查看与检查</span>'
        + order
        + '<footer>由 prompt-architect skill 生成 · 复制上面的 prompt 粘到你的 AI 工具里使用</footer>'
        '</div><div class="toast" id="toast">已复制 ✓</div>'
        f'<script>var KIND={json.dumps(kind)};{JS}</script></body></html>'
    )
    os.makedirs(out_dir, exist_ok=True)
    open(out_abs, "w", encoding="utf-8").write(HTML)
    print(out_abs)

if __name__ == "__main__":
    main()
