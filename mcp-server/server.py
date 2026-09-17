#!/usr/bin/env python3
# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

"""
BEA MCP Server v2.8.0
纯 Python 标准库实现的 MCP stdio 服务器，零第三方依赖，离线可用。

通过 MCP 协议（JSON-RPC 2.0 over stdio）向任意 AI 客户端暴露 BEA 工具：
  bea_analyze       单对象分析：W(T)、范式、评分、病症、建议
  bea_compare       A/B 对比：两方分析、逐维度差值、对比报告
  bea_dimensions    查询品类维度/权重定义与六范式锚点
  bea_diagnose      诊断审美病症（7种病症，按优先级排序）
  bea_suggest       调整建议：给定目标范式/W(T)，输出维度变更方案
  bea_generate      美感生成：给定目标，自动生成最优维度配置
  bea_sensitivity   灵敏度分析：找出改动哪个维度效果最明显
  bea_paradigms     查询六范式定义、区间、核心体验
  bea_diseases      查询7种审美病症诊断表（识别特征+处方）
  bea_health        健康检查：服务器状态、引擎版本、配置信息
  bea_multigroup    多组/跨模态分析（外形+内饰+声音等）
  bea_style_cycle   风格周期律分析：判断当前风格位置和趋势

客户端配置示例（WorkBuddy / Claude Desktop / Cursor 等通用）：
  "mcpServers": {
    "bea": {
      "command": "python3",
      "args": ["/绝对路径/BEA/mcp-server/server.py"]
    }
  }

一键安装：python3 mcp-server/install.py
自测：python3 mcp-server/test_server.py
"""

import importlib.util
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_START_TIME = time.time()


def _engine_path() -> str:
    """定位引擎：环境变量 → 仓库结构（../scripts/）→ 同目录（pip 安装布局）。"""
    env = os.environ.get("BEA_ENGINE")
    if env and os.path.exists(env):
        return env
    repo_layout = os.path.join(_HERE, "..", "scripts", "bea_quant.py")
    if os.path.exists(repo_layout):
        return repo_layout
    return os.path.join(_HERE, "bea_quant.py")


_ENGINE = _engine_path()

_spec = importlib.util.spec_from_file_location("bea_quant", _ENGINE)
_bq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bq)

SERVER_NAME = "bea"
PROTOCOL_VERSION = "2024-11-05"
SERVER_VERSION = getattr(_bq, "__version__", "2.8.0")

T_SCALE_DESC = (
    "t=0 纯亲极（圆润/柔色/对称/舒缓），"
    "t=10 纯危极（尖锐/强对比/失衡/冷峻），整数 0-10"
)

# 7种审美病症定义
DISEASES_DEFINITION = [
    {
        "name": "本能越界",
        "priority": "一级（一票否决）",
        "identification": "任何维度 t>=10，触及割伤、眩晕、疼痛、刺耳等生理红线",
        "prescription": "立即删除或钝化，无风格借口",
        "mechanism": "越过本能安全阈值，产生真实生理不适"
    },
    {
        "name": "攻击症",
        "priority": "二级（严重）",
        "identification": "W(T)>=0.55 且有 t>=6，令人紧张想回避",
        "prescription": "扩大亲极基底，降危极到范式区间，用大曲面/柔光/对称接住张力",
        "mechanism": "危极过载，逼近或越过认知阈值，产生攻击感"
    },
    {
        "name": "刺激疲劳",
        "priority": "二级（严重）",
        "identification": "W(T)>=0.65 且所有 t>=7，全程高能无喘息",
        "prescription": "时空上安排亲极呼吸段，控制强调点数量（1-2个）",
        "mechanism": "危极持续拉满，无张力-释放节奏，长期观看致疲劳"
    },
    {
        "name": "重点通胀症",
        "priority": "三级（中等）",
        "identification": ">=3个维度 t>=6，视觉噪音大，哪里都想强调结果哪里都不突出",
        "prescription": "做减法，强调点压回1-2个，建立视觉等级",
        "mechanism": "注意力预算超支，处处强调等于无强调"
    },
    {
        "name": "均分症",
        "priority": "三级（中等）",
        "identification": "所有 t 在3-5，W(T) 0.35-0.45，极差<2，亲危各半无主次",
        "prescription": "确立>=6:4主辅比，先让第一印象明确",
        "mechanism": "主辅缺失，情绪暧昧，'说不上哪里怪'"
    },
    {
        "name": "甜腻症",
        "priority": "四级（轻微）",
        "identification": "W(T)<0.25 且所有 t<=4，全圆角无锐度，发腻幼稚廉价",
        "prescription": "高价值细节注入10%-20%危极（利落线/冷灰/清晰边界），柔中藏骨",
        "mechanism": "倒U左侧单调区，亲极过载，缺少张力"
    },
    {
        "name": "张力不足症",
        "priority": "四级（轻微）",
        "identification": "W(T)<0.35 且极差<2，元素都对但无记忆点，一眼到头",
        "prescription": "1-2个维度提升到6+，制造清晰双极对立并用秩序收束",
        "mechanism": "呆板平庸区，张力缺失，缺少唤醒"
    }
]

