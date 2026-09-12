#!/usr/bin/env python3
"""CI：案例算式复算门。

案例库中每个声明的 W(T) 必须与 wt_calc 按同一权重表复算的结果一致（容差 0.005）。
注册表条目即案例文件中写明的各维度 t 值——改案例数字时必须同步改这里，
这门检查的存在就是为了防止「算式漂移」（声明一个数、公式算另一个数）。
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "bipolar-emotion-aesthetics", "scripts"))
from wt_calc import CATEGORY_WEIGHTS, compute_wt  # noqa: E402

# (案例, 场景, 品类, {维度: t}, 案例声明的 W(T))
REGISTRY = [
    ("demo-phone", "现状", "phone",
     {"形状线条": 2, "质感触觉": 3, "色彩": 4, "构图比例": 2, "光影": 3, "细节线条": 1}, 0.255),
    ("demo-phone", "初版处方", "phone",
     {"形状线条": 3, "质感触觉": 5, "色彩": 3, "构图比例": 2, "光影": 5, "细节线条": 5}, 0.375),
    ("demo-phone", "回调后", "phone",
     {"形状线条": 2, "质感触觉": 4, "色彩": 3, "构图比例": 2, "光影": 3, "细节线条": 4}, 0.295),
    ("demo-logo", "方案A 现状", "brand",
     {"图形形状": 2, "色彩": 2, "字体": 2, "版式构图": 2, "质感": 1}, 0.19),
    ("demo-logo", "方案B 微差补偿", "brand",
     {"图形形状": 3, "色彩": 3, "字体": 3, "版式构图": 3, "质感": 4}, 0.31),
    ("demo-poster", "现状", "brand",
     {"图形形状": 8, "色彩": 8, "字体": 7, "版式构图": 7, "质感": 6}, 0.74),
    ("demo-poster", "处方后", "brand",
     {"图形形状": 7, "色彩": 6, "字体": 6, "版式构图": 5, "质感": 5}, 0.595),
    ("iphone-17-pro", "iPhone 16 Pro", "phone",
     {"形状线条": 2, "质感触觉": 4, "色彩": 2, "构图比例": 3, "光影": 3, "细节线条": 3}, 0.285),
    ("iphone-17-pro", "iPhone 17 Pro", "phone",
     {"形状线条": 5, "质感触觉": 4, "色彩": 6, "构图比例": 6, "光影": 3, "细节线条": 4}, 0.475),
    ("aito-m9", "现状", "car",
     {"形体曲面动势": 2, "特征线条": 2, "灯组图形": 3, "比例姿态": 2, "材质光影": 3}, 0.23),
    ("aito-m9", "处方后", "car",
     {"形体曲面动势": 4, "特征线条": 6, "灯组图形": 6, "比例姿态": 4, "材质光影": 2}, 0.45),
]

TOL = 0.005


def main():
    failed = 0
    for case, scene, cat, tvals, claimed in REGISTRY:
        total, _ = compute_wt(CATEGORY_WEIGHTS[cat], tvals)
        ok = abs(total - claimed) <= TOL
        status = "OK " if ok else "FAIL"
        print(f"[{status}] {case} / {scene}: 声明 {claimed}，复算 {total:.3f}")
        if not ok:
            failed += 1
    print("-" * 50)
    if failed:
        print(f"{failed} 项不一致——案例数字必须等于公式计算结果，禁止四舍五入以外的修饰。")
        sys.exit(1)
    print(f"全部 {len(REGISTRY)} 项复算一致 ✓")


if __name__ == "__main__":
    main()
