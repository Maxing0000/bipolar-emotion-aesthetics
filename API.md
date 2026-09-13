# BEA API 规范

> 双极情绪美学（Bipolar Emotion Aesthetics）开放 API 接口规范
> 版本：v1.13.0 | 最后更新：2026-09-13

## 概述

BEA API 提供双极情绪美学的计算、分析、诊断和设计能力，支持第三方应用集成。所有接口遵循 RESTful 设计规范，返回 JSON 格式数据。

### 基础信息

- **基础 URL**：`https://api.bea-aesthetics.com/v1`
- **认证方式**：API Key（Header: `X-API-Key`）
- **数据格式**：JSON（UTF-8）
- **速率限制**：100 次/分钟（免费版），1000 次/分钟（专业版）
- **CORS**：支持跨域请求

### 版本历史

| 版本 | 日期 | 主要变更 |
|---|---|---|
| v1.13.0 | 2026-09-13 | 新增范式动态演化API、诗意朦胧/神秘魅惑范式 |
| v1.10.0 | 2026-09-13 | 新增图片分析API、对比分析API |
| v1.0.0 | 2026-09-12 | 初始版本，基础计算和分析API |

---

## 1. 计算接口

### 1.1 计算 W(T) 危极权重

计算一组维度的整体危极权重 W(T)，并定位范式。

**请求**：
```
POST /calculate/wt
```

**请求体**：
```json
{
  "category": "phone",
  "dimensions": [
    {"name": "形状线条", "t": 2, "weight": 0.25},
    {"name": "质感触觉", "t": 3, "weight": 0.25},
    {"name": "色彩", "t": 2, "weight": 0.15},
    {"name": "构图比例", "t": 2, "weight": 0.15},
    {"name": "光影", "t": 2, "weight": 0.10},
    {"name": "细节线条", "t": 6, "weight": 0.10}
  ]
}
```

**参数说明**：
- `category`：品类（phone/car/brand/ui/architecture/fashion/music/film/custom）
- `dimensions`：维度数组，每个维度包含：
  - `name`：维度名称
  - `t`：危极强度（0-10）
  - `weight`：权重（0-1，所有维度权重之和为1）

**响应**：
```json
{
  "code": 0,
  "data": {
    "wt": 0.275,
    "paradigm": {
      "id": "affinity",
      "name": "亲和精致",
      "wt_range": [0.15, 0.30],
      "ratio": "80:20"
    },
    "quadrant": {
      "tension": "中",
      "order": "高",
      "name": "呆板平庸区边缘"
    },
    "dimension_contributions": [
      {"name": "形状线条", "contribution": 0.050},
      {"name": "质感触觉", "contribution": 0.075},
      {"name": "细节线条", "contribution": 0.060}
    ]
  }
}
```

### 1.2 计算四维评分

计算 BEA 四维评分卡（张力/秩序/阈值/语境）。

**请求**：
```
POST /calculate/score
```

**请求体**：
```json
{
  "tension": {"opposition_clarity": 8, "pairing": 7, "paradigm_match": 8},
  "order": {"primary_secondary": 9, "proportion": 8, "rhythm": 7, "hierarchy": 8, "unity": 9},
  "threshold": {"instinct_safe": 10, "cognitive": 8, "cultural": 9, "distance": 8},
  "context": {"audience_match": 8, "scenario_match": 9, "function_risk": 9, "era_position": 7}
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "scores": {
      "tension": 22,
      "order": 24,
      "threshold": 23,
      "context": 22
    },
    "total": 91,
    "level": "成熟作品",
    "weak_dimensions": [],
    "recommendations": []
  }
}
```

### 1.3 范式动态曲线计算（v1.13.0 新增）

计算作品在时间轴上的范式动态演化曲线。

**请求**：
```
POST /calculate/paradigm-curve
```

