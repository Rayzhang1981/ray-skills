#!/bin/bash
# sync_from_local.sh — 从 ~/.workbuddy/skills 一键同步本仓库 skills/
# 白名单 = 仓库 skills/ 现有目录（只同步已收录的开源技能，不含 CCPS/私用层）
# 用法:
#   bash scripts/sync_from_local.sh            # 预览将同步哪些 + 拷贝
#   bash scripts/sync_from_local.sh --dry-run  # 只预览不拷贝
set -e

HERE="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$HOME/.workbuddy/skills"
DEST="$HERE/skills"
DRY="${1:-}"

echo "源: $SRC"
echo "目标: $DEST"
echo "白名单（仓库已收录）:"
count=0
for d in "$DEST"/ray-*/; do
  name="$(basename "$d")"
  [ -d "$SRC/$name" ] || { echo "  ⚠️ $name 在本地源不存在（跳过）"; continue; }
  count=$((count+1))
  echo "  - $name"
  if [ "$DRY" != "--dry-run" ]; then
    rsync -a --delete --exclude '__pycache__/' --exclude '*.pyc' \
      "$SRC/$name/" "$DEST/$name/"
  fi
done
echo "---"
echo "共 $count 个技能"
if [ "$DRY" = "--dry-run" ]; then
  echo "（dry-run：未拷贝）"
else
  echo "拷贝完成。请检查 git status 后提交："
  echo "  git add -A && git commit -m 'sync: <技能名> vX.Y.Z（一句话）' && git push"
fi
