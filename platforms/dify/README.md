# Dify 平台适配

## 快速使用

### 方式1：创建应用（推荐）
1. 打开 Dify，创建新应用（Chatflow / Workflow / Chat App）
2. 在 **编排** → **提示词** → **系统提示词** 中粘贴 `../universal-system-prompt.md` 内容
3. （可选）添加 **代码节点**，导入 `scripts/bea_quant.py` 进行精确计算
4. （可选）添加 **知识库**，上传 `references/` 文档
5. 发布并使用

### 方式2：添加为工具
1. 在 Dify 中创建 **自定义工具**
2. 将 `bea_quant.py` 封装为 API（可用 Flask/FastAPI 包装）
3. 配置工具参数：category、t_values、target 等
4. 在应用中调用该工具

## 最佳实践

- **Chatflow 模式**：适合多轮对话分析，可串联"识别品类→维度打分→计算W(T)→诊断病症→给出建议"流程
- **代码节点**：Dify 支持 Python 代码节点，可直接运行 `bea_quant.py`
- **知识库**：将 `references/` 文档上传为知识库，用 RAG 提升理论准确性
- **变量传递**：将 W(T)、范式、病症等作为变量传递给后续节点，生成结构化报告
