**English** | [简体中文](README_zh.md)

# prompt-architect — Prompt Optimizer & Compiler Suite for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-7c9cff.svg)](#contributing)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill%20suite-46e0d0.svg)](https://claude.com/claude-code)

You say one vague sentence. The suite **mines your real intent** into a typed IR, compiles a **genre-aware** structured prompt (6 structurally different skeletons — no one-size-fits-all), generates **3 candidates** scored head-to-head by an **LLM judge**, and ships an **interactive HTML report** you can review, copy from, and iterate on.

Covers **text prompts** (copywriting / chatbots / extraction / agent system prompts), **image prompts** (Midjourney, Seedream, gpt-image, SD/Flux…) and **video prompts** (Seedance, Sora, Kling, Veo, Runway…) — plus a **coding lane** (`pa-coding`, the one directly-callable sub-skill): it auto-scans your repo, interviews you about a dev task, compiles the optimal task brief, and on your confirmation executes it right in the current Claude Code session.

> **Core idea** (distilled from source-level analysis of 20 top prompt-engineering frameworks):
> a prompt is not prose you write — it is an artifact **compiled from a typed I/O contract**. Humans own the intent; the loop owns the wording.

## Table of Contents

- [See It in Action](#see-it-in-action)
- [New to Agent Skills? Read This First](#new-to-agent-skills-read-this-first)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Six Genre Templates — Why Outputs Don't All Look the Same](#six-genre-templates--why-outputs-dont-all-look-the-same)
- [The HTML Report](#the-html-report)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Credits & License](#credits--license)

## See It in Action

Three real pipeline runs (English inputs, fully-English result pages), three completely different needs — and three **structurally different** prompt skeletons (this anti-homogenization is the suite's core selling point). Full result pages live in [`examples/`](examples/) (download and open in a browser).

| Input (user's words) | Genre detected | Candidates | Winner strategy | Judge score |
|---|---|---|---|---|
| "Write me a prompt for Instagram product posts — amino-acid shampoo, best-friend recommendation voice" | creative | 3 | persona-driven | 0.86 ✅ |
| "Write a system prompt for our e-commerce customer-service bot — de-escalate with empathy, never over-promise, hand off when serious" | conversation_role | 3 | dialogue-scripted | 0.90 ✅ |
| "Write a prompt that extracts party_a/b, amount, signing date, breach clauses from contracts as strict JSON — missing fields must be null" | extract (machine-consumed) | 1 (deliberately) | contract-anchored | 0.91 ✅ |

The three winning skeletons share **zero section names**:

```text
creative      : Brief → Persona → Voice card → Tone calibration → Content contract → Shape outline
                (no rule list, no JSON, no stop sentinel — copy needs a voice, not a spec sheet)

conversation  : Persona → Boundaries & permissions → Boundary drill scripts (the core) →
                Escalation & handoff → Reply norms
                (constraints live as "scenario → scripted reply", not field definitions)

extract       : Role → Goal → Rules → Workflow → Output Format (JSON-schema injected verbatim
                + stop sentinel) → Examples (incl. a null case) → Input
                (machine-consumed, so constraints are maximal — and only ONE candidate:
                 diversity has no value here)
```

[![Result page — 3-candidate grid](examples/screenshots/shot-instagram-en.png)](examples/result-instagram-en.html)

<details>
<summary>📸 The other two result pages</summary>

[![Customer-service bot](examples/screenshots/shot-support-bot-en.png)](examples/result-support-bot-en.html)

[![Contract extraction](examples/screenshots/shot-contract-en.png)](examples/result-contract-en.html)

</details>

> The suite is bilingual — the same three pipelines run from Chinese inputs are also in [`examples/`](examples/) (`result-xiaohongshu.html`, `result-cs-bot.html`, `result-contract-extract.html`).

### Try it yourself

These are the exact inputs that produced the pages above — paste any of them into Claude Code to reproduce:

```text
Write me a prompt for Instagram product posts — promoting our amino-acid shampoo,
in a "best-friend recommendation" voice, for women 18–30 who care about ingredients.
```

```text
Write a system prompt for our e-commerce customer-service bot. It must de-escalate
angry customers with empathy, never promise refunds or compensation beyond policy,
and hand off to a human agent when things get serious.
```

```text
Write a prompt that extracts party_a, party_b, contract_amount, signing_date and
breach_clauses from raw contract text, returning strict JSON for our database —
missing fields must be null, never guessed.
```

## New to Agent Skills? Read This First

If this is your first Claude Code skill, five things worth knowing:

1. **A skill is just a folder of instructions.** No binaries, no background processes. Claude Code reads `SKILL.md` files under `.claude/skills/` and follows them when your request matches. This suite makes **no network calls and collects no telemetry** — everything runs inside your Claude session.
2. **You talk normally — skills trigger on intent.** Say *"rewrite this prompt so the model returns valid JSON"* and the suite picks it up. No slash commands to memorize. If it doesn't trigger, just be explicit: *"use prompt-architect to optimize: …"*.
3. **Restart Claude Code after installing.** Skills are loaded at session start. To verify the install: `ls .claude/skills` in your project should show 8 `pa-*` / `prompt-architect` folders.
4. **Only talk to the entry skill** (one exception). `prompt-architect` is the single entry point; the `pa-*` sub-skills are its internal pipeline stages. Calling them directly skips the injection-fencing and intent-mining steps — which is exactly how you get generic, homogenized output. The one exception is `pa-coding`: the coding lane is designed for direct invocation ("turn this dev task into an optimal prompt, then start").
5. **Expect a short interview, and a few more tokens.** The pipeline asks up to 3 clarifying questions before writing anything, and runs multiple stages (mine → compile ×3 candidates → judge). It costs more tokens than a bare "improve my prompt" — that's the price of output you don't have to redo.

## Installation

Requires [Claude Code](https://claude.com/claude-code) (CLI, desktop, or IDE extension).

```bash
git clone https://github.com/Cy4nLiang/claude-code-prompt-architect.git

# Option 1 (recommended): install into one project
cd /path/to/your-project
/path/to/claude-code-prompt-architect/install.sh --project

# Option 2: install user-wide (available in every project)
/path/to/claude-code-prompt-architect/install.sh
```

Restart Claude Code. To upgrade later: `git pull`, then re-run `install.sh` (it syncs — local edits to installed skills are overwritten).

> ⚠️ Don't `cp` skill folders around by hand. Mixed old/new copies are the #1 cause of mis-triggering — always go through `install.sh`.

## Usage

Just describe what you want, in English or Chinese:

```text
Optimize this prompt: (paste yours)
Write me a prompt from scratch that makes the AI generate weekly reports
This prompt keeps returning broken JSON — fix it
Write a product-photo prompt — which image model should I use?
Write a prompt for a 10-second product ad video
Turn this dev task into an optimal prompt, then start: add rate limiting to the login API
```

What happens next:

1. **It interviews you first** (≤3 questions) to fill the gaps that matter — goal, audience, red lines;
2. **It shows you the intent it extracted** — confirm before anything gets written;
3. **You get prompts + an HTML report** (`open …` command in the terminal): compare candidates side by side, copy with one click, tick through the quality checklist;
4. **Not happy? Say what's wrong.** It makes a minimal edit on top of the existing version — attempts are versioned, and regressions auto-revert.

## How It Works

8 skills form one pipeline. Only `prompt-architect` is the entry; everything else is an internal stage (with one directly-callable exception: `pa-coding`):

**Line 1 · Text prompts (most common)**

```mermaid
flowchart LR
    A["your one-line request"] --> B["prompt-architect<br/>entry: injection fencing<br/>+ routing"]
    B --> C["pa-deconstruct<br/>mine intent<br/>→ typed IR"]
    C --> D["pa-optimize<br/>genre-aware skeleton<br/>3 candidates"]
    D -->|human-read output| E["pa-eval<br/>judge: score +<br/>pairwise compare"]
    D -->|machine-parsed output| G["pa-precise-retrieval<br/>enforcement: schema /<br/>validate-reask"] --> E
    E --> H["HTML report"]
```

**Line 2 · Image / video prompts** (same shape, different compiler; if the subject/purpose is unclear it borrows Line 1's pa-deconstruct first):

```mermaid
flowchart LR
    A["your one-line request"] --> B["prompt-architect<br/>entry"]
    B -->|image wanted| I["pa-image<br/>10 elements + vendor pick<br/>3 variants when pure-creative"]
    B -->|video wanted| V["pa-video<br/>shots/audio/consistency<br/>2 candidates when style-sensitive"]
    I --> E["pa-eval<br/>score & rank"]
    V --> E
    E --> H["HTML report"]
```

**Line 3 · When the judge says no (automatic iteration loop)**

```mermaid
flowchart LR
    E["pa-eval scores"] -->|pass| H["deliver report"]
    E -->|fail| F["failure reasons<br/>written back to IR"]
    F --> R["pa-optimize iterate mode<br/>critic diagnoses → rewriter<br/>makes minimal edit"]
    R --> E
    E -->|2 rounds, no progress| S["halt: go re-mine the intent<br/>instead of polishing words"]
```

**Line 4 · Coding lane (`pa-coding`, directly callable — lightweight, ends in execution, not a report)**

```mermaid
flowchart LR
    A["your dev task"] --> P["pa-coding<br/>auto-scan repo<br/>+ short interview"]
    P --> B["task brief<br/>(goal / acceptance /<br/>scope / verification)"]
    B --> C{"confirm?"}
    C -->|yes| X["executes in this<br/>Claude Code session"]
    C -->|tweak| P
```

| skill | one-line job |
|---|---|
| **prompt-architect** | Sole entry: fences your raw text as data (anti-injection), gauges complexity, routes |
| pa-deconstruct | The interview: extracts real intent into a typed IR (genre, style, success criteria, output contract) |
| pa-optimize | The compiler: picks the genre skeleton, writes 3 candidates with orthogonal strategies |
| pa-eval | The judge: compiles a rubric from your success criteria; scores, compares pairwise, signals halt — never writes |
| pa-precise-retrieval | Enforcement: when output feeds a program, tightens to schema / constrained decoding / validate-reask |
| pa-image | Image compiler: subject/composition/lighting/fidelity, vendor-specific negative & aspect syntax |
| pa-video | Video compiler: duration budget, shot list, audio/dialogue, cross-shot consistency, vendor formats |
| pa-coding | Coding lane (directly callable): auto-scans the repo, interviews you for acceptance criteria & scope, compiles a task brief, executes it on confirmation |

## Six Genre Templates — Why Outputs Don't All Look the Same

Most prompt tools press every need into the same Role/Rules/Steps/Format mold. This suite classifies your task into one of six genres, **each with a structurally different skeleton** (templates in [`skills/prompt-architect/reference/templates/`](skills/prompt-architect/reference/templates/)):

| Genre | Typical need | What makes its skeleton different |
|---|---|---|
| creative | social posts / ads / brand stories | **Voice card + sample passage** instead of rule lists; no JSON, no stop sentinel |
| conversation_role | support bots / roleplay | **Persona + stage-based strategy + boundary drill scripts**; designed in "turns/scenes", not "fields" |
| extract | extraction / classification | Five-section + **schema injected verbatim** + stop sentinel + "uncertain → null" |
| analytical | analysis / reviews / reports | **Locked analysis dimensions + evidence taxonomy** (fact/inference/assumption) + conclusion-first |
| agent_system | tool-using agent prompts | **Tool contracts (when NOT to use) + decision loop + decidable stop conditions** + safety lines |
| rewrite_light | tone fix / shorten / translate | **≤10 lines**: invariants + direction + 1 before/after pair; adding structure is forbidden |

Plus: multi-candidate by default (3 strategies from a [tip library](skills/pa-optimize/reference/strategy-tips.md), each labeled with its tradeoff), deliberate single-candidate for extraction (diversity is fake there), and a judge that scores genre-appropriately — a copy prompt is graded on voice compliance and divergence from its sample, an extraction prompt on field precision and null correctness.

## The HTML Report

Every run ends with a self-contained HTML page (zero-dependency renderer, [`render_result.py`](skills/prompt-architect/scripts/render_result.py)):

1. your original request, verbatim — check nothing got distorted;
2. the extracted intent — confirm before reading outputs;
3. **candidate grid** (when multi-candidate): strategy badge, hypothesis, ⚖ tradeoff, score; the judge's pick highlighted;
4. the prompts — one-click copy, batch copy, EN/ZH side-by-side for image prompts;
5. a genre-aware quality checklist (a copywriting prompt is never nagged about JSON compliance);
6. change rationale — every edit traceable to an intent;
7. **"redo" generator** — untick failed checklist items and it assembles the rework instruction for you.

## FAQ

**Can I call `pa-optimize` directly?**
No — and you don't need to. Sub-skills are internal stages; bypassing the entry skips injection fencing and intent mining, which is precisely what produces generic output. Just state your need. (`pa-coding` is the one exception — the coding lane is built for direct invocation.)

**How do I know the skills are installed?**
`ls .claude/skills` in your project → you should see `prompt-architect` plus seven `pa-*` folders. Then restart Claude Code and ask naturally.

**What are the `{{placeholders}}` in results?**
Information you never provided (brand name, coupon caps…). The suite refuses to fabricate — swap them with real values before use. They also make the prompt reusable as a template.

**Do the generated prompts only work with Claude?**
No. Results are plain text — paste them into ChatGPT, Gemini, Midjourney, or any tool. Only the pipeline itself (interviewing, candidates, judging) runs on Claude Code.

**Is the judge's score trustworthy?**
It's a rubric compiled from *your* success criteria, scored reasons-first, with position-swapped pairwise comparison to kill ordering bias. Still an LLM judging — treat it as a strong signal, not ground truth.

**Will it work in my language?**
Yes. Skills operate in whatever language you use; ask in English, get English prompts — the showcase above was produced from English inputs. The [Chinese README](README_zh.md) has extra material (an onboarding guide for non-technical colleagues, knowledge-base HTML).

## Contributing

Issues and PRs welcome — especially:

- new genre templates or strategy tips (with evidence they produce *structurally* different skeletons);
- vendor matrix updates for new image/video models;
- trigger-regression cases: edit any skill `description`, then run the cases in [`evals/trigger-cases.yaml`](evals/trigger-cases.yaml) before and after (`must_not_trigger` hits = fail).

Edit only the sources under `skills/`, then run `scripts/sync-skills.sh`.

## Credits & License

Rules distilled from source-level analysis of 20 top prompt-engineering frameworks — DSPy, guidance, outlines, instructor, LangGPT, BAML, guardrails, TextGrad, promptfoo, Prompty, LMQL, ell, mirascope, promptbase, 12-factor-agents, and more. Full knowledge base: [`docs/prompt-engineering-knowledge.html`](docs/prompt-engineering-knowledge.html) (raw on GitHub — download and open in a browser).

[MIT](LICENSE) © Cy4nLiang

*The three showcase examples were produced by this suite's own pipeline — we eat our own dog food.*
