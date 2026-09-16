#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

"""BEA 标定器——用人工标注回归校准「特征 → t 值」映射。

背景：bea_image.py 的出厂线性表（FEATURE_SCALE）是未校准的合理猜测。
本模块把「程序算的 t」与「人/AI 按标尺（bea_rubric）打的 t」做逐维度
最小二乘拟合，产出仿射修正 t_final = clip(a * t_program + b)，
写入 data/calibration.json 后 bea_image 自动加载应用——让像素通道
从「能用」变「可信」，且案例越多、修正越准。

工作流（维护者 CLI，纯标准库）：
    1. collect: 对图片目录逐张提取特征与程序 t 值，产出待标注 CSV
       （t_human 列留空）
    2. 人工/AI 对照 bea_rubric 标尺填写 t_human（0-10 整数）
    3. fit:     逐维度最小二乘，产出 data/calibration.json
    4. status:  查看当前标定状态与拟合质量

用法：
    python3 scripts/bea_calibrate.py collect <图片目录> --out samples.csv [--category building]
    python3 scripts/bea_calibrate.py fit samples.csv [--out data/calibration.json]
    python3 scripts/bea_calibrate.py status
"""

import csv
import datetime
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, ".."))

# CSV 列：定位信息 + 标注列 + 七项原始特征（供未来更精细的映射重拟合）
CSV_COLUMNS = ["file", "category", "dimension", "t_program", "t_human",
               "sharpness", "symmetry", "texture", "light_hardness",
               "color_intensity", "warmth", "gravity"]

DEFAULT_CALIB_PATH = os.path.join(_ROOT, "data", "calibration.json")


