#!/usr/bin/env python3
# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

"""
BEA MCP Server 自测脚本

起真实子进程走完整 MCP 会话（握手 → 工具列表 → 工具调用 → 错误路径），
并与引擎直算结果比对。

用法：
  python3 test_server.py
  python3 test_server.py -v    # 详细输出
"""

import json
import os
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_SERVER = os.path.join(_HERE, "server.py")
_ENGINE = os.path.join(_HERE, "..", "scripts", "bea_quant.py")

PASS = 0
FAIL = 0
VERBOSE = "-v" in sys.argv


def ok(msg: str):
    global PASS
    PASS += 1
    print(f"  ok: {msg}")


def fail(msg: str):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {msg}")


def assert_eq(actual, expected, msg: str):
    if actual == expected:
        ok(msg)
    else:
        fail(f"{msg}（期望 {expected!r}，实际 {actual!r}）")


def assert_gt(actual, threshold, msg: str):
    if actual > threshold:
        ok(msg)
    else:
        fail(f"{msg}（期望 > {threshold}，实际 {actual!r}）")


def assert_in(item, container, msg: str):
    if item in container:
        ok(msg)
    else:
        fail(f"{msg}（{item!r} 不在 {container!r} 中）")


class MCPClient:
    """简易 MCP stdio 客户端"""

    def __init__(self):
        self.proc = subprocess.Popen(
            [sys.executable, _SERVER],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._id = 0

    def _next_id(self):
        self._id += 1
        return self._id

    def send(self, method: str, params: dict = None) -> dict:
        rid = self._next_id()
        req = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            req["params"] = params
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()

        # 读响应
        for _ in range(100):
            line = self.proc.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            resp = json.loads(line)
            if resp.get("id") == rid:
                return resp
        raise TimeoutError(f"等待响应超时：{method}")

    def initialize(self) -> dict:
        return self.send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        })

    def ping(self) -> dict:
        return self.send("ping")

    def list_tools(self) -> dict:
        return self.send("tools/list")

    def call_tool(self, name: str, args: dict) -> dict:
        return self.send("tools/call", {"name": name, "arguments": args})

    def send_notification(self, method: str):
        req = {"jsonrpc": "2.0", "method": method}
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


def test_handshake():
    print("\n=== 握手与基础协议 ===")
    client = MCPClient()

    resp = client.initialize()
    result = resp.get("result", {})
    assert_eq(result.get("protocolVersion"), "2024-11-05", "initialize：协议版本一致")
    assert_eq(result.get("serverInfo", {}).get("name"), "bea", "initialize：serverInfo.name")
    assert_in("tools", result.get("capabilities", {}), "initialize：声明 tools 能力")
    assert_eq(result.get("serverInfo", {}).get("version"), "2.8.0", "initialize：版本与引擎一致（2.8.0）")

    # 通知不产生响应
    client.send_notification("notifications/initialized")
    time.sleep(0.2)

    # ping
    resp = client.ping()
    assert_eq(resp.get("result"), {}, "通知不产生响应，ping 正常返回")

    client.close()


def test_tools_list():
    print("\n=== 工具列表 ===")
    client = MCPClient()
    client.initialize()

    resp = client.list_tools()
    tools = resp.get("result", {}).get("tools", [])

    assert_gt(len(tools), 10, f"tools/list：工具数量（{len(tools)}个）")

    expected_tools = [
        "bea_analyze", "bea_compare", "bea_dimensions",
        "bea_diagnose", "bea_suggest", "bea_generate",
        "bea_sensitivity", "bea_paradigms", "bea_diseases",
        "bea_health", "bea_multigroup", "bea_style_cycle",
    ]
    tool_names = [t["name"] for t in tools]
    for name in expected_tools:
        assert_in(name, tool_names, f"tools/list：包含 {name}")

    # 检查每个工具都有 inputSchema
    for tool in tools:
        assert_in("inputSchema", tool, f"tools/list：{tool['name']} 带 inputSchema")

    client.close()


