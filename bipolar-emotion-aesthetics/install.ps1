<#
.SYNOPSIS
    BEA 双极情绪美学技能包 - Windows 一键安装脚本

.DESCRIPTION
    自动检测并安装 BEA 技能包到 Windows 系统的 AI 技能目录

.PARAMETER Path
    自定义安装路径

.PARAMETER Force
    强制覆盖已有安装

.PARAMETER Check
    仅检查环境，不安装

.EXAMPLE
    .\install.ps1
    自动检测并安装

.EXAMPLE
    .\install.ps1 -Path "C:\Users\You\skills"
    安装到指定目录

.EXAMPLE
    .\install.ps1 -Force
    强制覆盖安装
#>

param(
    [string]$Path = "",
    [switch]$Force = $false,
    [switch]$Check = $false
)

# 配置
$SkillName = "bipolar-emotion-aesthetics"
$SkillVersion = "2.0.0"
$SkillDisplayName = "BEA 双极情绪美学"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 颜色函数
function Write-Step($msg)  { Write-Host "▶ $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info($msg)  { Write-Host "ℹ️  $msg" -ForegroundColor Blue }

# 打印横幅
function Write-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║           BEA 双极情绪美学技能包 v$SkillVersion 安装程序              ║" -ForegroundColor Magenta
    Write-Host "║           Bipolar Emotion Aesthetics Skill Pack               ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

# 检测 Python
function Test-Python {
    try {
        $python = Get-Command python -ErrorAction Stop
        $version = & python --version 2>&1
        Write-Ok "Python 已安装: $version"
        return $true
    } catch {
        Write-Warn "Python 未安装，脚本功能将受限（仅文档可用）"
        return $false
    }
}

# 检测技能目录
function Find-SkillDirs {
    $dirs = @()

    # 豆包 Windows
    $doubaoDir = "$env:APPDATA\Doubao\Default\.doubao\agent_mode\workspace\.user_skills"
    if (Test-Path $doubaoDir) { $dirs += $doubaoDir }

    # Claude Desktop
    $claudeDir = "$env:USERPROFILE\.claude\skills"
    if (Test-Path $claudeDir) { $dirs += $claudeDir }

    # 通用
    $genericDir = "$env:USERPROFILE\.skills"
    if (Test-Path $genericDir) { $dirs += $genericDir }

    return $dirs
}

# 选择安装目录
function Select-InstallDir {
    if ($Path) {
        if (-not (Test-Path $Path)) {
            Write-Warn "目录不存在，尝试创建: $Path"
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
        }
        return $Path
    }

    $dirs = Find-SkillDirs

    if ($dirs.Count -eq 0) {
        $defaultDir = "$env:USERPROFILE\.skills"
        Write-Warn "未检测到已安装的AI技能目录"
        Write-Info "将使用默认目录: $defaultDir"
        New-Item -ItemType Directory -Path $defaultDir -Force | Out-Null
        return $defaultDir
    }

    if ($dirs.Count -eq 1) {
        Write-Info "检测到技能目录: $($dirs[0])"
        return $dirs[0]
    }

    Write-Host ""
    Write-Host "检测到多个技能目录，请选择安装位置:" -ForegroundColor White
    for ($i = 0; $i -lt $dirs.Count; $i++) {
        Write-Host "  $($i+1)) $($dirs[$i])" -ForegroundColor Green
    }
    Write-Host "  0) 自定义路径" -ForegroundColor Yellow
    Write-Host ""

    $choice = Read-Host "请输入序号 [1-$($dirs.Count)]"

    if ($choice -eq "0") {
        $custom = Read-Host "请输入自定义路径"
        New-Item -ItemType Directory -Path $custom -Force | Out-Null
        return $custom
    } elseif ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le $dirs.Count) {
        return $dirs[[int]$choice - 1]
    } else {
        Write-Err "无效选择"
        exit 1
    }
}

# 备份已有版本
function Backup-Existing($targetDir) {
    $skillDir = Join-Path $targetDir $SkillName

    if (Test-Path $skillDir) {
        if (-not $Force) {
            Write-Warn "检测到已有安装: $skillDir"
            $confirm = Read-Host "是否覆盖？(y/N)"
            if ($confirm -notmatch '^[Yy]$') {
                Write-Info "安装已取消"
                exit 0
            }
        }

        $backupDir = Join-Path $targetDir "$SkillName.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
        Write-Step "备份已有版本到: $backupDir"
        Copy-Item -Path $skillDir -Destination $backupDir -Recurse -Force
        Write-Ok "备份完成"
    }
}

