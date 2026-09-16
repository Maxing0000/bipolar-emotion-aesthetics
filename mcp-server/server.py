#!/usr/bin/env python3
# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

"""
BEA MCP Server v（版本号动态读引擎）
纯 Python 标准库实现的 MCP stdio 服务器，零第三方依赖，离线可用。

通过 MCP 协议（JSON-RPC 2.0 over stdio）向任意 AI 客户端暴露三个工具：
  bea_analyze       单对象分析：返回 W(T)、六范式定位、四维评分卡、病症诊断
  bea_compare       A/B 对比：返回两方分析、逐维度差值、引擎对比报告
  bea_dimensions    查询品类维度/权重定义与六范式锚点

客户端配置示例（WorkBuddy / Claude Desktop 等通用）：
  "mcpServers": {
    "bea": {
      "command": "python3",
      "args": ["/绝对路径/BEA/mcp-server/server.py"]
    }
  }

自测：python3 mcp-server/test_server.py
"""

import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


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

T_SCALE_DESC = (
    "t=0 纯亲极（圆润/柔色/对称/舒缓），"
    "t=10 纯危极（尖锐/强对比/失衡/冷峻），整数 0-10"
)

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
        # 引擎的 parse_t_values 会校验维度名与取值范围
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


TOOLS = [
    {
        "name": "bea_analyze",
        "description": (
            "BEA 双极情绪美学单对象分析。对产品/品牌/UI/建筑做 t 值打分后，"
            "返回精确的 W(T) 危极权重、六范式定位、病症诊断与调分建议。"
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
]

_TOOL_FUNCS = {
    "bea_analyze": tool_analyze,
    "bea_compare": tool_compare,
    "bea_dimensions": tool_dimensions,
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
                "version": getattr(_bq, "__version__", "2.14.0"),
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
        except Exception as exc:  # 工具级错误按 MCP 规范放进 result.isError
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