def test_analyze():
    print("\n=== bea_analyze ===")
    client = MCPClient()
    client.initialize()

    # 字符串入参
    resp = client.call_tool("bea_analyze", {
        "category": "car",
        "t_values": "曲面=4,特征线=6,灯组=5,比例=3,材质=4",
    })
    result_text = resp["result"]["content"][0]["text"]
    result = json.loads(result_text)

    assert_eq(round(result["w_t"], 2), 0.45, "bea_analyze：W(T)=0.45 与引擎一致")
    assert_eq(result["paradigm"], "均衡典雅", "bea_analyze：范式=均衡典雅")
    assert_in("report_markdown", result, "bea_analyze：附 markdown 报告")
    assert_in("dimensions", result, "bea_analyze：包含维度详情")
    assert_in("score_suggestion", result, "bea_analyze：包含四维评分")
    assert_in("diseases", result, "bea_analyze：包含病症诊断")

    # dict 入参
    resp = client.call_tool("bea_analyze", {
        "category": "car",
        "t_values": {"曲面": 4, "特征线": 6, "灯组": 5, "比例": 3, "材质": 4},
    })
    result2 = json.loads(resp["result"]["content"][0]["text"])
    assert_eq(round(result2["w_t"], 2), 0.45, "bea_analyze：dict 入参与字符串入参等价")

    client.close()


def test_compare():
    print("\n=== bea_compare ===")
    client = MCPClient()
    client.initialize()

    resp = client.call_tool("bea_compare", {
        "category": "car",
        "a": "方案A=4,6,5,3,4",
        "b": "方案B=曲面=7,特征线=6,灯组=5,比例=4,材质=4",
    })
    result = json.loads(resp["result"]["content"][0]["text"])

    assert_eq(result["a"]["name"], "方案A", "bea_compare：A 名称解析正确")
    assert_eq(result["b"]["name"], "方案B", "bea_compare：B 名称解析正确")
    assert_in("dimension_diff_a_minus_b", result, "bea_compare：逐维度差值齐全")
    assert_in("w_t_diff_a_minus_b", result, "bea_compare：W(T) 差值")
    assert_in("report_markdown", result, "bea_compare：附对比报告")

    client.close()


def test_dimensions():
    print("\n=== bea_dimensions ===")
    client = MCPClient()
    client.initialize()

    # 全部品类
    resp = client.call_tool("bea_dimensions", {})
    result = json.loads(resp["result"]["content"][0]["text"])
    assert_eq(len(result["categories"]), 5, "bea_dimensions：返回全部 5 个品类")
    assert_eq(len(result["paradigms"]), 7, "bea_dimensions：七范式锚点齐全（含逼近越阈）")
    assert_in("t_scale", result, "bea_dimensions：包含 t 值标尺")

    # 单品类
    resp = client.call_tool("bea_dimensions", {"category": "phone"})
    result = json.loads(resp["result"]["content"][0]["text"])
    assert_eq(len(result["categories"]), 1, "bea_dimensions：单品类过滤")
    assert_in("phone", result["categories"], "bea_dimensions：单品类为 phone")

    client.close()


def test_diagnose():
    print("\n=== bea_diagnose ===")
    client = MCPClient()
    client.initialize()

    # 有病症的案例
    resp = client.call_tool("bea_diagnose", {
        "category": "phone",
        "t_values": "形状=1,质感=1,色彩=1,构图=1,光影=1,细节=1",
    })
    result = json.loads(resp["result"]["content"][0]["text"])
    assert_eq(result["has_disease"], True, "bea_diagnose：甜腻症检测（全1）")
    assert_gt(result["disease_count"], 0, "bea_diagnose：病症数量 > 0")
    assert_in("diseases", result, "bea_diagnose：包含病症列表")

    # 健康案例
    resp = client.call_tool("bea_diagnose", {
        "category": "phone",
        "t_values": "形状=3,质感=4,色彩=3,构图=3,光影=3,细节=5",
    })
    result = json.loads(resp["result"]["content"][0]["text"])
    assert_in("summary", result, "bea_diagnose：包含摘要")

    client.close()


def test_suggest():
    print("\n=== bea_suggest ===")
    client = MCPClient()
    client.initialize()

    resp = client.call_tool("bea_suggest", {
        "category": "car",
        "t_values": "曲面=4,特征线=6,灯组=5,比例=3,材质=4",
        "target": "0.30",
        "strategy": "focused",
    })
    result = json.loads(resp["result"]["content"][0]["text"])

    assert_eq(result["current_w_t"], 0.45, "bea_suggest：当前 W(T) 正确")
    assert_eq(result["target_w_t"], 0.30, "bea_suggest：目标 W(T) 正确")
    assert_eq(result["strategy"], "focused", "bea_suggest：策略正确")
    assert_gt(result["suggestion_count"], 0, "bea_suggest：建议数量 > 0")
    assert_in("report_markdown", result, "bea_suggest：附建议报告")

    client.close()


