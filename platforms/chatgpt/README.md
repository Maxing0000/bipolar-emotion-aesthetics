# ChatGPT / GPTs 平台适配

## 快速使用

### 方式1：Custom Instructions（推荐，最简单）
1. 打开 [ChatGPT](https://chat.openai.com/)
2. 点击左下角头像 → **Custom instructions**
3. 将 `../universal-system-prompt.md` 中的内容粘贴到 "Additional instructions"
4. 保存，开始使用

### 方式2：创建 GPT（可分享）
1. 打开 ChatGPT → **Explore** → **Create a GPT**
2. 在 **Configure** 标签页的 **Instructions** 中粘贴 `../universal-system-prompt.md` 内容
3. （可选）上传 `references/` 目录下的文档作为 Knowledge
4. （可选）添加 Code Interpreter，可直接运行 `scripts/bea_quant.py`
5. 保存并分享

### 方式3：单次对话使用
在新对话开头发送：
```
请你扮演 BEA（双极情绪美学）专家，按照以下框架工作：[粘贴 universal-system-prompt.md 内容]
```

## 最佳实践

- **GPTs 模式**：建议开启 Code Interpreter，可直接调用 `bea_quant.py` 进行精确计算
- **Knowledge 上传**：将 `references/01-core-theory.md`、`references/05-case-studies.md` 上传为 Knowledge，提升分析准确性
- **图片分析**：GPT-4V 支持图片上传，可直接上传设计图进行分析