# ──────────────────────────────────────────────
# 工具实现
# ──────────────────────────────────────────────

def _check_category(category: str) -> None:
    if category not in _bq.CATEGORY_WEIGHTS:
        raise ValueError(
            f"未知品类 '{category}'，可选：{', '.join(_bq.CATEGORY_WEIGHTS)}"
        )


def _build_t_str(t_values, category: str) -> str:
    """把 t_values（dict 或带维度名的字符串）规范化为引擎的 '维度=t' 字符串。"""
    valid_dims = list(_bq.CATEGORY_WEIGHTS[category].keys())
    if isinstance(t_values, dict):
        unknown = [k for k in t_values if k not in valid_dims]
        if unknown:
            raise ValueError(
                f"未知维度 {unknown}，'{category}' 的维度为：{', '.join(valid_dims)}"
            )
        missing = [k for k in valid_dims if k not in t_values]
        if missing:
            raise ValueError(f"缺少维度 {missing}，需提供全部 {valid_dims}")
        return ",".join(f"{k}={t_values[k]}" for k in valid_dims)
    if isinstance(t_values, str):
        return t_values
    raise ValueError("t_values 应为对象（维度名→t值）或 '维度=t,...' 字符串")


def _analysis_payload(a) -> dict:
    payload = a.to_dict()
    payload["report_markdown"] = _bq.format_report_markdown(a)
    return payload


def tool_analyze(args: dict) -> dict:
    category = args.get("category")
    _check_category(category)
    t_str = _build_t_str(args.get("t_values"), category)
    a = _bq.analyze(category, t_str)
    return _analysis_payload(a)


def tool_compare(args: dict) -> dict:
    category = args.get("category")
    _check_category(category)
    name_a, dims_a = _bq.parse_compact_values(args.get("a"), category)
    name_b, dims_b = _bq.parse_compact_values(args.get("b"), category)
    a1 = _bq.analyze(category, _build_t_str(dims_a, category))
    a2 = _bq.analyze(category, _build_t_str(dims_b, category))
    diff = {dim: round(dims_a[dim] - dims_b[dim], 1) for dim in dims_a}
    return {
        "category": category,
        "a": {"name": name_a, **_analysis_payload(a1)},
        "b": {"name": name_b, **_analysis_payload(a2)},
        "dimension_diff_a_minus_b": diff,
        "w_t_diff_a_minus_b": round(a1.w_t - a2.w_t, 3),
        "report_markdown": _bq.format_compare(a1, a2, name_a, name_b),
    }


def tool_dimensions(args: dict) -> dict:
    category = args.get("category")
    if category is not None:
        _check_category(category)
    categories = (
        {category: _bq.CATEGORY_WEIGHTS[category]}
        if category is not None
        else _bq.CATEGORY_WEIGHTS
    )
    return {
        "t_scale": T_SCALE_DESC,
        "categories": {
            cat: {
                "dimensions": [
                    {"name": dim, "weight": w}
                    for dim, w in weights.items()
                ],
            }
            for cat, weights in categories.items()
        },
        "paradigms": [
            {
                "w_t_range": [low, high],
                "name": name,
                "experience": desc,
            }
            for low, high, name, desc in _bq.PARADIGMS
        ],
    }


