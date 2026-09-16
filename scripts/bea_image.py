#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2026 马星. Licensed under CC BY-NC-SA 4.0.

"""BEA 图像特征引擎——从像素到 W(T) 的程序化通道。

流程：图片 → 六项特征提取（纯程序，无 AI 参与）→ 特征→t 值映射 →
复用 bea_quant.analyze 计算精确 W(T)。

特征提取依赖 Pillow（图像解码），属可选依赖：
    pip install "bea-mcp[image]"   # 或 pip install Pillow

v1 标定说明：特征→t 值的线性映射为初版人工标定，适用常规产品图/建筑照；
随案例库（data/cases.json）积累可继续回归校准。
"""

import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _engine_path() -> str:
    env = os.environ.get("BEA_ENGINE")
    if env and os.path.exists(env):
        return env
    repo_layout = os.path.join(_HERE, "..", "scripts", "bea_quant.py")
    if os.path.exists(repo_layout):
        return repo_layout
    return os.path.join(_HERE, "bea_quant.py")


_spec = importlib.util.spec_from_file_location("bea_quant", _engine_path())
_bq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bq)

try:
    from PIL import Image  # 可选依赖
except ImportError:  # pragma: no cover
    Image = None

# 分析用最大边长（性能与稳定性的平衡）
_MAX_SIDE = 256
_TEXTURE_BLOCK = 8

# ──────────────────────────────────────────────
# 特征 → 危极分（0-10）标定表：(raw_lo, t_at_lo, raw_hi, t_at_hi)
# raw 在 [lo,hi] 间线性映射到 [t_lo, t_hi]，可逆向（lo>hi 数值意义）
# ──────────────────────────────────────────────
FEATURE_SCALE = {
    # 拉普拉斯方差（边缘锐度）：低=柔和平缓，高=锋利切割
    "sharpness": (30.0, 1.5, 900.0, 8.5),
    # 水平镜像相似度：高对称=亲极，低对称=失衡危极
    "symmetry": (0.95, 1.5, 0.55, 8.0),
    # 纹理复杂度（块内标准差均值）：低=细腻平滑，高=粗粝强肌理
    "texture": (6.0, 1.5, 40.0, 8.0),
    # 光影硬度（反差跨度+硬边占比）：低=柔光均匀，高=舞台硬光
    "light_hardness": (0.12, 1.5, 0.55, 8.5),
    # 色彩强度（HSV 平均饱和度）：低=pastel 温润，高=高饱和撞色
    "color_intensity": (0.08, 1.5, 0.55, 8.0),
    # 色温（R-B 均值差）：暖=亲极，冷=危极（区间逆向）
    "warmth": (0.12, 2.5, -0.12, 7.5),
    # 构图重心偏移（边缘质量质心偏离画面中心，按半对角线归一）
    "gravity": (0.02, 2.0, 0.22, 8.0),
}

# ──────────────────────────────────────────────
# 品类维度 ← 特征 映射（权重和不必为 1，内部归一）
# ──────────────────────────────────────────────
DIM_MAP = {
    "phone": {
        "形状": [("sharpness", 0.6), ("symmetry", 0.4)],
        "质感": [("texture", 0.6), ("sharpness", 0.4)],
        "色彩": [("color_intensity", 0.7), ("warmth", 0.3)],
        "构图": [("symmetry", 0.5), ("gravity", 0.5)],
        "光影": [("light_hardness", 1.0)],
        "细节": [("sharpness", 0.4), ("texture", 0.6)],
    },
    "car": {
        "曲面": [("texture", 0.4), ("sharpness", 0.6)],
        "特征线": [("sharpness", 1.0)],
        "灯组": [("sharpness", 0.7), ("light_hardness", 0.3)],
        "比例": [("gravity", 0.6), ("symmetry", 0.4)],
        "材质": [("light_hardness", 0.5), ("color_intensity", 0.5)],
    },
    "brand": {
        "图形": [("sharpness", 0.6), ("symmetry", 0.4)],
        "色彩": [("color_intensity", 1.0)],
        "字体": [("sharpness", 1.0)],
        "版式": [("gravity", 0.5), ("symmetry", 0.5)],
        "质感": [("texture", 1.0)],
    },
    "ui": {
        "布局": [("gravity", 0.4), ("symmetry", 0.3), ("texture", 0.3)],
        "色彩对比": [("color_intensity", 0.6), ("light_hardness", 0.4)],
        "组件形": [("sharpness", 0.6), ("symmetry", 0.4)],
        # 动效无法从静态图提取，取中性值 5 并在结果中标注
        "字体图标": [("texture", 0.5), ("sharpness", 0.5)],
    },
    "building": {
        "形体轮廓": [("sharpness", 0.5), ("gravity", 0.5)],
        "立面线条": [("sharpness", 0.6), ("texture", 0.4)],
        "比例尺度": [("gravity", 0.5), ("symmetry", 0.5)],
        "材质肌理": [("texture", 1.0)],
        "光影空间": [("light_hardness", 1.0)],
    },
}

UNMEASURED = {"ui": {"动效": 5}}  # 静态图无法测量的维度 → 中性值


def _require_pillow():
    if Image is None:
        raise RuntimeError(
            "图像特征提取需要 Pillow：pip install 'bea-mcp[image]'（或 pip3 install Pillow）"
        )


