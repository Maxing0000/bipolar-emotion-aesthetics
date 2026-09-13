# BEA 技能包安装指南

> 多种安装方式，5分钟搞定，零配置开箱即用。

---

## 目录

- [方式一：一键安装脚本（推荐）](#方式一一键安装脚本推荐)
- [方式二：Make 安装](#方式二make-安装)
- [方式三：手动安装](#方式三手动安装)
- [方式四：Git 克隆安装](#方式四git-克隆安装)
- [安装后验证](#安装后验证)
- [命令行工具使用](#命令行工具使用)
- [卸载与更新](#卸载与更新)
- [常见问题](#常见问题)
- [支持的AI平台](#支持的ai平台)

---

## 方式一：一键安装脚本（推荐）

### macOS / Linux

```bash
# 1. 解压技能包
unzip bipolar-emotion-aesthetics-v2.0.0.zip
cd bipolar-emotion-aesthetics

# 2. 运行安装脚本（自动检测技能目录）
chmod +x install.sh
./install.sh
```

安装脚本会自动：
- ✅ 检测你的操作系统和已安装的AI客户端
- ✅ 找到正确的技能目录（豆包/Claude/通用）
- ✅ 备份已有版本（如果存在）
- ✅ 复制所有文件并设置权限
- ✅ 验证安装完整性
- ✅ 显示快速开始指南

### Windows

```powershell
# 1. 解压技能包
# 2. 进入目录
cd bipolar-emotion-aesthetics

# 3. 以管理员身份运行 PowerShell，执行安装脚本
.\install.ps1
```

> 如果遇到执行策略限制，先运行：`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### 安装脚本选项

```bash
# 自动检测安装
./install.sh

# 安装到指定目录
./install.sh --path /path/to/skills

# 强制覆盖已有安装
./install.sh --force

# 仅检查环境，不安装
./install.sh --check

# 显示帮助
./install.sh --help
```

---

## 方式二：Make 安装

如果你的系统有 `make`（macOS/Linux默认有，Windows需安装）：

```bash
# 安装
make install

# 更新
make update

# 卸载
make uninstall

# 检查环境
make check

# 运行测试
make test

# 显示帮助
make help
```

---

## 方式三：手动安装

如果自动检测失败，或者你想完全控制安装过程：

### 步骤1：找到技能目录

| 平台 | 默认技能目录 |
|---|---|
| 豆包 macOS | `~/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills/` |
| 豆包 Linux | `~/.doubao/agent_mode/workspace/.user_skills/` |
| 豆包 Windows | `%APPDATA%\Doubao\Default\.doubao\agent_mode\workspace\.user_skills\` |
| Claude Desktop | `~/.claude/skills/` |
| 通用 | `~/.skills/` |

### 步骤2：复制技能包

```bash
# 将整个 bipolar-emotion-aesthetics 目录复制到技能目录
cp -r bipolar-emotion-aesthetics /path/to/skills/

# 设置脚本可执行权限
chmod +x /path/to/skills/bipolar-emotion-aesthetics/scripts/*.py
```

### 步骤3：重启AI客户端

重启豆包/Claude，技能将自动加载。

---

## 方式四：Git 克隆安装

如果你想从 GitHub 直接安装并方便后续更新：

```bash
# 克隆到技能目录
git clone https://github.com/Maxing0000/bipolar-emotion-aesthetics.git /path/to/skills/bipolar-emotion-aesthetics

# 设置权限
chmod +x /path/to/skills/bipolar-emotion-aesthetics/scripts/*.py

# 后续更新
cd /path/to/skills/bipolar-emotion-aesthetics
git pull
```

---

## 安装后验证

### 验证1：检查文件完整性

```bash
# 检查核心文件是否存在
ls -la /path/to/skills/bipolar-emotion-aesthetics/

# 应该看到:
# SKILL.md  README.md  references/  scripts/  templates/  examples/
```

### 验证2：测试Python脚本

```bash
# 测试 W(T) 计算器
python3 /path/to/skills/bipolar-emotion-aesthetics/scripts/wt_calc.py --category phone --t "形状线条=4,质感触觉=3,色彩=2,构图比例=2,光影=2,细节线条=5"

# 应该输出 W(T) = 0.305，范式落点：均衡典雅
```

### 验证3：在AI中测试

重启AI客户端后，尝试提问：

```
帮我分析一下 iPhone 17 Pro 的设计
```

如果AI能调用BEA技能进行分析，说明安装成功。

---

## 命令行工具使用

安装后，可以将 `bea` 命令添加到 PATH，实现全局调用：

```bash
# 添加到 PATH（macOS/Linux）
echo 'export PATH="/path/to/skills/bipolar-emotion-aesthetics:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 或者创建符号链接
sudo ln -s /path/to/skills/bipolar-emotion-aesthetics/bea /usr/local/bin/bea
```

### bea 命令用法

```bash
# 计算 W(T)
bea calc --category phone --t "形状=4,质感=3,色彩=2"

# 完整量化分析
bea quant --category car --t "形体=3,特征线=5,灯组=6"

# 交互模式图片分析
bea analyze --interactive

# 查看文档列表
bea docs

# 查看示例列表
bea examples

# 查看模板列表
bea templates

# 显示版本
bea version

# 显示帮助
bea help
```

---

## 卸载与更新

### 卸载

```bash
# 一键卸载（自动检测并删除所有安装）
./uninstall.sh

# 或手动删除
rm -rf /path/to/skills/bipolar-emotion-aesthetics
```

### 更新

```bash
# 一键更新（自动备份+覆盖）
./update.sh

# 或强制重新安装
./install.sh --force

# Git 安装的更新
cd /path/to/skills/bipolar-emotion-aesthetics
git pull
```

---

## 常见问题

### Q1: 安装后AI没有识别到技能？

**A:** 请尝试以下步骤：
1. 完全重启AI客户端（不只是关闭窗口）
2. 检查技能目录路径是否正确
3. 确认 `SKILL.md` 文件存在且格式正确（开头有 `name:` 和 `description:`）
4. 检查文件权限：`chmod -R 755 /path/to/skills/bipolar-emotion-aesthetics`

### Q2: Python脚本运行报错？

**A:** 
- 确认已安装 Python 3.6+：`python3 --version`
- 所有脚本仅使用Python标准库，无需安装额外依赖
- 如果是权限问题：`chmod +x scripts/*.py`

### Q3: Windows下PowerShell无法运行脚本？

**A:** 需要调整执行策略：
```powershell
# 以管理员身份运行PowerShell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# 然后重新运行安装脚本
.\install.ps1
```

### Q4: 可以安装到多个AI平台吗？

**A:** 可以！安装脚本会检测所有已安装的AI平台，你可以选择安装到多个目录。每个平台独立使用，互不影响。

### Q5: 如何自定义技能行为？

**A:** 
- 修改 `references/` 下的文档来调整理论内容
- 修改 `scripts/` 下的Python脚本来调整计算逻辑
- 修改 `templates/` 下的模板来调整输出格式
- 修改 `SKILL.md` 中的 `description` 来调整触发条件

### Q6: 安装会覆盖我的自定义修改吗？

**A:** 安装脚本会自动备份已有版本到 `bipolar-emotion-aesthetics.backup.YYYYMMDDHHMMSS/`，你可以随时从备份恢复。建议使用 `--force` 前先备份你的自定义修改。

---

## 支持的AI平台

| 平台 | 自动检测 | 安装方式 | 状态 |
|---|---|---|---|
| 豆包 (Doubao) macOS | ✅ | install.sh | 已测试 |
| 豆包 (Doubao) Windows | ✅ | install.ps1 | 已测试 |
| 豆包 (Doubao) Linux | ✅ | install.sh | 已测试 |
| Claude Desktop | ✅ | install.sh | 已测试 |
| 其他支持技能的AI | ⚠️ 手动指定路径 | install.sh --path | 理论支持 |
| 通用目录 | ✅ | ~/.skills/ | 已测试 |

---

## 技术支持

- **GitHub Issues**: https://github.com/Maxing0000/bipolar-emotion-aesthetics/issues
- **开源地址**: https://github.com/Maxing0000/bipolar-emotion-aesthetics
- **版本**: v2.0.0
- **作者**: 星空本空
- **许可**: CC BY 4.0

---

*安装遇到问题？先运行 `./install.sh --check` 检查环境，再查看上方常见问题。*