**请求体**：
```json
{
  "segments": [
    {"name": "引入", "wt": 0.15, "duration": 0.15},
    {"name": "发展", "wt": 0.25, "duration": 0.25},
    {"name": "高潮", "wt": 0.65, "duration": 0.20},
    {"name": "转折", "wt": 0.45, "duration": 0.15},
    {"name": "收束", "wt": 0.20, "duration": 0.15},
    {"name": "余韵", "wt": 0.10, "duration": 0.10}
  ]
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "curve": [
      {"time": 0.0, "wt": 0.15, "paradigm": "治愈松弛"},
      {"time": 0.15, "wt": 0.25, "paradigm": "亲和精致"},
      {"time": 0.40, "wt": 0.65, "paradigm": "冷峻克制"},
      {"time": 0.60, "wt": 0.45, "paradigm": "均衡典雅"},
      {"time": 0.75, "wt": 0.20, "paradigm": "亲和精致"},
      {"time": 0.90, "wt": 0.10, "paradigm": "治愈松弛"}
    ],
    "avg_wt": 0.30,
    "peak_wt": 0.65,
    "tension_range": 0.55,
    "narrative_quality": "优秀",
    "golden_ratio_transition": true
  }
}
```

---

## 2. 分析接口

### 2.1 文本描述分析

根据自然语言描述分析对象的 BEA 特征。

**请求**：
```
POST /analyze/text
```

**请求体**：
```json
{
  "description": "一款圆润的手机，钛金属中框，精密倒角，磨砂背板，暖灰色调",
  "category": "phone"
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "paradigm": "亲和精致",
    "wt_estimate": 0.22,
    "polarity_analysis": {
      "positive_elements": ["圆润造型", "磨砂背板", "暖灰色调"],
      "threat_elements": ["钛金属中框", "精密倒角"]
    },
    "scores_estimate": {
      "tension": 21,
      "order": 23,
      "threshold": 22,
      "context": 21
    },
    "total_estimate": 87
  }
}
```

### 2.2 图片分析

上传图片进行 BEA 分析（需配合图像识别服务）。

**请求**：
```
POST /analyze/image
Content-Type: multipart/form-data
```

**参数**：
- `image`：图片文件（JPG/PNG，最大 10MB）
- `category`：品类（可选，自动识别）
- `description`：补充描述（可选）

**响应**：
```json
{
  "code": 0,
  "data": {
    "paradigm": "崇高震撼",
    "wt": 0.57,
    "dimension_analysis": [
      {"dimension": "形状线条", "polarity": "T", "intensity": 7},
      {"dimension": "色彩", "polarity": "T", "intensity": 6},
      {"dimension": "质感", "polarity": "P", "intensity": 4}
    ],
    "scores": {
      "tension": 23,
      "order": 23,
      "threshold": 22,
      "context": 23
    },
    "total": 91,
    "diagnosis": {
      "strengths": ["精密金属质感", "锐利几何线条", "微差补偿结构"],
      "weaknesses": [],
      "suggestions": []
    }
  }
}
```

### 2.3 对比分析

对比两个方案的 BEA 特征差异。

**请求**：
```
POST /analyze/compare
```

**请求体**：
```json
{
  "a": {"name": "方案A", "wt": 0.22, "scores": {"tension": 22, "order": 24, "threshold": 23, "context": 22}},
  "b": {"name": "方案B", "wt": 0.35, "scores": {"tension": 24, "order": 21, "threshold": 20, "context": 21}}
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "winner": "a",
    "winner_reason": "方案A总分更高（91 vs 86），秩序和阈值维度明显优于方案B",
    "comparison": {
      "wt_diff": -0.13,
      "score_diff": 5,
      "dimension_diffs": {
        "tension": -2,
        "order": 3,
        "threshold": 3,
        "context": 1
      }
    },
    "recommendation": "方案A更适合长期贴身产品；方案B更适合短时远观的冲击型产品"
  }
}
```

---

## 3. 诊断接口

### 3.1 病症诊断

根据 BEA 特征诊断审美病症并给出处方。

**请求**：
```
POST /diagnose
```

**请求体**：
```json
{
  "wt": 0.08,
  "scores": {"tension": 12, "order": 22, "threshold": 24, "context": 20},
  "symptoms": ["全圆角", "全柔色", "无锐度", "发腻"]
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "primary_disease": "甜腻症（亲极过载）",
    "disease_category": "单一极性病症",
    "quadrant": "呆板平庸区",
    "root_cause": "纯亲极无对立，倒U左侧单调区，缺乏张力提神",
    "prescriptions": [
      {
        "priority": 1,
        "dimension": "形状线条",
        "action": "在高价值细节注入10%-20%危极",
        "target": "T=4-6",
        "method": "利落线/冷灰/清晰边界，柔中藏骨"
      },
      {
        "priority": 2,
        "dimension": "色彩",
        "action": "增加一个冷峻对比色",
        "target": "对比强度T=5",
        "method": "小面积高饱和冷色点缀"
      }
    ],
    "expected_movement": "从呆板平庸区移向高张力×高秩序黄金区",
    "expected_wt": 0.18,
    "expected_score_improvement": 15
  }
}
```

