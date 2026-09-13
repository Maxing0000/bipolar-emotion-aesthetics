#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BEA 盲评实验数据分析：读入 experiment.html 导出的 JSON，输出统计报告与 Issue 模板。

用法：
    python3 analyze_experiment.py data.json [data2.json ...]

判定规则（docs/experiment-protocol.md 第三节）：
    支持窗口预测：窗口内版本的喜好度均值比两个窗外版本均高 ≥0.8 分，
    且设计相关组偏好峰值相对大众组右移（如有分组数据）。
"""
import json
import sys


def load_data(paths):
    """合并多份导出文件。"""
    category, versions, responses = None, None, []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if category is None:
            category, versions = d["category"], d["versions"]
        elif d["versions"] != versions:
            raise ValueError(f"{p} 的版本配置与其他文件不一致，不能合并")
        responses.extend(d["responses"])
    if not responses:
        raise ValueError("没有任何被试数据")
    return category, versions, responses


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def stats(versions, responses, key, filt=None):
    """各版本某指标均值。filt 为被试筛选函数。"""
    pool = [r for r in responses if filt is None or filt(r)]
    out = {}
    for v in versions:
        vals = [r["ratings"][v["id"]][key] for r in pool
                if v["id"] in r.get("ratings", {}) and key in r["ratings"][v["id"]]]
        out[v["id"]] = (round(mean(vals), 2), len(vals))
    return out


def verdict(versions, responses):
    """按协议判定规则给出结论。返回 (是否支持, 说明行列表)。"""
    notes = []
    by_wt = sorted(versions, key=lambda v: v["wt"])
    mid = by_wt[len(by_wt) // 2] if len(by_wt) % 2 == 1 else None
    if mid is None:
        return None, ["版本数为偶数，无法自动判定窗口内版本，请人工核对"]
    in_id = mid["id"]
    like = stats(versions, responses, "like")
    like_mid = like[in_id][0]
    outs = [v for v in versions if v["id"] != in_id]
    diffs = {v["id"]: round(like_mid - like[v["id"]][0], 2) for v in outs}
    notes.append(f"窗口内版本 {in_id}（W(T)={mid['wt']}）喜好度均值 {like_mid}，"
                 f"对窗外版本差值：" + "、".join(f"{k} {d:+.2f}" for k, d in diffs.items()))
    main_ok = all(d >= 0.8 for d in diffs.values())

    # 分组：设计相关 vs 大众
    pro = [r for r in responses if r["background"].get("design") == "yes"]
    pub = [r for r in responses if r["background"].get("design") == "no"]
    shift_note = "分组数据不足（设计相关组与大众组都需 ≥2 人），未检验右移"
    shift_ok = None
    if len(pro) >= 2 and len(pub) >= 2:
        like_pro = stats(versions, responses, "like",
                         filt=lambda r: r["background"].get("design") == "yes")
        like_pub = stats(versions, responses, "like",
                         filt=lambda r: r["background"].get("design") == "no")
        peak_pro = max(like_pro, key=lambda k: like_pro[k][0])
        peak_pub = max(like_pub, key=lambda k: like_pub[k][0])
        wt_of = {v["id"]: v["wt"] for v in versions}
        shift_ok = wt_of[peak_pro] > wt_of[peak_pub]
        shift_note = (f"偏好峰值：设计相关组 {peak_pro}（W(T)={wt_of[peak_pro]}），"
                      f"大众组 {peak_pub}（W(T)={wt_of[peak_pub]}）"
                      f" → 峰值{'右移 ✓' if shift_ok else '未右移'}")
    notes.append(shift_note)
    if main_ok and shift_ok is not False:
        return True, notes
    return False, notes


def report(category, versions, responses):
    lines = [
        f"【BEA 盲评实验报告】品类：{category}",
        f"被试：n={len(responses)}（设计相关 "
        f"{sum(1 for r in responses if r['background'].get('design') == 'yes')} / 大众 "
        f"{sum(1 for r in responses if r['background'].get('design') == 'no')}）",
        "",
        "版本与 W(T)：" + " / ".join(f"{v['id']}={v['wt']}" for v in versions),
    ]
    for key, name in (("like", "喜好度"), ("pay", "付费/转发意愿")):
        s = stats(versions, responses, key)
        lines.append(f"{name}均值：" + " / ".join(f"{vid} {val}" for vid, (val, _) in s.items()))
    lines.append("")
    ok, notes = verdict(versions, responses)
    lines.extend(notes)
    lines.append("")
    lines.append("判定：" + ("支持窗口预测 ✓（可写入证据库）" if ok else
                            "不支持窗口预测 ✗（应回应：修正权重表/窗口区间——好反例比好观点更有价值）"))
    lines.append("")
    lines.append("—— Issue 提交模板（标题前缀 [盲评数据]）——")
    s_like = stats(versions, responses, "like")
    s_pay = stats(versions, responses, "pay")
    lines.append(f"- 品类：{category}")
    lines.append("- 版本与 W(T)：" + " / ".join(f"{v['id']}={v['wt']}" for v in versions))
    lines.append(f"- 被试：n={len(responses)}")
    lines.append("- 喜好度均值：" + " / ".join(f"{vid} {val}" for vid, (val, _) in s_like.items()))
    lines.append("- 付费意愿均值：" + " / ".join(f"{vid} {val}" for vid, (val, _) in s_pay.items()))
    lines.append("- 结论：" + ("支持" if ok else "不支持") + " 窗口预测")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        sys.exit("用法：python3 analyze_experiment.py data.json [data2.json ...]")
    category, versions, responses = load_data(sys.argv[1:])
    print(report(category, versions, responses))


if __name__ == "__main__":
    main()
