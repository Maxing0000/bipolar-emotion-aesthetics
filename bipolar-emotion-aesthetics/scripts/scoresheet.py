#!/usr/bin/env python3
"""BEA 评分卡：四维打分 + 短板定位 + 自动映射回六步法的修正步骤。

用法：
  python3 scoresheet.py --s "张力=20,秩序=22,阈值=23,语境=21"
  python3 scoresheet.py --s "20,22,23,21"          # 按固定顺序：张力/秩序/阈值/语境
  python3 scoresheet.py --s "..." --json            # 机器可读输出

四维各 25 分：双极张力 / 结构秩序 / 阈值安全 / 语境适配。
总分 ≥80 为成熟作品；任一维 <15 为短板，须回六步法对应环节重修。
分值为协作刻度，不是心理物理常数。
"""
import argparse
import json
import sys

DIMENSIONS = ["张力", "秩序", "阈值", "语境"]
FULL_NAMES = {
    "张力": "双极张力",
    "秩序": "结构秩序",
    "阈值": "阈值安全",
    "语境": "语境适配",
}
# 短板 → 六步法回修环节（method.md）
FIX_MAP = {
    "张力": "回第四步「配比与强调」：调整主辅极比例（主导极 60%–90%），检查强调点数量（一视域 ≤2 个）；张力过低补危极细节锚点，过高降高权重维度 t 值。",
    "秩序": "回第三步「秩序组织」：叠加五种秩序手段（对称/比例/节奏/层级/呼应），确立至少一条贯穿全局的统一要素（共同色板/栅格/母题）。",
    "阈值": "回第五步「校阈」：本能红线一票否决；认知阈靠补秩序/降复杂度右移；文化阈做符号审计（audit-templates.md 模板 8）。",
    "语境": "回第二步「范式选择」：重做受众三问（阈值/距离时长/第一情绪），检查符号层文化联想与使用场景是否错配。",
}


def parse_scores(spec: str):
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    scores = {}
    if all("=" in p for p in parts):
        for p in parts:
            k, v = p.rsplit("=", 1)
            k = k.strip()
            if k not in DIMENSIONS:
                sys.exit(f"未知维度 {k!r}，应为：{'/'.join(DIMENSIONS)}")
            scores[k] = float(v)
    else:
        if len(parts) != 4:
            sys.exit("简写形式须按顺序给 4 个分数：张力,秩序,阈值,语境")
        scores = dict(zip(DIMENSIONS, (float(p) for p in parts)))
    missing = [d for d in DIMENSIONS if d not in scores]
    if missing:
        sys.exit(f"缺少维度：{'、'.join(missing)}")
    for d, v in scores.items():
        if not 0 <= v <= 25:
            sys.exit(f"{FULL_NAMES[d]} 得分 {v} 超出 0-25")
    return scores


def evaluate(scores: dict):
    total = sum(scores.values())
    short_boards = [d for d in DIMENSIONS if scores[d] < 15]
    return {
        "total": round(total, 1),
        "mature": total >= 80,
        "short_boards": short_boards,
        "fixes": {d: FIX_MAP[d] for d in short_boards},
    }


def main():
    ap = argparse.ArgumentParser(description="BEA 评分卡")
    ap.add_argument("--s", required=True, help='四维得分，如 "张力=20,秩序=22,阈值=23,语境=21" 或 "20,22,23,21"')
    ap.add_argument("--json", action="store_true", help="机器可读 JSON 输出")
    args = ap.parse_args()

    scores = parse_scores(args.s)
    result = evaluate(scores)

    if args.json:
        print(json.dumps({"scores": scores, **result}, ensure_ascii=False, indent=2))
        return

    print("BEA 评分卡")
    print("-" * 44)
    for d in DIMENSIONS:
        v = scores[d]
        bar = "█" * int(round(v))
        flag = "  ⚠ 短板" if v < 15 else ""
        print(f"{FULL_NAMES[d]:<6}{v:>6.1f}/25  {bar:<25}{flag}")
    print("-" * 44)
    verdict = "成熟作品（≥80）" if result["mature"] else "未成熟（<80）"
    print(f"总分 {result['total']}/100    {verdict}")
    if result["short_boards"]:
        print("\n短板修复指引（回六步法对应环节）：")
        for d in result["short_boards"]:
            print(f"  · {FULL_NAMES[d]}：{result['fixes'][d]}")
    else:
        print("无短板维度（均 ≥15）。")


if __name__ == "__main__":
    main()
