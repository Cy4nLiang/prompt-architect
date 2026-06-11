#!/usr/bin/env bash
# 安装 prompt-architect 套件到 Claude Code 的 skills 目录。
#   ./install.sh            装到全局 ~/.claude/skills/（所有项目可用）
#   ./install.sh --project  装到当前目录 ./.claude/skills/（仅当前项目，推荐）
#
# 重复执行 = 升级到仓库最新版（rsync --delete 同步，本地对 skill 的手改会被覆盖）。
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/skills"
if [ "${1:-}" = "--project" ]; then
  DST="$(pwd)/.claude/skills"
else
  DST="$HOME/.claude/skills"
fi

PA_SKILLS=(prompt-architect pa-deconstruct pa-optimize pa-precise-retrieval pa-eval pa-image pa-video pa-coding)

mkdir -p "$DST"
for d in "${PA_SKILLS[@]}"; do
  if [ ! -d "$SRC/$d" ]; then
    echo "✗ 源缺失: $SRC/$d" >&2
    exit 1
  fi
  rsync -a --delete "$SRC/$d/" "$DST/$d/"
  echo "✓ 安装/更新 $d"
done
chmod +x "$DST/prompt-architect/scripts/render_result.py" 2>/dev/null || true
echo
echo "完成（${#PA_SKILLS[@]} 个 skill → $DST）。重开 Claude Code，对它说「帮我优化这个 prompt：…」即可。"