def tool_diagnose(args: dict) -> dict:
    """诊断审美病症"""
    category = args.get("category")
    _check_category(category)
    t_str = _build_t_str(args.get("t_values"), category)
    a = _bq.analyze(category, t_str)
    diseases = _bq.diagnose_diseases(a.w_t, a.dimensions)
    return {
        "category": category,
        "w_t": a.w_t,
        "paradigm": a.paradigm,
        "diseases": diseases,
        "disease_count": len(diseases),
        "has_disease": len(diseases) > 0,
        "summary": f"诊断出 {len(diseases)} 种病症" if diseases else "✓ 无明显病症",
        "report_markdown": _bq.format_report_markdown(a),
    }


def tool_suggest(args: dict) -> dict:
    """调整建议：给定目标范式/W(T)，输出维度变更方案"""
    category = args.get("category")
    _check_category(category)
    t_str = _build_t_str(args.get("t_values"), category)
    target = args.get("target", "0.30")
    strategy = args.get("strategy", "focused")
    if strategy not in ["focused", "distributed"]:
        raise ValueError(f"未知策略 '{strategy}'，可选：focused, distributed")
    a = _bq.analyze(category, t_str)
    target_wt, target_desc = _bq.resolve_target(target)
    suggestions, summary = _bq.suggest_adjustment(a, target_wt, strategy)
    return {
        "category": category,
        "current_w_t": a.w_t,
        "current_paradigm": a.paradigm,
        "target_w_t": target_wt,
        "target_desc": target_desc,
        "strategy": strategy,
        "suggestions": suggestions,
        "suggestion_count": len(suggestions),
        "summary": summary,
        "report_markdown": _bq.format_suggest(a, target_wt, target_desc, suggestions, summary),
    }


def tool_generate(args: dict) -> dict:
    """美感生成：给定目标，自动生成最优维度配置"""
    category = args.get("category")
    _check_category(category)
    target = args.get("target", "0.30")
    strategy = args.get("strategy", "balanced")
    if strategy not in ["balanced", "focused", "distributed"]:
        raise ValueError(f"未知策略 '{strategy}'，可选：balanced, focused, distributed")
    target_wt, target_desc = _bq.resolve_target(target)
    result = _bq.generate_design(category, target_wt, strategy)
    # 移除无法序列化的 BEAAnalysis 对象
    analysis_obj = result.pop("analysis", None)
    return {
        "category": category,
        "target_w_t": target_wt,
        "target_desc": target_desc,
        "strategy": strategy,
        "generated_dimensions": result.get("dimensions", {}),
        "actual_w_t": result.get("w_t", 0),
        "paradigm": result.get("paradigm", ""),
        "deviation": result.get("deviation", 0),
        "design_notes": result.get("notes", []),
        "t_values_str": result.get("t_str", ",".join(f"{k}={v}" for k, v in result.get("dimensions", {}).items())),
    }


def tool_sensitivity(args: dict) -> dict:
    """灵敏度分析：找出改动哪个维度效果最明显"""
    category = args.get("category")
    _check_category(category)
    t_str = _build_t_str(args.get("t_values"), category)
    target = args.get("target")
    step = args.get("step", 1)
    a = _bq.analyze(category, t_str)
    target_wt = _bq.resolve_target(target)[0] if target else None
    results = _bq.sensitivity_analysis(a, target_wt, step)
    return {
        "category": category,
        "current_w_t": a.w_t,
        "target_w_t": target_wt,
        "step": step,
        "sensitivity_results": results,
        "most_impactful": results[0]["dimension"] if results else None,
        "report_markdown": _bq.format_sensitivity(a, results, target_wt, step),
    }


def tool_paradigms(args: dict) -> dict:
    """查询六范式定义、区间、核心体验"""
    return {
        "paradigms": [
            {
                "w_t_range": [low, high],
                "name": name,
                "experience": desc,
                "typical_applications": _get_paradigm_applications(name),
            }
            for low, high, name, desc in _bq.PARADIGMS
        ],
        "w_t_formula": "W(T) = Σ wᵢ × (tᵢ/10)，Σwᵢ=1，结果 0-1",
        "t_scale": T_SCALE_DESC,
    }


