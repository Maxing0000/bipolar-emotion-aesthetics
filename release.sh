#!/usr/bin/env bash
# BEA 三平台发版脚本
# 用法: ./release.sh <版本号> "<更新摘要>"
# 示例: ./release.sh 1.2.1 "新增 FAQ 与网页计算器"
#
# 依赖: git, gh(GitHub CLI), ModelScope SDK(可选, 需 MS_TOKEN 环境变量)
# 前提: 在仓库根目录执行; Gitee 走 ~/.ssh/gitee_bea_key
set -euo pipefail

VER="${1:?用法: ./release.sh <版本号> \"<更新摘要>\"}"
SUMMARY="${2:?需要更新摘要}"
TAG="v${VER}"
GH_REMOTE="origin"
GITEE_REMOTE="git@gitee.com:maxing0000/bipolar-emotion-aesthetics.git"
MS_DATASET="xkbk0000/bipolar-emotion-aesthetics"
PY_MS="${MS_PYTHON:-/Users/m/.workbuddy/binaries/python/envs/default/bin/python3}"

echo "==> BEA 发版 ${TAG}: ${SUMMARY}"

# ── 1. 版本号替换 ─────────────────────────────
sed -i '' "s/^version: \"[0-9.]*\"/version: \"${VER}\"/" bipolar-emotion-aesthetics/SKILL.md
sed -i '' "s/badge\/version-[0-9.]*-blue/badge\/version-${VER}-blue/" README.md
sed -i '' "s/（BEA）：可计算的形式美学技能》v[0-9.]*,/(BEA)：可计算的形式美学技能》v${VER},/" README.md
sed -i '' "s/》v[0-9.]*, 2026/》v${VER}, 2026/" README.md
sed -i '' "s/version= {[0-9.]*}/version= {${VER}}/" README.md
grep -q "version: \"${VER}\"" bipolar-emotion-aesthetics/SKILL.md || { echo "✗ SKILL.md 版本替换失败"; exit 1; }

# ── 2. 更新日志 ───────────────────────────────
TODAY=$(date +%Y-%m-%d)
if ! grep -q "### ${TAG}（${TODAY}）" README.md; then
  awk -v tag="### ${TAG}（${TODAY}）" -v sum="${SUMMARY}" '
    /^## 更新日志/ && !done { print; print ""; print tag; print ""; print "- " sum; print ""; done=1; next }
    { print }
  ' README.md > README.md.tmp && mv README.md.tmp README.md
fi

# ── 3. 提交 / 打标签 / 推 GitHub ─────────────
git add -A
git commit -m "${TAG}: ${SUMMARY}" || true
git tag "${TAG}"
git push "${GH_REMOTE}" main --tags
echo "✓ GitHub 已推送"

# ── 4. Gitee 镜像 ────────────────────────────
if git push "${GITEE_REMOTE}" main --tags 2>/dev/null; then
  echo "✓ Gitee 已同步"
else
  echo "⚠ Gitee 推送失败（检查 ~/.ssh/gitee_bea_key），可稍后手动: git push ${GITEE_REMOTE} main --tags"
fi

# ── 5. GitHub Release ────────────────────────
gh release create "${TAG}" --title "${TAG} — ${SUMMARY}" --notes "${SUMMARY}

完整变更见 README 更新日志。" 2>/dev/null && echo "✓ Release 已创建" || echo "⚠ Release 创建失败或已存在"

# ── 6. ModelScope 数据集（可选）──────────────
if [ -n "${MS_TOKEN:-}" ]; then
  STAGE=$(mktemp -d)
  rsync -a --exclude='.git' --exclude='dataset_infos.json' --exclude='.gitattributes' ./ "${STAGE}/"
  "${PY_MS}" - "$STAGE" << 'PYEOF'
import sys
from modelscope.hub.api import HubApi
stage = sys.argv[1]
api = HubApi()
api.login(__import__('os').environ['MS_TOKEN'])
api.upload_folder(
    repo_id='xkbk0000/bipolar-emotion-aesthetics',
    folder_path=stage, path_in_repo='', repo_type='dataset',
    commit_message='sync: ' + __import__('os').environ.get('MS_MSG', 'sync with GitHub'))
print('✓ ModelScope 已同步')
PYEOF
  rm -rf "${STAGE}"
else
  echo "⚠ 跳过 ModelScope：未设置 MS_TOKEN 环境变量"
fi

echo "==> 完成: ${TAG} — GitHub / Gitee / ModelScope"