def test_generate():
    print("\n=== bea_generate ===")
    client = MCPClient()
    client.initialize()

    resp = client.call_tool("bea_generate", {
        "category": "phone",
        "target": "0.30",
        "strategy": "balanced",
    })
    result = json.loads(resp["result"]["content"][0]["text"])

    assert_eq(result["category"], "phone", "bea_generate：品类正确")
    assert_eq(result["target_w_t"], 0.30, "bea_generate：目标 W(T) 正确")
    assert_eq(result["strategy"], "balanced", "bea_generate：策略正确")
    assert_in("generated_dimensions", result, "bea_generate：包含生成的维度")
    assert_in("actual_w_t", result, "bea_generate：包含实际 W(T)")
    assert_in("t_values_str", result, "bea_generate：包含 t 值字符串")

    client.close()


def test_sensitivity():
    print("\n=== bea_sensitivity ===")
    client = MCPClient()
    client.initialize()

    resp = client.call_tool("bea_sensitivity", {
        "category": "car",
        "t_values": "曲面=4,特征线=6,灯组=5,比例=3,材质=4",
        "target": "0.30",
        "step": 1,
    })
    result = json.loads(resp["result"]["content"][0]["text"])

    assert_eq(result["current_w_t"], 0.45, "bea_sensitivity：当前 W(T) 正确")
    assert_eq(result["target_w_t"], 0.30, "bea_sensitivity：目标 W(T) 正确")
    assert_in("sensitivity_results", result, "bea_sensitivity：包含灵敏度结果")
    assert_in("most_impactful", result, "bea_sensitivity：包含最有影响力的维度")
    assert_in("report_markdown", result, "bea_sensitivity：附灵敏度报告")

    client.close()


def test_paradigms():
    print("\n=== bea_paradigms ===")
    client = MCPClient()
    client.initialize()

    resp = client.call_tool("bea_paradigms", {})
    result = json.loads(resp["result"]["content"][0]["text"])

    assert_eq(len(result["paradigms"]), 7, "bea_paradigms：七范式齐全（含逼近越阈）")
    assert_in("w_t_formula", result, "bea_paradigms：包含 W(T) 公式")
    assert_in("t_scale", result, "bea_paradigms：包含 t 值标尺")

    for p in result["paradigms"]:
        assert_in("name", p, f"bea_paradigms：{p.get('name', '?')} 有名称")
        assert_in("w_t_range", p, f"bea_paradigms：{p.get('name', '?')} 有区间")
        assert_in("experience", p, f"bea_paradigms：{p.get('name', '?')} 有体验描述")
        assert_in("typical_applications", p, f"bea_paradigms：{p.get('name', '?')} 有应用场景")

    client.close()


def test_diseases():
    print("\n=== bea_diseases ===")
    client = MCPClient()
    client.initialize()

    resp = client.call_tool("bea_diseases", {})
    result = json.loads(resp["result"]["content"][0]["text"])

    assert_eq(result["disease_count"], 7, "bea_diseases：7种病症齐全")
    assert_eq(len(result["diseases"]), 7, "bea_diseases：病症列表长度正确")
    assert_in("priority_levels", result, "bea_diseases：包含优先级级别")

    for d in result["diseases"]:
        assert_in("name", d, f"bea_diseases：{d.get('name', '?')} 有名称")
        assert_in("priority", d, f"bea_diseases：{d.get('name', '?')} 有优先级")
        assert_in("identification", d, f"bea_diseases：{d.get('name', '?')} 有识别特征")
        assert_in("prescription", d, f"bea_diseases：{d.get('name', '?')} 有处方")

    client.close()


def test_health():
    print("\n=== bea_health ===")
    client = MCPClient()
    client.initialize()

    resp = client.call_tool("bea_health", {})
    result = json.loads(resp["result"]["content"][0]["text"])

    assert_eq(result["status"], "healthy", "bea_health：状态健康")
    assert_eq(result["server_name"], "bea", "bea_health：服务器名称正确")
    assert_eq(result["server_version"], "2.8.0", "bea_health：版本号正确")
    assert_in("engine_path", result, "bea_health：包含引擎路径")
    assert_in("engine_version", result, "bea_health：包含引擎版本")
    assert_in("supported_categories", result, "bea_health：包含支持的品类")
    assert_in("supported_tools", result, "bea_health：包含支持的工具")
    assert_gt(result["tool_count"], 10, f"bea_health：工具数量（{result['tool_count']}个）")
    assert_in("python_version", result, "bea_health：包含 Python 版本")
    assert_in("platform", result, "bea_health：包含平台信息")

    client.close()


