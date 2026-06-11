#!/usr/bin/env bash
# prompt-architect 套件唯一安装方式
#
# 项目 skills/ 是唯一源（single source of truth）。
# ⛔ 禁止手动 cp / 复制 skill 目录 —— 双副本漂移（旧版残留、缺子 skill）
#    正是触发错配的根源。改 skill 一律改 skills/ 下的源，然后跑本脚本。
#
# 用法:
#   scripts/sync-skills.sh                    # 同步到 .claude/skills/（及存在的 .agents/skills/）
#   scripts/sync-skills.sh <额外目标目录>...   # 显式同步到其它位置（不建议用户级 ~/.claude/skills，
#                                             # 旧版会泄漏到所有项目；如确需全局安装请自负同步责任）
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/skills"
PA_SKILLS=(prompt-architect pa-deconstruct pa-optimize pa-precise-retrieval pa-eval pa-image pa-video pa-coding)

DESTS=("$ROOT/.claude/skills")
[[ -d "$ROOT/.agents/skills" ]] && DESTS+=("$ROOT/.agents/skills")
DESTS+=("$@")

for dest in "${DESTS[@]}"; do
  mkdir -p "$dest"
  for s in "${PA_SKILLS[@]}"; do
    if [[ ! -d "$SRC/$s" ]]; then
      echo "✗ 源缺失: $SRC/$s" >&2
      exit 1
    fi
    rsync -a --delete "$SRC/$s/" "$dest/$s/"
  done
  echo "✓ ${#PA_SKILLS[@]} 个 skill 已同步 -> $dest"
done
