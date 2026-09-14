# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

# BEA v2.2 一键安装脚本（Windows PowerShell）
#
# 用法：
#   从 GitHub 安装：  irm https://raw.githubusercontent.com/Maxing0000/bipolar-emotion-aesthetics/main/install.ps1 | iex
#   从本地安装：     .\install.ps1
#   指定安装目录：   $env:SKILL_DIR="C:\path\to\skills"; .\install.ps1

$ErrorActionPreference = "Stop"
$SkillName = "bipolar-emotion-aesthetics"
$RepoUrl = "https://github.com/Maxing0000/bipolar-emotion-aesthetics.git"

function Write-Info($msg)  { Write-Host "[INFO] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# ── 检测 Skill 目录 ──────────────────────────────────
function Find-SkillDir {
    if ($env:SKILL_DIR -and (Test-Path $env:SKILL_DIR)) {
        return $env:SKILL_DIR
    }

    $candidates = @(
        "$env:APPDATA\Doubao\Default\.doubao\agent_mode\workspace\.user_skills",
        "$env:USERPROFILE\.doubao\agent_mode\workspace\.user_skills",
        "$env:APPDATA\doubao\agent_mode\workspace\.user_skills"
    )

    foreach ($dir in $candidates) {
        if (Test-Path $dir) {
            return $dir
        }
    }
    return $null
}

# ── 检查 Python ──────────────────────────────────────
function Find-Python {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return "python" }
    $python3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3) { return "python3" }
    return $null
}

# ── 主流程 ───────────────────────────────────────────
Write-Host "========================================"
Write-Host "  BEA v2.2 安装程序 (Windows)"
Write-Host "========================================"
Write-Host ""

$python = Find-Python
if (-not $python) {
    Write-Error "未找到 Python，请先安装：https://www.python.org/downloads/"
    exit 1
}
Write-Info "Python: $(& $python --version 2>&1)"

$skillDir = Find-SkillDir
if (-not $skillDir) {
    Write-Error "未检测到 Skill 目录。"
    Write-Host ""
    Write-Host "请手动指定目录："
    Write-Host "  `$env:SKILL_DIR=`"C:\path\to\skills`"; .\install.ps1"
    Write-Host ""
    Write-Host "常见 Skill 目录位置："
    Write-Host "  %APPDATA%\Doubao\Default\.doubao\agent_mode\workspace\.user_skills"
    exit 1
}

Write-Info "Skill 目录: $skillDir"
$dest = Join-Path $skillDir $SkillName

# 已安装检测
if (Test-Path $dest) {
    Write-Warn "已检测到旧版本: $dest"
    $answer = Read-Host "是否覆盖？(y/N)"
    if ($answer -notmatch "^[yY]") {
        Write-Info "取消安装"
        exit 0
    }
    Remove-Item -Recurse -Force $dest
}

Write-Info "安装到: $dest"

# 获取 skill 文件
if ((Test-Path "SKILL.md") -and (Test-Path "scripts\bea_quant.py")) {
    Write-Info "检测到本地 skill 文件，直接复制"
    Copy-Item -Recurse SKILL.md, scripts, references, templates $dest
} else {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "未找到 git，请先安装 git 或手动下载 zip 包"
        exit 1
    }
    $tmp = Join-Path $env:TEMP ("bea-install-" + [System.Guid]::NewGuid().ToString("N"))
    Write-Info "从 GitHub 克隆..."
    git clone --depth 1 $RepoUrl $tmp | Out-Null
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item -Recurse "$tmp\SKILL.md", "$tmp\scripts", "$tmp\references", "$tmp\templates" $dest
    Remove-Item -Recurse -Force $tmp
}

# 验证
Write-Host ""
Write-Info "运行自测试..."
Push-Location $dest
try {
    & $python scripts/bea_quant.py test | Out-Null
    Write-Info "自测试通过"
} catch {
    Write-Warn "自测试失败，请检查 Python 环境"
    & $python scripts/bea_quant.py test
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "========================================"
Write-Host "  ✅ 安装成功！" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "  位置: $dest"
Write-Host ""
Write-Host "  快速开始："
Write-Host "    cd $dest"
Write-Host "    python scripts/bea_quant.py template --category phone"
Write-Host "    python scripts/bea_quant.py report --category phone --t `"形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6`""
Write-Host ""
