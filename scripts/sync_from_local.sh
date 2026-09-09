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
      --exclude 'data/' --exclude 'anchor_db.json' --exclude 'output/' \
      --exclude '*.zip' --exclude '.venv/' \
      "$SRC/$name/" "$DEST/$name/"
    # 去敏后处理：本机路径占位化（防同步冲掉开源版修改；源目录不受影响）
    find "$DEST/$name/" -type f \( -name '*.md' -o -name '*.py' -o -name '*.js' \
      -o -name '*.json' -o -name '*.sh' -o -name '*.yaml' -o -name '*.cjs' \) \
      -exec sed -i 's|C:/Users/rayzh|~/.workbuddy|g; s|D:/RayClaw|~/RayClaw|g; s|E:/LingXi|~/LingXi|g' {} + 2>/dev/null || true
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
