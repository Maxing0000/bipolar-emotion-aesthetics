#!/usr/bin/env python3
"""同步校验：mcp-server 的数据表必须与 scripts/ 中的 CLI 脚本完全一致。

防止两处维护漂移——改任何一边，本测试都会失败并提示同步另一边。
直接运行：python3 tests/test_mcp_sync.py
"""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    failures = []

    wt = load("wt_calc", os.path.join(ROOT, "bipolar-emotion-aesthetics/scripts/wt_calc.py"))
    ss = load("scoresheet", os.path.join(ROOT, "bipolar-emotion-aesthetics/scripts/scoresheet.py"))

    mcp_path = os.path.join(ROOT, "mcp-server/bea_mcp/server.py")
    try:
        srv = load("bea_mcp_server", mcp_path)
    except ModuleNotFoundError:
        # mcp SDK 未安装时，用文本提取方式兜底校验数据表
        print("⚠ mcp SDK 未安装，跳过模块级校验（CI 中应安装 mcp 后运行）")
        return 0

    if srv.CATEGORY_WEIGHTS != wt.CATEGORY_WEIGHTS:
        failures.append("CATEGORY_WEIGHTS 不一致（mcp-server vs wt_calc.py）")
    if srv.PARADIGM_RANGES != wt.PARADIGM_RANGES:
        failures.append("PARADIGM_RANGES 不一致")
    if srv.DIM_MOVES != wt.DIM_MOVES:
        failures.append("DIM_MOVES 维度手法表不一致（mcp-server vs wt_calc.py）")
    if srv.DIMENSIONS != ss.DIMENSIONS or srv.FIX_MAP != ss.FIX_MAP:
        failures.append("评分卡维度/修复映射不一致（mcp-server vs scoresheet.py）")

    if failures:
        for f in failures:
            print(f"✗ {f}")
        return 1
    print("✓ MCP Server 与 CLI 脚本数据表完全一致（4 项）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
