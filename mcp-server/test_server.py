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
           ["bea_analyze", "bea_compare", "bea_dimensions",
            "bea_suggest", "bea_generate", "bea_sensitivity", "bea_batch",
            "bea_rubric", "bea_analyze_image"],
           "tools/list：九个工具")
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

        # 6b. bea_suggest：范式名目标 + 步骤 + 验证
        sug = payload(call_tool(proc, "bea_suggest",
                                {"category": "phone",
                                 "t_values": "形状=2,质感=4,色彩=3,构图=3,光影=4,细节=4",
                                 "target": "崇高震撼"}))
        ok(sug["target_wt"] == 0.54, "bea_suggest：范式名解析为中点 0.54")
        ok(len(sug["steps"]) > 0 and all("dimension" in s for s in sug["steps"]),
           "bea_suggest：调整步骤齐全")
        ok(sug["verification"] is not None and "achieved" in sug["verification"],
           "bea_suggest：附调整后验证")

        # 6c. bea_generate：数值目标 + 生成配置可回流验证
        gen = payload(call_tool(proc, "bea_generate",
                                {"category": "car", "target": "0.30", "strategy": "balanced"}))
        ok(set(gen["dimensions"]) == set(_bq.CATEGORY_WEIGHTS["car"]),
           "bea_generate：生成维度与品类一致")
        ok(abs(gen["w_t"] - 0.30) <= 0.05, f"bea_generate：W(T)={gen['w_t']} 接近目标 0.30")
        ok("t_str" in gen and "=" in gen["t_str"], "bea_generate：附可直接复用的 t_str")
        ok("w_t" in gen["analysis"], "bea_generate：analysis 已转为可序列化 dict")

        # 6d. bea_sensitivity：结果按综合灵敏度排序
        sen = payload(call_tool(proc, "bea_sensitivity",
                                {"category": "phone",
                                 "t_values": "形状=2,质感=4,色彩=3,构图=3,光影=4,细节=4",
                                 "step": 1}))
        ok(len(sen["results"]) == 6 and "wt_plus" in sen["results"][0],
           "bea_sensitivity：六维度差分结果齐全")
        ok("report_markdown" in sen and sen["report_markdown"], "bea_sensitivity：附报告")

        # 6e. bea_batch：多对象排名
        bat = payload(call_tool(proc, "bea_batch",
                                {"category": "ui",
                                 "items": ["甲=3,6,4,3,5", "乙=4,4,4,4,4", "丙=7,7,6,6,7"]}))
        ok(bat["count"] == 3 and len(bat["ranking"]) == 3, "bea_batch：三对象全部分析")
        wts = [r["w_t"] for r in bat["results"]]
        ok(wts == sorted(wts), "bea_batch：结果按 W(T) 升序排名")
        ok("report_markdown" in bat and bat["report_markdown"], "bea_batch：附批量报告")

        # 6f. bea_rubric：标尺文本与引擎维度一致
        rub = payload(call_tool(proc, "bea_rubric", {"category": "building"}))
        ok(list(rub["dimensions"]) == list(_bq.CATEGORY_WEIGHTS["building"]),
           "bea_rubric：building 维度与引擎一致")
        ok("形体轮廓" in rub["rubric_markdown"] and "t=8" in rub["rubric_markdown"],
           "bea_rubric：标尺文本含锚点")
        bad_rub = call_tool(proc, "bea_rubric", {"category": "nope"})
        ok(bad_rub.get("isError") is True, "bea_rubric：未知品类 → isError")

        # 6g. bea_analyze_image：Pillow 可用则端到端，不可用则优雅报错
        _has_pil = importlib.util.find_spec("PIL") is not None
        if _has_pil:
            import tempfile
            with tempfile.TemporaryDirectory() as td:
                p1 = os.path.join(td, "soft.png")
                p2 = os.path.join(td, "harsh.png")
                _make_images(p1, p2)
                img1 = payload(call_tool(proc, "bea_analyze_image",
                                         {"category": "phone", "path": p1}))
                img2 = payload(call_tool(proc, "bea_analyze_image",
                                         {"category": "phone", "path": p2}))
                ok(set(img1["features"]) ==
                   {"sharpness", "symmetry", "texture", "light_hardness",
                    "color_intensity", "warmth", "gravity"},
                   "bea_analyze_image：七项特征齐全")
                ok(all(0 <= v <= 10 for v in img1["feature_t_values"].values()),
                   "bea_analyze_image：t 值在 0-10")
                ok(img1["w_t"] < img2["w_t"], "bea_analyze_image：柔和图 W(T) < 硬朗图")
                bad_img = call_tool(proc, "bea_analyze_image",
                                    {"category": "phone", "path": "/nonexistent.png"})
                ok(bad_img.get("isError") is True, "bea_analyze_image：文件不存在 → isError")
        else:
            no_pil = call_tool(proc, "bea_analyze_image",
                               {"category": "phone", "path": "/tmp/x.png"})
            ok(no_pil.get("isError") is True and "Pillow" in no_pil["content"][0]["text"],
               "bea_analyze_image：无 Pillow 优雅报错（CI 环境属预期）")

        # 7. 错误路径：未知工具 / 非法品类 / 非法维度 / 非法策略 / 空 items
        bad1 = call_tool(proc, "no_such_tool", {})
        ok(bad1.get("isError") is True, "未知工具 → isError")
        bad2 = call_tool(proc, "bea_analyze", {"category": "logo", "t_values": {}})
        ok(bad2.get("isError") is True, "非法品类 → isError")
        bad3 = call_tool(proc, "bea_analyze",
                         {"category": "phone", "t_values": {"形状": 3}})
        ok(bad3.get("isError") is True, "缺维度 → isError")
        bad4 = call_tool(proc, "bea_generate",
                         {"category": "car", "target": "0.3", "strategy": "wild"})
        ok(bad4.get("isError") is True, "非法策略 → isError")
        bad5 = call_tool(proc, "bea_batch", {"category": "ui", "items": []})
        ok(bad5.get("isError") is True, "空 items → isError")

        # 8. 未知方法 → JSON-RPC 错误
        send(proc, {"jsonrpc": "2.0", "id": 7, "method": "resources/list"})
        err = recv(proc)
        ok(err["error"]["code"] == -32601, "未知方法 → -32601")

        print(f"\nPASS：MCP server 自测 {_checks} 项全部通过")
        return 0
    finally:
        proc.stdin.close()
        proc.wait(timeout=5)


def _make_images(soft_path, harsh_path):
    """生成一柔一硬两张合成图，供 bea_analyze_image 端到端验证。"""
    from PIL import Image, ImageDraw
    size = 256
    im = Image.new("RGB", (size, size))
    px = im.load()
    for y in range(size):
        for x in range(size):
            px[x, y] = (220 - y // 6, 210 - y // 8, 190)
    ImageDraw.Draw(im).ellipse([88, 88, 168, 168], fill=(235, 225, 205))
    im.save(soft_path)

    im2 = Image.new("RGB", (size, size))
    px2 = im2.load()
    for y in range(size):
        for x in range(size):
            v = 255 if ((x // 16 + y // 16) % 2 == 0) else 10
            if abs(x - y) < 6:
                v = 255 - v
            px2[x, y] = (v, v, 255 - v)
    ImageDraw.Draw(im2).polygon([(0, 255), (128, 0), (255, 255)],
                                outline=(255, 255, 255), width=8)
    im2.save(harsh_path)


if __name__ == "__main__":
    sys.exit(main())