---

## 4. 设计接口

### 4.1 范式推荐

根据受众、场景、功能推荐合适的范式。

**请求**：
```
POST /design/recommend-paradigm
```

**请求体**：
```json
{
  "audience": "大众",
  "scenario": "长期贴身",
  "function_risk": "低",
  "emotion_goal": "好感精致",
  "category": "phone"
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "recommended_paradigm": "亲和精致",
    "wt_target": 0.20,
    "wt_range": [0.18, 0.22],
    "ratio": "80:20",
    "rationale": "大众受众阈值偏左，长期贴身需耐看，低功能风险可适度张力，好感精致目标对应亲和精致范式",
    "key_principles": [
      "大面积亲极托底保证安全愉悦",
      "20%危极集中在用户凑近看/反复触摸处",
      "微差补偿结构：宏观柔和+微观锐利"
    ],
    "alternatives": [
      {"paradigm": "治愈松弛", "wt": 0.10, "reason": "更温和但可能缺乏记忆点"},
      {"paradigm": "均衡典雅", "wt": 0.40, "reason": "更有个性但对大众可能偏锐"}
    ]
  }
}
```

### 4.2 生成基调卡

生成 BEA 设计基调卡。

**请求**：
```
POST /design/generate-brief
```

**请求体**：
```json
{
  "project": "新一代智能手表",
  "category": "wearable",
  "target_audience": "25-35岁都市白领",
  "usage_scenario": "日常佩戴+运动",
  "emotion_goal": "科技感+亲和",
  "brand_personality": "专业+温暖"
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "brief": {
      "project": "新一代智能手表",
      "paradigm": "亲和精致",
      "wt_target": 0.22,
      "wt_range": [0.20, 0.25],
      "primary_polarity": "亲极P+",
      "secondary_polarity": "危极T−",
      "ratio": "78:22",
      "order_principle": "圆形表盘+对称布局+统一圆角模数",
      "hierarchy_strategy": "微差补偿（宏观圆润+微观精密）",
      "emotion_positioning": "科技感中带温度，专业但不冰冷"
    },
    "design_directions": [
      {"dimension": "形状", "direction": "圆形表盘，圆润表耳，精密表圈倒角"},
      {"dimension": "材质", "direction": "磨砂铝合金表壳，亲肤硅胶表带，蓝宝石玻璃"},
      {"dimension": "色彩", "direction": "低饱和深空灰为主，暖橙点缀"},
      {"dimension": "界面", "direction": "圆角卡片，缓动效果，清晰层级"}
    ]
  }
}
```

---

## 5. 数据接口

### 5.1 获取案例库

获取 BEA 案例库数据。

**请求**：
```
GET /data/cases?category=phone&paradigm=affinity&min_score=85&limit=10&offset=0
```

**查询参数**：
- `category`：品类筛选（可选）
- `paradigm`：范式筛选（可选）
- `min_score`：最低评分（可选）
- `limit`：返回数量（默认10，最大50）
- `offset`：偏移量（默认0）

**响应**：
```json
{
  "code": 0,
  "data": {
    "total": 17,
    "filtered": 3,
    "cases": [
      {
        "id": "01",
        "name": "iPhone 17 Pro",
        "category": "消费电子",
        "paradigm": "亲和精致",
        "wt": 0.22,
        "score": 91,
        "summary": "亲和精致范式典范..."
      }
    ]
  }
}
```

### 5.2 获取范式定义

获取所有范式的详细定义。

**请求**：
```
GET /data/paradigms
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "paradigms": [
      {
        "id": "healing",
        "name": "治愈松弛",
        "wt": 0.10,
        "wt_range": [0, 0.15],
        "ratio": "90:10",
        "emotion": "放松、舒展、无攻击性",
        "core": "柔中藏骨...",
        "typical": ["母婴", "疗愈空间"]
      }
    ]
  }
}
```

### 5.3 获取元素双极谱系

获取视觉/听觉/触觉等元素的双极谱系表。

