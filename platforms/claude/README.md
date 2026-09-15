# Claude 平台适配

## 快速使用

### 方式1：Project Instructions（推荐）
1. 打开 [Claude](https://claude.ai/)
2. 新建项目（Project）
3. 进入 **Project Settings** → **Add Project Instruction**
4. 将 `../universal-system-prompt.md` 中的内容粘贴进去
5. 保存，在该项目中开始对话

### 方式2：上传文件作为 Context
1. 在对话中上传 `SKILL.md` 和 `references/` 目录下的文档
2. 发送："请按照上传的 BEA 框架工作"
3. 开始使用

### 方式3：单次对话使用
在新对话开头发送：
```
请你扮演 BEA（双极情绪美学）专家，按照以下框架工作：[粘贴 universal-system-prompt.md 内容]
```

## 最佳实践

- **Claude 3.5 Sonnet / Opus**：支持长 context，可将完整 `references/` 文档上传
- **Artifacts 功能**：分析结果可直接生成 Artifact，方便保存和分享
- **图片分析**：Claude 支持图片上传，可直接上传设计图进行分析
- **代码执行**：Claude 可直接运行 `bea_quant.py` 进行精确计算
