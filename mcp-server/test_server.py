#!/usr/bin/env python3
# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

"""
BEA MCP Server 自测：起真实子进程，走完整 MCP 会话
（initialize → tools/list → tools/call × 3 → 错误路径 → ping），
并把工具返回结果与引擎直算结果逐一比对。

运行：python3 mcp-server/test_server.py
通过输出 PASS 并退出码 0，失败退出码 1。
"""

import importlib.util
import json
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SERVER = os.path.join(_HERE, "server.py")
_ENGINE = os.path.join(_HERE, "..", "scripts", "bea_quant.py")

_spec = importlib.util.spec_from_file_location("bea_quant", _ENGINE)
_bq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bq)

_checks = 0


def ok(cond, label):
    global _checks
    if not cond:
        print(f"FAIL: {label}")
        sys.exit(1)
    _checks += 1
    print(f"  ok: {label}")


def send(proc, obj):
    proc.stdin.write(json.dumps(obj, ensure_ascii=False) + "\n")
    proc.stdin.flush()


def recv(proc):
    line = proc.stdout.readline()
    assert line.strip(), "服务器意外关闭或无响应"
    return json.loads(line)


def call_tool(proc, name, arguments):
    send(proc, {"jsonrpc": "2.0", "id": 99, "method": "tools/call",
                "params": {"name": name, "arguments": arguments}})
    resp = recv(proc)
    assert resp["id"] == 99
    return resp["result"]


def payload(result):
    assert not result.get("isError"), result
    return json.loads(result["content"][0]["text"])


def main():
    proc = subprocess.Popen(
        [sys.executable, _SERVER],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        text=True, encoding="utf-8",
    )
    try:
        # 1. initialize 握手
        proto = "2024-11-05"
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": proto,
                               "capabilities": {}, "clientInfo": {"name": "test"}}})
        init = recv(proc)["result"]
        ok(init["protocolVersion"] == proto, "initialize：协议版本一致")
        ok(init["serverInfo"]["name"] == "bea", "initialize：serverInfo.name")
        ok(init["capabilities"]["tools"] == {}, "initialize：声明 tools 能力")
        ok(init["serverInfo"]["version"] == _bq.__version__,
           f"initialize：版本与引擎一致（{_bq.__version__}）")

        # 2. initialized 通知：不应产生任何响应行
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        send(proc, {"jsonrpc": "2.0", "id": 2, "method": "ping"})
        pong = recv(proc)
        ok(pong["id"] == 2, "通知不产生响应，ping 正常返回")

        # 3. tools/list
        send(proc, {"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
        tools = recv(proc)["result"]["tools"]
        ok([t["name"] for t in tools] ==
           ["bea_analyze", "bea_compare", "bea_dimensions"], "tools/list：三个工具")
        ok(all("inputSchema" in t for t in tools), "tools/list：均带 inputSchema")

        # 4. bea_analyze：与引擎直算比对
        t_str = "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6"
        result = call_tool(proc, "bea_analyze",
                           {"category": "phone", "t_values": t_str})
        data = payload(result)
        expected = _bq.analyze("phone", t_str)
        ok(data["w_t"] == round(expected.w_t, 3), f"bea_analyze：W(T)={data['w_t']} 与引擎一致")
        ok(data["paradigm"] == expected.paradigm, f"bea_analyze：范式={data['paradigm']}")
        ok(isinstance(data.get("report_markdown"), str) and data["report_markdown"],
           "bea_analyze：附 markdown 报告")

        # 对象格式入参也应等价
        result2 = payload(call_tool(proc, "bea_analyze",
                                    {"category": "phone",
                                     "t_values": {"形状": 3, "质感": 6, "色彩": 4,
                                                  "构图": 3, "光影": 5, "细节": 6}}))
        ok(result2["w_t"] == data["w_t"], "bea_analyze：dict 入参与字符串入参等价")

        # 5. bea_compare
        comp = payload(call_tool(proc, "bea_compare",
                                 {"category": "building",
                                  "a": "中银=8,7,6,5,6",
                                  "b": "汇丰=5,4,6,6,5"}))
        ok(set(comp["dimension_diff_a_minus_b"]) ==
           set(_bq.CATEGORY_WEIGHTS["building"]), "bea_compare：逐维度差值齐全")
        ok(comp["a"]["name"] == "中银" and comp["b"]["name"] == "汇丰",
           "bea_compare：双方名称解析正确")

        # 6. bea_dimensions
        dims = payload(call_tool(proc, "bea_dimensions", {}))
        ok(set(dims["categories"]) == set(_bq.CATEGORY_WEIGHTS),
           "bea_dimensions：返回全部 5 个品类")
        ok(len(dims["paradigms"]) == len(_bq.PARADIGMS), "bea_dimensions：六范式锚点齐全")
        one = payload(call_tool(proc, "bea_dimensions", {"category": "car"}))
        ok(list(one["categories"]) == ["car"], "bea_dimensions：单品类过滤")

        # 7. 错误路径：未知工具 / 非法品类 / 非法维度
        bad1 = call_tool(proc, "no_such_tool", {})
        ok(bad1.get("isError") is True, "未知工具 → isError")
        bad2 = call_tool(proc, "bea_analyze", {"category": "logo", "t_values": {}})
        ok(bad2.get("isError") is True, "非法品类 → isError")
        bad3 = call_tool(proc, "bea_analyze",
                         {"category": "phone", "t_values": {"形状": 3}})
        ok(bad3.get("isError") is True, "缺维度 → isError")

        # 8. 未知方法 → JSON-RPC 错误
        send(proc, {"jsonrpc": "2.0", "id": 7, "method": "resources/list"})
        err = recv(proc)
        ok(err["error"]["code"] == -32601, "未知方法 → -32601")

        print(f"\nPASS：MCP server 自测 {_checks} 项全部通过")
        return 0
    finally:
        proc.stdin.close()
        proc.wait(timeout=5)


if __name__ == "__main__":
    sys.exit(main())
