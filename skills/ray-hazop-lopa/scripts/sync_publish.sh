#!/bin/bash
# ray-hazop-lopa 发布辅助：SkillHub dry-run / 正式发布
# 说明：专家目录已用 Junction 指向用户级源，无需同步副本。
# 用法:
#   bash sync_publish.sh            # dry-run 预检
#   bash sync_publish.sh --pub "v1.2.0 更新说明"   # 正式发布 SkillHub
set -e

SRC="$HOME/.workbuddy/skills/ray-hazop-lopa"
SRC_WIN=$(cygpath -w "$SRC" 2>/dev/null || echo "$SRC")

[ -d "$SRC" ] || { echo "[ERR] 源目录不存在: $SRC"; exit 1; }

echo "== SkillHub dry-run 预检（源: $SRC_WIN）=="
skillhub publish "$SRC_WIN" --dry-run

if [ "$1" = "--pub" ]; then
  shift
  CHANGELOG="${1:-版本更新}"
  echo "== 正式发布 SkillHub =="
  skillhub publish "$SRC_WIN" --changelog "$CHANGELOG"
  echo "== 验证上架 =="
  skillhub search ray-hazop-lopa | head -6
else
  echo "（未正式发布；如需发布: bash sync_publish.sh --pub \"更新说明\"）"
fi
echo "== 完成（专家目录 junction 已自动同步，无需手动复制）=="
