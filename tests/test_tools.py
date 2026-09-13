"""BEA 工具链单元测试：wt_calc、scoresheet 与 rubric。"""
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "bipolar-emotion-aesthetics", "scripts"))

import rubric  # noqa: E402
import scoresheet  # noqa: E402
import wt_calc  # noqa: E402
import report as rp  # noqa: E402
import analyze_experiment as ae  # noqa: E402


class TestWtCalc(unittest.TestCase):
    def test_known_values(self):
        # iPhone 17 Pro 案例：0.475
        total, _ = wt_calc.compute_wt(
            wt_calc.CATEGORY_WEIGHTS["phone"],
            {"形状线条": 5, "质感触觉": 4, "色彩": 6, "构图比例": 6, "光影": 3, "细节线条": 4})
        self.assertAlmostEqual(total, 0.475, places=3)

    def test_weights_sum_to_one(self):
        for cat, dims in wt_calc.CATEGORY_WEIGHTS.items():
            self.assertAlmostEqual(sum(dims.values()), 1.0, places=6, msg=cat)

    def test_paradigm_anchors(self):
        self.assertEqual(wt_calc.paradigm_of(0.10), "治愈松弛")
        self.assertEqual(wt_calc.paradigm_of(0.20), "亲和精致")
        self.assertEqual(wt_calc.paradigm_of(0.40), "均衡典雅")
        self.assertEqual(wt_calc.paradigm_of(0.90), "逼近越阈——非美区")

    def test_parse_t_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            wt_calc.parse_t("形状=11")
        with self.assertRaises(ValueError):
            wt_calc.parse_t("形状")

    def test_parse_t_chinese_comma(self):
        # 中文逗号应正常分隔，不得静默吞维度（debug 轮发现的真实 bug）
        r = wt_calc.parse_t("形状=2，色彩=3")
        self.assertEqual(r, {"形状": 2.0, "色彩": 3.0})

    def test_parse_t_non_numeric_friendly_error(self):
        with self.assertRaisesRegex(ValueError, "不是数字"):
            wt_calc.parse_t("形状=abc")


class TestPrescribe(unittest.TestCase):
    PHONE_T = {"形状线条": 5, "质感触觉": 4, "色彩": 6, "构图比例": 6, "光影": 3, "细节线条": 4}  # 0.475

    def test_soften_reaches_target(self):
        lines, new_t = wt_calc.prescribe(wt_calc.CATEGORY_WEIGHTS["phone"], self.PHONE_T, 0.28)
        after, _ = wt_calc.compute_wt(wt_calc.CATEGORY_WEIGHTS["phone"], new_t)
        self.assertAlmostEqual(after, 0.28, places=2)
        self.assertTrue(all(new_t[d] <= self.PHONE_T[d] for d in new_t))  # 减锐方向不升档

    def test_sharpen_reaches_target(self):
        car_t = {"形体曲面动势": 2, "特征线条": 2, "灯组图形": 3, "比例姿态": 2, "材质光影": 3}  # 0.23
        lines, new_t = wt_calc.prescribe(wt_calc.CATEGORY_WEIGHTS["car"], car_t, 0.55)
        after, _ = wt_calc.compute_wt(wt_calc.CATEGORY_WEIGHTS["car"], new_t)
        self.assertAlmostEqual(after, 0.55, delta=0.05)
        self.assertTrue(all(new_t[d] >= car_t[d] for d in new_t))  # 加锐方向不降档

    def test_in_range_no_change(self):
        lines, new_t = wt_calc.prescribe(wt_calc.CATEGORY_WEIGHTS["phone"], self.PHONE_T, 0.47)
        self.assertEqual(new_t, self.PHONE_T)
        self.assertIn("已落入目标区间", "\n".join(lines))

    def test_moves_cover_builtin_dims(self):
        for cat, dims in wt_calc.CATEGORY_WEIGHTS.items():
            for d in dims:
                self.assertIn(d, wt_calc.DIM_MOVES, f"{cat}/{d} 缺手法")
                self.assertIn("up", wt_calc.DIM_MOVES[d])
                self.assertIn("down", wt_calc.DIM_MOVES[d])


class TestScoresheet(unittest.TestCase):
    def test_parse_named_and_positional(self):
        a = scoresheet.parse_scores("张力=20,秩序=22,阈值=23,语境=21")
        b = scoresheet.parse_scores("20,22,23,21")
        self.assertEqual(a, b)

    def test_mature_and_short_board(self):
        r = scoresheet.evaluate({"张力": 20, "秩序": 22, "阈值": 23, "语境": 21})
        self.assertTrue(r["mature"])
        self.assertEqual(r["short_boards"], [])
        r2 = scoresheet.evaluate({"张力": 12, "秩序": 22, "阈值": 23, "语境": 21})
        self.assertFalse(r2["mature"])
        self.assertEqual(r2["short_boards"], ["张力"])
        self.assertIn("张力", r2["fixes"])

    def test_total(self):
        r = scoresheet.evaluate({"张力": 25, "秩序": 25, "阈值": 25, "语境": 25})
        self.assertEqual(r["total"], 100.0)