def _load_gray_rgb(path: str):
    """读图、缩放到最大边 _MAX_SIDE，返回 (gray 二维列表, rgb 三通道均值原料)。"""
    _require_pillow()
    if not os.path.exists(path):
        raise FileNotFoundError(f"图片不存在：{path}")
    with Image.open(path) as im:
        im = im.convert("RGB")
        w, h = im.size
        scale = _MAX_SIDE / max(w, h)
        if scale < 1:
            im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))))
        rgb = list(im.getdata())
        w, h = im.size
        gray = [[0.0] * w for _ in range(h)]
        sat_sum = 0.0
        r_sum = b_sum = 0.0
        hsv = im.convert("HSV")
        hsv_px = list(hsv.getdata())
        for y in range(h):
            row = gray[y]
            for x in range(w):
                i = y * w + x
                r, g, b = rgb[i]
                row[x] = 0.299 * r + 0.587 * g + 0.114 * b
                sat_sum += hsv_px[i][1]
                r_sum += r
                b_sum += b
        n = w * h
        meta = {
            "w": w, "h": h,
            "sat": sat_sum / n,
            "warmth": (r_sum - b_sum) / (255.0 * n),
        }
    return gray, meta


def _laplacian_stats(gray):
    """返回 (拉普拉斯方差, 边缘质量图, 硬边占比)。"""
    h = len(gray)
    w = len(gray[0])
    edge_mass = [[0.0] * w for _ in range(h)]
    total_mass = 0.0
    hard = 0
    hard_count = 0
    vals = []
    for y in range(1, h - 1):
        up, cur, dn = gray[y - 1], gray[y], gray[y + 1]
        for x in range(1, w - 1):
            lap = (up[x - 1] + up[x] + up[x + 1] +
                   cur[x - 1] - 4.0 * cur[x] + cur[x + 1] +
                   dn[x - 1] + dn[x] + dn[x + 1])
            vals.append(lap)
            mag = abs(lap)
            edge_mass[y][x] = mag
            total_mass += mag
            hard_count += 1
            if mag > 50:
                hard += 1
    n = len(vals)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / n
    return var, edge_mass, total_mass, (hard / hard_count if hard_count else 0.0)


def _block_std_mean(gray, block=_TEXTURE_BLOCK):
    h = len(gray)
    w = len(gray[0])
    stds = []
    for by in range(0, h - block + 1, block):
        for bx in range(0, w - block + 1, block):
            s = s2 = 0.0
            for y in range(by, by + block):
                row = gray[y]
                for x in range(bx, bx + block):
                    v = row[x]
                    s += v
                    s2 += v * v
            n = block * block
            mean = s / n
            stds.append(max(0.0, s2 / n - mean * mean) ** 0.5)
    return sum(stds) / len(stds)


def _symmetry(gray):
    h = len(gray)
    w = len(gray[0])
    diff = 0.0
    for y in range(h):
        row = gray[y]
        for x in range(w // 2):
            diff += abs(row[x] - row[w - 1 - x])
    return 1.0 - (diff / (255.0 * (h * (w // 2))))


def _contrast_span(gray):
    px = sorted(v for row in gray for v in row)
    p5 = px[int(len(px) * 0.05)]
    p95 = px[min(len(px) - 1, int(len(px) * 0.95))]
    return (p95 - p5) / 255.0


def _gravity_offset(edge_mass, total_mass):
    h = len(edge_mass)
    w = len(edge_mass[0])
    cx = cy = 0.0
    for y in range(1, h - 1):
        row = edge_mass[y]
        for x in range(1, w - 1):
            m = row[x]
            cx += x * m
            cy += y * m
    if total_mass <= 0:
        return 0.0
    cx /= total_mass
    cy /= total_mass
    dx = (cx - (w - 1) / 2.0) / (w / 2.0)
    dy = (cy - (h - 1) / 2.0) / (h / 2.0)
    return (dx * dx + dy * dy) ** 0.5


def extract_features(path: str) -> dict:
    """从图片提取六项特征（原始值）。"""
    gray, meta = _load_gray_rgb(path)
    var, edge_mass, total_mass, hard_edge = _laplacian_stats(gray)
    contrast = _contrast_span(gray)
    return {
        "sharpness": var,
        "symmetry": _symmetry(gray),
        "texture": _block_std_mean(gray),
        "light_hardness": 0.5 * contrast + 0.5 * hard_edge,
        "color_intensity": meta["sat"],
        "warmth": meta["warmth"],
        "gravity": _gravity_offset(edge_mass, total_mass),
    }


def _raw_to_t(name: str, raw: float) -> float:
    lo, t_lo, hi, t_hi = FEATURE_SCALE[name]
    t = t_lo + (raw - lo) * (t_hi - t_lo) / (hi - lo)
    return max(0.0, min(10.0, t))


def features_to_t(category: str, feats: dict):
    """特征 → 各维度 t 值。返回 (t_dict, unmeasured_dict)。"""
    if category not in DIM_MAP:
        raise ValueError(f"未知品类 {category!r}，可选：{'/'.join(DIM_MAP)}")
    t = {}
    for dim, parts in DIM_MAP[category].items():
        num = den = 0.0
        for fname, weight in parts:
            num += weight * _raw_to_t(fname, feats[fname])
            den += weight
        t[dim] = int(round(num / den))
    unmeasured = UNMEASURED.get(category, {})
    for dim, default in unmeasured.items():
        t[dim] = default
    return t, dict(unmeasured)


def analyze_image(path: str, category: str):
    """图片 → 特征 → t 值 → 引擎全链路分析。

    返回 (BEAAnalysis, features, t_values, unmeasured)。
    """
    feats = extract_features(path)
    t, unmeasured = features_to_t(category, feats)
    t_str = ",".join(f"{k}={v}" for k, v in t.items())
    return _bq.analyze(category, t_str), feats, t, unmeasured