def test_multigroup():
    print("\n=== bea_multigroup ===")
    client = MCPClient()
    client.initialize()

    resp = client.call_tool("bea_multigroup", {
        "category": "car",
        "groups": [
            {"name": "外形", "t_values": "曲面=4,特征线=6,灯组=5,比例=3,材质=4"},
            {"name": "内饰", "t_values": "曲面=3,特征线=3,灯组=3,比例=4,材质=3"},
        ],
    })
    result = json.loads(resp["result"]["content"][0]["text"])

    assert_eq(result["category"], "car", "bea_multigroup：品类正确")
    assert_eq(result["group_count"], 2, "bea_multigroup：组数正确")
    assert_in("groups", result, "bea_multigroup：包含各组分析")
    assert_in("overall_assessment", result, "bea_multigroup：包含整体评估")
    assert_in("report_markdown", result, "bea_multigroup：附报告")

    client.close()


def test_style_cycle():
    print("\n=== bea_style_cycle ===")
    client = MCPClient()
    client.initialize()

    resp = client.call_tool("bea_style_cycle", {
        "category": "car",
        "w_t": 0.45,
    })
    result = json.loads(resp["result"]["content"][0]["text"])

    assert_eq(result["category"], "car", "bea_style_cycle：品类正确")
    assert_eq(result["current_w_t"], 0.45, "bea_style_cycle：当前 W(T) 正确")
    assert_in("cycle_position", result, "bea_style_cycle：包含周期位置")
    assert_in("trend", result, "bea_style_cycle：包含趋势")
    assert_in("recommendation", result, "bea_style_cycle：包含建议")
    assert_in("report_markdown", result, "bea_style_cycle：附报告")

    client.close()


def test_error_paths():
    print("\n=== 错误路径 ===")
    client = MCPClient()
    client.initialize()

    # 未知工具
    resp = client.call_tool("bea_unknown", {})
    assert_eq(resp["result"].get("isError"), True, "未知工具 → isError")

    # 非法品类
    resp = client.call_tool("bea_analyze", {"category": "unknown", "t_values": "x=1"})
    assert_eq(resp["result"].get("isError"), True, "非法品类 → isError")

    # 缺维度
    resp = client.call_tool("bea_analyze", {"category": "phone", "t_values": "形状=3"})
    assert_eq(resp["result"].get("isError"), True, "缺维度 → isError")

    # t 值越界
    resp = client.call_tool("bea_analyze", {"category": "phone", "t_values": "形状=11,质感=3,色彩=3,构图=3,光影=3,细节=3"})
    assert_eq(resp["result"].get("isError"), True, "t 值越界 → isError")

    # 未知方法
    resp = client.send("unknown/method")
    assert_eq(resp.get("error", {}).get("code"), -32601, "未知方法 → -32601")

    client.close()


def main():
    print("=" * 60)
    print("  BEA MCP Server 自测")
    print("=" * 60)

    # 检查服务器文件存在
    if not os.path.exists(_SERVER):
        print(f"❌ 服务器文件不存在：{_SERVER}")
        sys.exit(1)

    # 检查引擎文件存在
    if not os.path.exists(_ENGINE):
        print(f"❌ 引擎文件不存在：{_ENGINE}")
        sys.exit(1)

    print(f"  服务器：{_SERVER}")
    print(f"  引擎：{_ENGINE}")
    print(f"  Python：{sys.executable}")
    print()

    try:
        test_handshake()
        test_tools_list()
        test_analyze()
        test_compare()
        test_dimensions()
        test_diagnose()
        test_suggest()
        test_generate()
        test_sensitivity()
        test_paradigms()
        test_diseases()
        test_health()
        test_multigroup()
        test_style_cycle()
        test_error_paths()
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()
    print("=" * 60)
    if FAIL == 0:
        print(f"  PASS：MCP server 自测 {PASS} 项全部通过")
    else:
        print(f"  FAIL：{PASS} 通过，{FAIL} 失败")
    print("=" * 60)

    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()