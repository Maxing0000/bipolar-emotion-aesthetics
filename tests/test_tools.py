"""BEA 工具链单元测试：wt_calc 与 scoresheet。"""
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "bipolar-emotion-aesthetics", "scripts"))

import scoresheet  # noqa: E402
import wt_calc  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
