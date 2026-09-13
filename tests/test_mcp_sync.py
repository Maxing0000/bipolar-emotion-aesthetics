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
    rb = load("rubric", os.path.join(ROOT, "bipolar-emotion-aesthetics/scripts/rubric.py"))

    mcp_dir = os.path.join(ROOT, "mcp-server")
    if mcp_dir not in sys.path:
        sys.path.insert(0, mcp_dir)
    try:
        import bea_mcp.server as srv
        from bea_mcp.rubric_data import RUBRICS as srv_rubrics
    except ModuleNotFoundError:
        # mcp SDK 未安装时，跳过模块级校验
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
    if srv_rubrics != rb.RUBRICS:
        failures.append("RUBRICS 视觉评分标尺不一致（mcp-server/rubric_data.py vs rubric.py）")

    # 诊断报告：同一份输入，CLI 与 MCP 输出必须逐字一致
    rpt = load("report", os.path.join(ROOT, "bipolar-emotion-aesthetics/scripts/report.py"))
    cases = [
        ("phone", wt.CATEGORY_WEIGHTS["phone"],
         {"形状线条": 5, "质感触觉": 4, "色彩": 6, "构图比例": 6, "光影": 3, "细节线条": 4},
         0.28, {"张力": 20, "秩序": 22, "阈值": 13, "语境": 21}, "测试机"),
        ("car", wt.CATEGORY_WEIGHTS["car"],
         {"形体曲面动势": 2, "特征线条": 2, "灯组图形": 3, "比例姿态": 2, "材质光影": 3},
         0.0, None, ""),
        ("ui", wt.CATEGORY_WEIGHTS["ui"],
         {"布局留白": 3, "色彩对比": 2, "组件形": 2, "动效": 2, "字体图标": 3},
         0.45, {"张力": 18, "秩序": 21, "阈值": 24, "语境": 22}, ""),
    ]
    for cat, wts, tv, tgt, sc, nm in cases:
        cli_out = rpt.generate_report(cat, wts, tv, target=tgt, scores=sc, name=nm, date_str="2026-09-13")
        mcp_out = srv.generate_report(cat, wts, tv, target=tgt, scores=sc, name=nm, date_str="2026-09-13")
        if cli_out != mcp_out:
            failures.append(f"generate_report 输出不一致（{cat}，target={tgt}）——同步 report.py 与 server.py")

    if failures:
        for f in failures:
            print(f"✗ {f}")
        return 1
    print("✓ MCP Server 与 CLI 脚本数据表完全一致（6 项）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