def _get_paradigm_applications(name: str) -> str:
    applications = {
        "治愈松弛": "母婴、疗愈空间、家居、民生服务、医疗空间",
        "亲和精致": "消费电子、高端日用品、主流品牌视觉、多数量产产品",
        "均衡典雅": "经典主义、新中式、奢侈品经典线、商务产品",
        "崇高震撼": "大型公共建筑、豪华/旗舰产品、史诗级视觉、当代装置、豪华汽车",
        "冷峻克制": "极简主义、专业工具、德系工业设计、科技产品",
        "先锋反叛": "潮牌、亚文化、先锋艺术、概念设计、实验影像",
    }
    return applications.get(name, "")


def tool_diseases(args: dict) -> dict:
    """查询7种审美病症诊断表"""
    return {
        "diseases": DISEASES_DEFINITION,
        "disease_count": len(DISEASES_DEFINITION),
        "priority_levels": ["一级（一票否决）", "二级（严重）", "三级（中等）", "四级（轻微）"],
    }


def tool_health(args: dict) -> dict:
    """健康检查：服务器状态、引擎版本、配置信息"""
    uptime = round(time.time() - _START_TIME, 2)
    return {
        "status": "healthy",
        "server_name": SERVER_NAME,
        "server_version": SERVER_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "engine_path": _ENGINE,
        "engine_version": getattr(_bq, "__version__", "unknown"),
        "uptime_seconds": uptime,
        "supported_categories": list(_bq.CATEGORY_WEIGHTS.keys()),
        "supported_tools": [t["name"] for t in TOOLS],
        "tool_count": len(TOOLS),
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
    }


def tool_multigroup(args: dict) -> dict:
    """多组/跨模态分析（外形+内饰+声音等）"""
    category = args.get("category")
    _check_category(category)
    groups_input = args.get("groups", [])
    if not groups_input:
        raise ValueError("groups 不能为空，需提供至少一组分析")
    groups = []
    for g in groups_input:
        name = g.get("name", "未命名")
        t_str = _build_t_str(g.get("t_values"), category)
        dims = _bq.parse_t_values(t_str, list(_bq.CATEGORY_WEIGHTS[category].keys()))
        groups.append({"name": name, "dimensions": dims})
    result = _bq.multigroup_analysis(category, groups)
    return {
        "category": category,
        "group_count": len(groups),
        "groups": result.get("groups", []),
        "cross_modal_consistency": result.get("cross_modal_consistency", {}),
        "hierarchy": result.get("hierarchy", {}),
        "overall_assessment": result.get("overall", {}),
        "report_markdown": _bq.format_multigroup(result),
    }


def tool_style_cycle(args: dict) -> dict:
    """风格周期律分析：判断当前风格位置和趋势"""
    category = args.get("category")
    _check_category(category)
    w_t = args.get("w_t")
    if w_t is None:
        raise ValueError("w_t 不能为空，需提供当前 W(T) 值")
    w_t = float(w_t)
    result = _bq.style_cycle_analysis(category, w_t)
    return {
        "category": category,
        "current_w_t": w_t,
        "cycle_position": result.get("position", ""),
        "trend": result.get("trend", ""),
        "recommendation": result.get("recommendation", ""),
        "report_markdown": _bq.format_style_cycle(result),
    }


