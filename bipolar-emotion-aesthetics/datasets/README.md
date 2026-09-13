# BEA 标注数据集

> 双极情绪美学（Bipolar Emotion Aesthetics，BEA）标注数据集，用于量化模型校准和自动标注模型训练。

## 文件说明

| 文件 | 说明 |
|---|---|
| `bea_annotation_template.csv` | CSV 格式标注模板（Excel 可打开） |
| `bea_annotation_template.json` | JSON 格式标注模板（支持嵌套结构） |
| `annotation_guide.md` | 标注指南（标注者必读） |

## 数据集版本

| 版本 | 样本量 | 发布日期 | 说明 |
|---|---|---|---|
| v0.1 | 50（目标） | 2026-09 | 初步验证模型可行性 |
| v0.5 | 200（目标） | TBD | 品类权重校准 |
| v1.0 | 500（目标） | TBD | 跨品类验证、论文发表 |
| v2.0 | 2000+（目标） | TBD | 训练自动标注模型 |

## 标注字段

### 基础信息
- `sample_id`：样本唯一 ID，格式 BEA-XXX
- `category`：品类：phone/car/brand/ui/architecture/fashion
- `object_name`：对象名称，如 iPhone 17 Pro
- `image_url`：图片 URL（可选）

### 维度强度（0.0-10.0 连续值）
按品类不同，维度不同：
- **phone**：形状线条、质感触觉、色彩、构图比例、光影、细节线条
- **car**：形体曲面动势、特征线条、灯组图形、比例姿态、材质光影
- **brand**：图形形状、色彩、字体、版式构图、质感
- **ui**：布局留白、色彩对比、组件形、动效、字体图标
- **architecture**：空间尺度、形体造型、材料质感、光影、色彩、动线布局
- **fashion**：廓形、面料质感、色彩、细节配件、比例剪裁

### 注意力系数（0.5-2.0，可选）
- `attention_*`：各维度注意力系数，默认 1.0

### 子维度评分（0-5 整数，共 12 项）
- **双极张力**：对立清晰度、成对呼应度、范式匹配度
- **结构秩序**：主辅层级、比例精当度、全局统一性
- **阈值安全**：本能红线、认知负荷、文化适配
- **语境适配**：受众匹配、场景功能、时代位置

### 整体评分与判定
- `overall_score`：整体美感评分（0-100）
- `paradigm`：范式判定
- `wt_v1`：v1.0 W(T) 计算值（自动生成）
- `wt_v2`：v2.0 W(T) 计算值（自动生成）
- `bea_score`：BEA 美感总分（自动生成）

### 标注元数据
- `annotator_id`：标注者 ID
- `confidence`：标注置信度（0-1）
- `notes`：备注
- `timestamp`：标注时间

## 使用方法

### 计算 W(T) 和 BEA 美感总分

```bash
# 简化模式（v1.0 兼容）
python3 ../scripts/bea_quant_v2.py --category phone --t "形状线条=2.5,质感触觉=3.0,..."

# 完整模式（v2.0）
python3 ../scripts/bea_quant_v2.py --category phone --t "..." --mode full --report

# 带子维度评分
python3 ../scripts/bea_quant_v2.py --category phone --t "..." --subscores "对立清晰度=4,..." --report
```

### 批量验证

```bash
# 验证 CSV 文件中的所有样本
python3 ../scripts/verify_annotations.py --input bea_annotations.csv
```

## 质量控制

- 每个样本至少 2 名标注者独立标注
- 标注者间一致性（ICC）目标 > 0.7
- 不一致样本由第三人仲裁
- 每月进行一次标注者校准培训

## 引用

如使用本数据集，请引用：

```
星空本空. (2026). Bipolar Emotion Aesthetics: A Computational Framework for Formal Beauty Analysis and Design. Preprints.org, ID: 233113.
```

## 许可证

CC BY 4.0（署名 4.0 国际）