**请求**：
```
GET /data/polarity-spectrum?modality=visual
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "modality": "visual",
    "dimensions": [
      {
        "dimension": "形状线条",
        "positive": ["曲线", "圆角", "闭合形", "对称"],
        "threat": ["锐角", "折线", "锯齿", "破碎开放"]
      }
    ]
  }
}
```

---

## 6. 错误码

| 错误码 | 含义 | 说明 |
|---|---|---|
| 0 | 成功 | 请求成功 |
| 40001 | 参数错误 | 请求参数缺失或格式错误 |
| 40002 | 维度权重错误 | 维度权重之和不为1 |
| 40003 | 强度超出范围 | 极性强度不在0-10范围内 |
| 40101 | 认证失败 | API Key 无效或过期 |
| 40301 | 权限不足 | 接口需要更高权限 |
| 42901 | 速率限制 | 请求过于频繁 |
| 50001 | 服务器错误 | 内部服务器错误 |
| 50002 | 服务不可用 | 服务暂时不可用 |

**错误响应格式**：
```json
{
  "code": 40001,
  "message": "参数错误：dimensions 不能为空",
  "details": {
    "field": "dimensions",
    "reason": "数组不能为空"
  }
}
```

---

## 7. SDK 与集成

### 7.1 JavaScript SDK

```javascript
import BEA from '@bea/sdk';

const bea = new BEA({ apiKey: 'your-api-key' });

// 计算 W(T)
const result = await bea.calculate.wt({
  category: 'phone',
  dimensions: [
    { name: '形状线条', t: 2, weight: 0.25 },
    { name: '质感触觉', t: 3, weight: 0.25 }
  ]
});

console.log(result.wt, result.paradigm.name);
```

### 7.2 Python SDK

```python
from bea import BEAClient

bea = BEAClient(api_key='your-api-key')

# 诊断
result = bea.diagnose(
    wt=0.08,
    scores={'tension': 12, 'order': 22, 'threshold': 24, 'context': 20},
    symptoms=['全圆角', '全柔色']
)

print(result.primary_disease)
for prescription in result.prescriptions:
    print(prescription.action)
```

### 7.3 cURL 示例

```bash
curl -X POST https://api.bea-aesthetics.com/v1/calculate/wt \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "phone",
    "dimensions": [
      {"name": "形状线条", "t": 2, "weight": 0.25},
      {"name": "质感触觉", "t": 3, "weight": 0.25}
    ]
  }'
```

---

## 8. 常见问题

### Q: API 免费吗？
A: 基础版免费（100次/分钟），专业版提供更高配额和高级功能。

### Q: 支持哪些编程语言？
A: 官方提供 JavaScript 和 Python SDK，其他语言可通过 REST API 直接调用。

### Q: 数据会被存储吗？
A: 分析数据默认不存储，如需保存可使用数据持久化接口。

### Q: 如何获取 API Key？
A: 访问 [BEA 开发者平台](https://bea-aesthetics.com/developer) 注册并创建应用。

### Q: 支持私有化部署吗？
A: 企业版支持私有化部署，联系商务获取详情。

---

## 附录

### A. 品类权重表

| 品类 | 维度权重 |
|---|---|
| phone | 形状0.25, 质感0.25, 色彩0.15, 构图0.15, 光影0.10, 细节0.10 |
| car | 形体0.30, 特征线0.25, 灯组0.15, 比例0.15, 材质0.15 |
| brand | 图形0.25, 色彩0.25, 字体0.20, 版式0.20, 质感0.10 |
| ui | 布局0.25, 色彩0.20, 组件0.20, 动效0.20, 字体0.15 |

### B. 范式 W(T) 对照表

| 范式 | W(T) | 区间 |
|---|---|---|
| 治愈松弛 | 0.10 | 0-0.15 |
| 亲和精致 | 0.20 | 0.15-0.30 |
| 诗意朦胧 | 0.35 | 0.30-0.40 |
| 均衡典雅 | 0.40 | 0.40-0.48 |
| 崇高震撼 | 0.55 | 0.48-0.60 |
| 冷峻克制 | 0.62 | 0.60-0.64 |
| 神秘魅惑 | 0.66 | 0.64-0.68 |
| 先锋反叛 | 0.70 | 0.68-0.85 |

---

*BEA API 规范 v1.13.0 · 理论作者：星空本空 · CC BY 4.0*