TOOLS = [
    {
        "name": "bea_analyze",
        "description": (
            "BEA 双极情绪美学单对象分析。对产品/品牌/UI/建筑做 t 值打分后，"
            "返回精确的 W(T) 危极权重、六范式定位、四维评分、病症诊断与调分建议。"
            "必须先调用 bea_dimensions 获取该品类的维度列表。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["phone", "car", "brand", "ui", "building"],
                    "description": "分析品类",
                },
                "t_values": {
                    "description": (
                        "各维度 t 值（0-10 整数）。"
                        "对象格式 {\"形状\":3,...} 或字符串 \"形状=3,质感=6,...\""
                    ),
                },
            },
            "required": ["category", "t_values"],
        },
    },
    {
        "name": "bea_compare",
        "description": (
            "BEA A/B 对比。输入两个对象（紧凑格式 '名称=3,6,4,3,5,6' 按维度顺序，"
            "或完整格式 '名称=形状=3,质感=6,...'），"
            "返回两方分析、逐维度差值与引擎对比报告。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["phone", "car", "brand", "ui", "building"],
                    "description": "分析品类",
                },
                "a": {"type": "string", "description": "对象 A，'名称=值' 格式"},
                "b": {"type": "string", "description": "对象 B，'名称=值' 格式"},
            },
            "required": ["category", "a", "b"],
        },
    },
    {
        "name": "bea_dimensions",
        "description": (
            "查询 BEA 品类维度定义与权重（打分前必查），"
            "以及 t 值标尺与六范式锚点。不传 category 返回全部 5 个品类。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["phone", "car", "brand", "ui", "building"],
                    "description": "可选，只查一个品类",
                },
            },
        },
    },
    {
        "name": "bea_diagnose",
        "description": (
            "BEA 审美病症诊断。输入品类 + t 值，返回 7 种病症的诊断结果，"
            "按优先级排序（一级一票否决 → 四级轻微），包含识别特征和处方。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["phone", "car", "brand", "ui", "building"],
                    "description": "分析品类",
                },
                "t_values": {
                    "description": "各维度 t 值，对象或字符串格式",
                },
            },
            "required": ["category", "t_values"],
        },
    },
    {
        "name": "bea_suggest",
        "description": (
            "BEA 调整建议。给定当前 t 值和目标范式/W(T)，输出具体的维度变更方案，"
            "包含原值→目标值、具体做法、预期效果。支持 focused（集中改动）和 distributed（分散改动）两种策略。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["phone", "car", "brand", "ui", "building"],
                    "description": "分析品类",
                },
                "t_values": {
                    "description": "当前各维度 t 值",
                },
                "target": {
                    "type": "string",
                    "description": "目标 W(T) 值（如 '0.30'）或范式名（如 '亲和精致'）",
                    "default": "0.30",
                },
                "strategy": {
                    "type": "string",
                    "enum": ["focused", "distributed"],
                    "description": "调整策略：focused 集中改动少数维度，distributed 分散改动多个维度",
                    "default": "focused",
                },
            },
            "required": ["category", "t_values"],
        },
    },
    {
        "name": "bea_generate",
        "description": (
            "BEA 美感生成。给定目标范式/W(T)，自动生成最优维度配置。"
            "支持 balanced（均衡）、focused（集中）、distributed（分散）三种生成策略。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["phone", "car", "brand", "ui", "building"],
                    "description": "生成品类",
                },
                "target": {
                    "type": "string",
                    "description": "目标 W(T) 值或范式名",
                    "default": "0.30",
                },
                "strategy": {
                    "type": "string",
                    "enum": ["balanced", "focused", "distributed"],
                    "description": "生成策略",
                    "default": "balanced",
                },
            },
            "required": ["category"],
        },
    },
    {
        "name": "bea_sensitivity",
        "description": (
            "BEA 灵敏度分析。找出改动哪个维度对 W(T) 影响最大，"
            "帮助用户用最少的改动达到目标效果。可指定目标 W(T) 和改动步长。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["phone", "car", "brand", "ui", "building"],
                    "description": "分析品类",
                },
                "t_values": {
                    "description": "当前各维度 t 值",
                },
                "target": {
                    "type": "string",
                    "description": "可选，目标 W(T) 值，用于计算达到目标所需的改动量",
                },
                "step": {
                    "type": "integer",
                    "description": "改动步长（1-3）",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 3,
                },
            },
            "required": ["category", "t_values"],
        },
    },
    {
        "name": "bea_paradigms",
        "description": (
            "查询 BEA 六范式定义、W(T) 区间、核心体验和典型应用场景。"
            "用于范式选择和风格定位参考。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "bea_diseases",
        "description": (
            "查询 BEA 7 种审美病症诊断表，包含病症名称、优先级、识别特征、"
            "发病机理和处方。用于诊断参考和设计自查。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "bea_health",
        "description": (
            "BEA MCP 服务器健康检查。返回服务器状态、版本号、引擎路径、"
            "支持的品类和工具列表、运行时间等信息。用于调试和验证连接。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "bea_multigroup",
        "description": (
            "BEA 多组/跨模态分析。同时分析多个组（如外形+内饰+声音+界面），"
            "返回各组分析结果和整体一致性评估。用于跨模态设计审查。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["phone", "car", "brand", "ui", "building"],
                    "description": "分析品类",
                },
                "groups": {
                    "type": "array",
                    "description": "分析组列表，每组包含 name 和 t_values",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "组名称，如 '外形'、'内饰'"},
                            "t_values": {"description": "该组各维度 t 值"},
                        },
                        "required": ["name", "t_values"],
                    },
                },
            },
            "required": ["category", "groups"],
        },
    },
    {
        "name": "bea_style_cycle",
        "description": (
            "BEA 风格周期律分析。根据当前 W(T) 值判断在风格周期中的位置，"
            "预测趋势并给出设计建议。用于品牌风格迭代和潮流判断。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["phone", "car", "brand", "ui", "building"],
                    "description": "分析品类",
                },
                "w_t": {
                    "type": "number",
                    "description": "当前 W(T) 值（0-1）",
                },
            },
            "required": ["category", "w_t"],
        },
    },
]

