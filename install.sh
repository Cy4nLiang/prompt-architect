#!/usr/bin/env bash
# 安装 prompt-architect 套件到 Claude Code 的 skills 目录。
#   ./install.sh            装到全局 ~/.claude/skills/（所有项目可用）
#   ./install.sh --project  装到当前目录 ./.claude/skills/（仅当前项目）
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/skills"
if [ "${1:-}" = "--project" ]; then
  DST="$(pwd)/.claude/skills"
else
  DST="$HOME/.claude/skills"
fi

mkdir -p "$DST"
for d in prompt-architect pa-deconstruct pa-optimize pa-precise-retrieval pa-image; do
  if [ -e "$DST/$d" ]; then
    echo "⚠️  已存在，跳过（如需覆盖请先手动删除）：$DST/$d"
  else
    cp -R "$SRC/$d" "$DST/$d"
    echo "✓ 安装 $d"
  fi
done
chmod +x "$DST/prompt-architect/scripts/render_result.py" 2>/dev/null || true
echo "完成。重开 Claude Code，对它说「用 prompt-architect 优化…」即可。"