def _load_image_module():
    """动态加载 bea_image（其自身会加载 bea_quant）。"""
    path = os.path.join(_HERE, "bea_image.py")
    spec = importlib.util.spec_from_file_location("bea_image_cal", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ols(xs, ys):
    """一元线性最小二乘 y = a*x + b。返回 dict(a, b, r2, n)。

    样本数 < 2 或 x 无方差时返回 None（不可拟合）。
    """
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 1e-12:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    a = sxy / sxx
    b = my - a * mx
    ss_res = sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 1.0
    return {"a": round(a, 6), "b": round(b, 6), "r2": round(r2, 4), "n": n}


# ──────────────────────────────────────────────
# collect：图片目录 → 待标注 CSV
# ──────────────────────────────────────────────

def collect(image_dir: str, out_csv: str, category: str = None) -> int:
    """对目录内图片提取特征与程序 t 值，写出待标注 CSV。返回行数。

    品类推断规则：文件名以下划线/连字符前的品类名开头（如 building_x.jpg）；
    无法推断且未给 --category 时报错。
    """
    img = _load_image_module()
    cats = sorted(img.DIM_MAP)
    rows = []
    names = sorted(f for f in os.listdir(image_dir)
                   if f.lower().rsplit(".", 1)[-1] in
                   {"png", "jpg", "jpeg", "webp", "bmp", "gif"})
    if not names:
        raise FileNotFoundError(f"目录中没有图片：{image_dir}")
    for name in names:
        cat = category
        if cat is None:
            head = name.lower().split("_")[0].split("-")[0]
            cat = head if head in cats else None
        if cat not in cats:
            raise ValueError(
                f"{name}: 无法推断品类，请用 --category 指定或按 "
                f"<品类>_<描述>.png 命名（可选：{'/'.join(cats)}）")
        path = os.path.join(image_dir, name)
        feats = img.extract_features(path)
        t, _ = img.features_to_t(cat, feats)
        for dim, tv in t.items():
            rows.append({"file": name, "category": cat, "dimension": dim,
                         "t_program": tv, "t_human": "",
                         **{k: f"{feats[k]:.6f}" for k in
                            ("sharpness", "symmetry", "texture",
                             "light_hardness", "color_intensity",
                             "warmth", "gravity")}})
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


# ──────────────────────────────────────────────
# fit：已标注 CSV → calibration.json
# ──────────────────────────────────────────────

def fit(csv_path: str, out_json: str = None, min_n: int = 3) -> dict:
    """对已标注 CSV 逐维度拟合 t_human ≈ a*t_program + b。

    n < min_n 或无方差的维度跳过并警告。返回拟合摘要。
    """
    img = _load_image_module()
    per_dim = {}
    skipped = []
    samples = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        groups = {}
        for row in reader:
            th = (row.get("t_human") or "").strip()
            if not th:
                continue  # 未标注的行跳过
            key = (row["category"], row["dimension"])
            groups.setdefault(key, []).append(
                (float(row["t_program"]), float(th)))
    for (cat, dim), pairs in sorted(groups.items()):
        if dim not in img._bq.CATEGORY_WEIGHTS.get(cat, {}):
            skipped.append(f"{cat}/{dim}（引擎无此维度，疑标注错误）")
            continue
        res = ols([p[0] for p in pairs], [p[1] for p in pairs])
        if res is None:
            skipped.append(f"{cat}/{dim}（n<2 或程序 t 无方差，不可拟合）")
            continue
        if res["n"] < min_n:
            skipped.append(f"{cat}/{dim}（样本 {res['n']}<{min_n}，暂不纳入）")
            continue
        per_dim[f"{cat}/{dim}"] = res
        samples += res["n"]
    summary = {
        "version": img._bq.__version__,
        "fitted_at": datetime.date.today().isoformat(),
        "source": os.path.basename(csv_path),
        "samples": samples,
        "per_dim": per_dim,
    }
    if out_json:
        os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    if skipped:
        print("  跳过：", "; ".join(skipped))
    return summary


def format_summary(summary: dict) -> str:
    lines = [f"标定完成：{len(summary['per_dim'])} 个维度，"
             f"{summary['samples']} 个样本（引擎 v{summary['version']}，"
             f"{summary['fitted_at']}）"]
    for key, r in summary["per_dim"].items():
        quality = "优" if r["r2"] >= 0.9 else ("良" if r["r2"] >= 0.7 else "差")
        lines.append(f"  {key}: t' = {r['a']:.3f}*t + {r['b']:+.3f}  "
                     f"R²={r['r2']:.3f}  n={r['n']}  [{quality}]")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# status：查看当前标定状态
# ──────────────────────────────────────────────

def status() -> str:
    img = _load_image_module()
    cal = img.CALIBRATION
    if not cal or not cal.get("per_dim"):
        return "未标定（bea_image 使用出厂线性表 FEATURE_SCALE）"
    lines = [f"已加载标定：{len(cal['per_dim'])} 个维度，"
             f"{cal.get('samples', '?')} 个样本（{cal.get('fitted_at', '?')}）"]
    for key, r in sorted(cal["per_dim"].items()):
        lines.append(f"  {key}: a={r['a']:.3f} b={r['b']:+.3f} "
                     f"R²={r['r2']:.3f} n={r['n']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "collect":
        args = [a for a in argv[1:] if not a.startswith("--")]
        if len(args) < 1:
            print("用法：collect <图片目录> [--out samples.csv] [--category cat]")
            return 2
        image_dir = args[0]
        out = args[1] if len(args) > 1 else "samples.csv"
        category = None
        if "--category" in argv:
            category = argv[argv.index("--category") + 1]
        n = collect(image_dir, out, category)
        print(f"✓ {n} 行已写入 {out}——请对照 bea_rubric 标尺填写 t_human 列"
              f"（0-10 整数），然后运行 fit")
        return 0
    if cmd == "fit":
        args = [a for a in argv[1:] if not a.startswith("--")]
        if not args:
            print("用法：fit <已标注.csv> [--out data/calibration.json]")
            return 2
        out = DEFAULT_CALIB_PATH
        if "--out" in argv:
            out = argv[argv.index("--out") + 1]
        summary = fit(args[0], out)
        print(format_summary(summary))
        print(f"✓ 已写入 {out}——bea_image / bea_analyze_image 自动加载生效")
        return 0
    if cmd == "status":
        print(status())
        return 0
    print(f"未知子命令 {cmd!r}，可选：collect / fit / status")
    return 2


if __name__ == "__main__":
    sys.exit(main())