_TOOL_FUNCS = {
    "bea_analyze": tool_analyze,
    "bea_compare": tool_compare,
    "bea_dimensions": tool_dimensions,
    "bea_diagnose": tool_diagnose,
    "bea_suggest": tool_suggest,
    "bea_generate": tool_generate,
    "bea_sensitivity": tool_sensitivity,
    "bea_paradigms": tool_paradigms,
    "bea_diseases": tool_diseases,
    "bea_health": tool_health,
    "bea_multigroup": tool_multigroup,
    "bea_style_cycle": tool_style_cycle,
}


# ──────────────────────────────────────────────
# JSON-RPC 2.0 调度
# ──────────────────────────────────────────────

def _resp(rid, result):
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def _err(rid, code, message):
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


def handle_request(req: dict):
    """处理一条 JSON-RPC 请求；通知（无 id）返回 None。"""
    method = req.get("method", "")
    rid = req.get("id")

    if method == "initialize":
        requested = req.get("params", {}).get("protocolVersion", PROTOCOL_VERSION)
        return _resp(rid, {
            "protocolVersion": requested,
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": SERVER_NAME,
                "version": SERVER_VERSION,
            },
        })

    if method == "ping":
        return _resp(rid, {})

    if method == "tools/list":
        return _resp(rid, {"tools": TOOLS})

    if method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        args = params.get("arguments") or {}
        func = _TOOL_FUNCS.get(name)
        if func is None:
            return _resp(rid, {
                "content": [{"type": "text", "text": f"未知工具 '{name}'"}],
                "isError": True,
            })
        try:
            result = func(args)
        except Exception as exc:
            return _resp(rid, {
                "content": [{"type": "text", "text": f"BEA 错误：{exc}"}],
                "isError": True,
            })
        return _resp(rid, {
            "content": [{
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False, indent=2),
            }],
        })

    if method.startswith("notifications/"):
        return None

    if rid is None:
        return None
    return _err(rid, -32601, f"未知方法 '{method}'")


def serve() -> int:
    """stdio 主循环：逐行读 JSON-RPC，逐行写响应。"""
    out = sys.stdout
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except ValueError:
                resp = _err(None, -32700, "解析错误：不是合法 JSON")
            else:
                resp = handle_request(req)
            if resp is not None:
                out.write(json.dumps(resp, ensure_ascii=False) + "\n")
                out.flush()
    except BrokenPipeError:
        pass
    return 0


def main() -> int:
    """pip 安装后的 console_script 入口（bea-mcp 命令）。"""
    return serve()


if __name__ == "__main__":
    sys.exit(serve())