# 安装文件
function Install-Files($targetDir) {
    $skillDir = Join-Path $targetDir $SkillName

    Write-Step "正在安装到: $skillDir"

    # 创建目录
    New-Item -ItemType Directory -Path $skillDir -Force | Out-Null

    # 复制核心文件
    Copy-Item -Path (Join-Path $ScriptDir "SKILL.md") -Destination $skillDir -Force -ErrorAction SilentlyContinue
    Copy-Item -Path (Join-Path $ScriptDir "README.md") -Destination $skillDir -Force -ErrorAction SilentlyContinue

    # 复制子目录
    foreach ($subdir in @("references", "scripts", "templates", "examples")) {
        $src = Join-Path $ScriptDir $subdir
        if (Test-Path $src) {
            $dst = Join-Path $skillDir $subdir
            if (Test-Path $dst) { Remove-Item -Path $dst -Recurse -Force }
            Copy-Item -Path $src -Destination $skillDir -Recurse -Force
        }
    }

    Write-Ok "文件复制完成"
}

# 验证安装
function Test-Installation($skillDir) {
    $errors = 0
    Write-Step "验证安装..."

    $required = @("SKILL.md", "references\theory.md", "references\paradigms.md",
                  "references\method.md", "references\playbooks.md",
                  "scripts\wt_calc.py", "scripts\bea_quant.py")

    foreach ($file in $required) {
        $fullPath = Join-Path $skillDir $file
        if (Test-Path $fullPath) {
            Write-Ok "  ✓ $file"
        } else {
            Write-Err "  ✗ $file 缺失"
            $errors++
        }
    }

    # 验证 Python 语法
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Get-ChildItem -Path (Join-Path $skillDir "scripts") -Filter "*.py" | ForEach-Object {
            $result = & python -m py_compile $_.FullName 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Ok "  ✓ $($_.Name) 语法正确"
            } else {
                Write-Err "  ✗ $($_.Name) 语法错误"
                $errors++
            }
        }
    }

    if ($errors -eq 0) {
        Write-Ok "安装验证通过！"
        return $true
    } else {
        Write-Err "安装验证失败，发现 $errors 个问题"
        return $false
    }
}

# 主流程
Write-Banner

Write-Step "环境检测"
Write-Info "操作系统: Windows"
Test-Python | Out-Null

if ($Check) {
    Write-Info "仅检查模式，不执行安装"
    Write-Host ""
    Write-Step "检测到的技能目录:"
    $dirs = Find-SkillDirs
    if ($dirs.Count -eq 0) {
        Write-Warn "未检测到已安装的AI技能目录"
    } else {
        $dirs | ForEach-Object { Write-Ok "  - $_" }
    }
    exit 0
}

Write-Host ""
$targetDir = Select-InstallDir

if (-not $targetDir) {
    Write-Err "无法确定安装目录"
    exit 1
}

Write-Host ""
Backup-Existing $targetDir

Write-Host ""
Install-Files $targetDir

Write-Host ""
$skillDir = Join-Path $targetDir $SkillName
if (Test-Installation $skillDir) {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  🎉 安装成功！                                                 ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 安装信息" -ForegroundColor White
    Write-Host "  技能名称: $SkillDisplayName"
    Write-Host "  版本: v$SkillVersion"
    Write-Host "  安装路径: $skillDir"
    Write-Host ""
    Write-Host "🚀 快速开始" -ForegroundColor White
    Write-Host "  1. 重启你的 AI 客户端，技能将自动加载"
    Write-Host "  2. 向 AI 提问，例如:"
    Write-Host "     - ""帮我分析一下 iPhone 17 Pro 的设计"""
    Write-Host "     - ""这个海报哪里不好看？怎么改？"""
    Write-Host "     - ""上传一张图片，分析它的美感"""
    Write-Host ""
    Write-Host "🛠️  命令行工具" -ForegroundColor White
    Write-Host "  python $skillDir\scripts\wt_calc.py --category phone --t ""形状=4,质感=3"""
    Write-Host "  python $skillDir\scripts\bea_quant.py --category car --t ""形体=3,特征线=5"""
    Write-Host ""
    exit 0
} else {
    Write-Err "安装验证失败"
    exit 1
}