class TestRubric(unittest.TestCase):
    def test_dimensions_aligned_with_weights(self):
        for cat, wts in wt_calc.CATEGORY_WEIGHTS.items():
            self.assertIn(cat, rubric.RUBRICS)
            self.assertEqual(set(wts), set(rubric.RUBRICS[cat]), cat)

    def test_anchor_structure(self):
        for cat, dims in rubric.RUBRICS.items():
            for dim, r in dims.items():
                self.assertTrue(r["look"].strip(), f"{cat}/{dim} 缺观察点")
                self.assertEqual(set(r["anchors"]), {2, 5, 8}, f"{cat}/{dim} 锚点档不全")
                for t, desc in r["anchors"].items():
                    self.assertTrue(desc.strip(), f"{cat}/{dim} t={t} 锚点为空")

    def test_format_rubric(self):
        out = rubric.format_rubric("car", wt_calc.CATEGORY_WEIGHTS["car"])
        self.assertIn("形体曲面动势", out)
        self.assertIn("t=2", out)
        self.assertIn("t=8", out)
        self.assertIn("观察点", out)
        with self.assertRaises(ValueError):
            rubric.format_rubric("watch", {})


class TestReport(unittest.TestCase):
    PHONE_T = {"形状线条": 5, "质感触觉": 4, "色彩": 6, "构图比例": 6, "光影": 3, "细节线条": 4}  # 0.475

    def test_full_report_structure(self):
        md = rp.generate_report(
            "phone", wt_calc.CATEGORY_WEIGHTS["phone"], self.PHONE_T,
            target=0.28, scores={"张力": 20, "秩序": 22, "阈值": 13, "语境": 21},
            name="测试机", date_str="2026-09-13")
        self.assertIn("# BEA 形式诊断报告：测试机", md)
        self.assertIn("W(T) = 0.475", md)
        self.assertIn("均衡典雅", md)
        self.assertIn("## 2 诊断处方", md)          # 偏差超区间 → 出处方
        self.assertIn("## 3 成稿评分卡", md)
        self.assertIn("阈值安全", md)                 # 短板维
        self.assertIn("76/100", md)
        self.assertIn("2026-09-13", md)

    def test_no_target_no_prescription(self):
        md = rp.generate_report(
            "car", wt_calc.CATEGORY_WEIGHTS["car"],
            {"形体曲面动势": 2, "特征线条": 2, "灯组图形": 3, "比例姿态": 2, "材质光影": 3},
            date_str="2026-09-13")
        self.assertNotIn("诊断处方", md)
        self.assertNotIn("评分卡", md)
        self.assertIn("W(T) = 0.230", md)

    def test_in_range_target_no_prescription(self):
        md = rp.generate_report(
            "phone", wt_calc.CATEGORY_WEIGHTS["phone"], self.PHONE_T,
            target=0.47, date_str="2026-09-13")
        self.assertIn("落入区间", md)
        self.assertNotIn("## 2 诊断处方", md)


class TestAnalyzeExperiment(unittest.TestCase):
    VERSIONS = [{"id": "V-low", "wt": 0.10}, {"id": "V-mid", "wt": 0.24}, {"id": "V-high", "wt": 0.45}]

    def _resp(self, design, likes):
        return {"background": {"age": "26-35", "design": design, "city": "二线"},
                "ratings": {vid: {"like": l, "pay": l - 1} for vid, l in likes.items()}}

    def test_verdict_support(self):
        # 窗口内高出 0.8+，且专业组峰值右移 → 支持
        resps = ([self._resp("no", {"V-low": 3, "V-mid": 6, "V-high": 4}) for _ in range(4)] +
                 [self._resp("yes", {"V-low": 3, "V-mid": 5, "V-high": 6}) for _ in range(2)])
        ok, notes = ae.verdict(self.VERSIONS, resps)
        self.assertTrue(ok, notes)

    def test_verdict_reject_when_diff_too_small(self):
        # 窗口内对 V-high 差值 < 0.8 → 不支持
        resps = [self._resp("no", {"V-low": 3, "V-mid": 5, "V-high": 4.5}) for _ in range(6)]
        ok, notes = ae.verdict(self.VERSIONS, resps)
        self.assertFalse(ok)

    def test_stats_and_report(self):
        resps = [self._resp("no", {"V-low": 2, "V-mid": 6, "V-high": 4}) for _ in range(3)]
        s = ae.stats(self.VERSIONS, resps, "like")
        self.assertEqual(s["V-mid"][0], 6.0)
        out = ae.report("测试品类", self.VERSIONS, resps)
        self.assertIn("n=3", out)
        self.assertIn("[盲评数据]", out)


if __name__ == "__main__":
    unittest.main()
