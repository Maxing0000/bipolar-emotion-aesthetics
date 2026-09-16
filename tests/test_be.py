"""BEA 自测试套件（从 bea_quant.py 拆出，单一职责）

运行方式：
    python3 scripts/bea_quant.py test     # 引擎 test 子命令会委托到这里
    python3 tests/test_be.py              # 直接运行

依赖：仅标准库；引擎通过 importlib 从 scripts/bea_quant.py 动态加载。

注：引擎符号在运行时注入全局（globals().update），静态分析器会误报 undefined name，
因此 pyflakes 只检查 scripts/，本文件由 CI 的"全量自测"步骤实际执行验证。
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.join(os.path.dirname(_HERE), "scripts")
_ENGINE = os.path.join(_SCRIPTS, "bea_quant.py")

if not os.path.exists(_ENGINE):
    print(f"✗ 未找到引擎文件：{_ENGINE}")
    sys.exit(1)

import importlib.util
_spec = importlib.util.spec_from_file_location("bea_quant", _ENGINE)
_bq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bq)
sys.modules["bea_quant"] = _bq
# 将引擎的全部公开符号注入全局，使测试体可以裸名调用（与拆分前行为一致）
globals().update({k: v for k, v in vars(_bq).items() if not k.startswith("__") or k == "__version__"})


def run_tests() -> bool:
    passed = 0
    failed = 0

    def check(name: str, condition: bool):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}")

    print("运行 BEA 量化引擎自测试...")

    dims = {"形状": 5, "质感": 5, "色彩": 5, "构图": 5, "光影": 5, "细节": 5}
    check("全5分 W(T)=0.5", abs(compute_w_t(dims, CATEGORY_WEIGHTS["phone"]) - 0.5) < 0.001)

    dims = {"形状": 0, "质感": 0, "色彩": 0, "构图": 0, "光影": 0, "细节": 0}
    check("全0分 W(T)=0.0", abs(compute_w_t(dims, CATEGORY_WEIGHTS["phone"]) - 0.0) < 0.001)

    dims = {"形状": 10, "质感": 10, "色彩": 10, "构图": 10, "光影": 10, "细节": 10}
    check("全10分 W(T)=1.0", abs(compute_w_t(dims, CATEGORY_WEIGHTS["phone"]) - 1.0) < 0.001)

    name, _, _ = locate_paradigm(0.4)
    check("W(T)=0.4 定位均衡典雅", name == "均衡典雅")
    name, _, _ = locate_paradigm(0.1)
    check("W(T)=0.1 定位治愈松弛", name == "治愈松弛")
    name, _, _ = locate_paradigm(0.7)
    check("W(T)=0.7 定位先锋反叛", name == "先锋反叛")

    dims = {"形状": 2, "质感": 2, "色彩": 2, "构图": 2, "光影": 2, "细节": 2}
    check("低W(T)全低分诊断甜腻症", any(d["name"] == "甜腻症" for d in diagnose_diseases(0.12, dims)))

    dims = {"形状": 8, "质感": 8, "色彩": 7, "构图": 7, "光影": 8, "细节": 8}
    check("高W(T)全高分诊断刺激疲劳", any(d["name"] == "刺激疲劳" for d in diagnose_diseases(0.76, dims)))
    check("刺激疲劳覆盖攻击症", not any(d["name"] == "攻击症" for d in diagnose_diseases(0.76, dims)))

    dims = {"形状": 7, "质感": 7, "色彩": 7, "构图": 3, "光影": 3, "细节": 3}
    check("三个>=6维度诊断重点通胀症", any(d["name"] == "重点通胀症" for d in diagnose_diseases(0.5, dims)))

    try:
        a = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
        check("完整分析不报错", a.w_t > 0 and a.paradigm != "")
    except Exception as e:
        check(f"完整分析不报错（异常: {e}）", False)

    try:
        parse_t_values("形状=3", ["形状", "质感"])
        check("缺少维度应报错", False)
    except ValueError:
        check("缺少维度应报错", True)

    try:
        parse_t_values("形状=15", ["形状"])
        check("超出范围应报错", False)
    except ValueError:
        check("超出范围应报错", True)

    try:
        parse_t_values("形状=abc", ["形状"])
        check("非整数应报错", False)
    except ValueError:
        check("非整数应报错", True)

    # 紧凑格式解析
    name, dims = parse_compact_values("Test=3,6,4,3,5,6", "phone")
    check("紧凑格式解析", name == "Test" and dims["形状"] == 3 and dims["细节"] == 6)

    # 完整格式解析（在 compare/batch 条目中）
    name, dims = parse_compact_values("Test=形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6", "phone")
    check("完整格式解析", name == "Test" and dims["形状"] == 3 and dims["质感"] == 6)

    # 紧凑格式数字数量不对
    try:
        parse_compact_values("Test=3,6,4", "phone")
        check("紧凑格式数量不对应报错", False)
    except ValueError as e:
        check("紧凑格式数量不对应报错", "需要" in str(e))

    for cat, ws in CATEGORY_WEIGHTS.items():
        check(f"品类 {cat} 权重和为1", abs(sum(ws.values()) - 1.0) < 0.001)

    # 均分症：极差>=2时不诊断（即使都在3-5区间）
    dims = {"形状": 3, "质感": 3, "色彩": 5, "构图": 5, "光影": 3, "细节": 5}
    diseases = diagnose_diseases(0.4, dims)
    check("均分症：极差>=2不诊断", not any(d["name"] == "均分症" for d in diseases))

    # 均分症：极差<2且都在3-5时诊断
    dims = {"形状": 4, "质感": 4, "色彩": 4, "构图": 4, "光影": 4, "细节": 4}
    diseases = diagnose_diseases(0.4, dims)
    check("均分症：极差<2诊断", any(d["name"] == "均分症" for d in diseases))

    # 甜腻症触发时不重复触发张力不足症
    dims = {"形状": 2, "质感": 2, "色彩": 2, "构图": 2, "光影": 2, "细节": 2}
    diseases = diagnose_diseases(0.12, dims)
    check("甜腻症触发时不重复张力不足症",
          any(d["name"] == "甜腻症" for d in diseases)
          and not any(d["name"] == "张力不足症" for d in diseases))

    # resolve_target：范式名
    wt, desc = resolve_target("崇高震撼")
    check("resolve_target 范式名", abs(wt - 0.54) < 0.01 and "崇高" in desc)

    # resolve_target：数字
    wt, desc = resolve_target("0.55")
    check("resolve_target 数字", abs(wt - 0.55) < 0.001)

    # suggest_adjustment：提升危极
    a = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
    steps, verification = suggest_adjustment(a, 0.55)
    check("suggest_adjustment 提升危极有输出", len(steps) > 0 and all("dimension" in s for s in steps))
    check("suggest_adjustment 包含验证信息", verification is not None and "actual_wt" in verification)

    # suggest_adjustment：无需调整
    steps, verification = suggest_adjustment(a, a.w_t)
    check("suggest_adjustment 无需调整", len(steps) == 1 and "message" in steps[0])

    # suggest 降低危极时优先降高t值维度
    a = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
    steps, _ = suggest_adjustment(a, 0.2)
    dim_steps = [s["dimension"] for s in steps if "dimension" in s]
    check("suggest降低危极优先降高t值", dim_steps and dim_steps[0] in ("质感", "细节"))

    # suggest 提升危极时优先升低t值维度
    steps, _ = suggest_adjustment(a, 0.6)
    dim_steps = [s["dimension"] for s in steps if "dimension" in s]
    check("suggest提升危极优先升高权重低t值", dim_steps and dim_steps[0] == "形状")

    # 攻击症新条件：W(T)>=0.55 且有维度>=6
    dims = {"形状": 6, "质感": 6, "色彩": 6, "构图": 6, "光影": 6, "细节": 6}
    wt = compute_w_t(dims, CATEGORY_WEIGHTS["phone"])
    diseases = diagnose_diseases(wt, dims)
    check("全6分诊断攻击症", any(d["name"] == "攻击症" for d in diseases))
    check("全6分诊断重点通胀症", any(d["name"] == "重点通胀症" for d in diseases))

    # 攻击症边界：W(T)<0.55 即使有维度>=6也不诊断
    dims = {"形状": 6, "质感": 5, "色彩": 5, "构图": 5, "光影": 5, "细节": 5}
    wt = compute_w_t(dims, CATEGORY_WEIGHTS["phone"])
    diseases = diagnose_diseases(wt, dims)
    check("W(T)<0.55不诊断攻击症", not any(d["name"] == "攻击症" for d in diseases))

    # 四维评分范围测试
    a = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
    scores = a.score_suggestion
    check("四维评分各维度在0-25范围", all(0 <= scores[k] <= 25 for k in ["双极张力", "结构秩序", "阈值安全", "语境适配"]))
    total = sum(scores[k] for k in ["双极张力", "结构秩序", "阈值安全", "语境适配"])
    check("四维评分总分在0-100范围", 0 <= total <= 100)
    check("四维评分包含评分明细", "评分明细" in scores)

    # 范式边界值测试
    name, _, _ = locate_paradigm(0.15)
    check("W(T)=0.15定位亲和精致", name == "亲和精致")
    name, _, _ = locate_paradigm(0.30)
    check("W(T)=0.30定位均衡典雅", name == "均衡典雅")
    name, _, _ = locate_paradigm(0.48)
    check("W(T)=0.48定位崇高震撼", name == "崇高震撼")
    name, _, _ = locate_paradigm(0.60)
    check("W(T)=0.60定位冷峻克制", name == "冷峻克制")
    name, _, _ = locate_paradigm(0.66)
    check("W(T)=0.66定位先锋反叛", name == "先锋反叛")

    # compare/batch 命令不报错（通过函数调用测试）
    try:
        name1, dims1 = parse_compact_values("A=3,6,4,3,5,6", "phone")
        name2, dims2 = parse_compact_values("B=形状=4,质感=4,色彩=4,构图=3,光影=3,细节=5", "phone")
        check("compare解析两种格式", name1 == "A" and name2 == "B" and dims1["形状"] == 3 and dims2["质感"] == 4)
    except Exception as e:
        check(f"compare解析失败({e})", False)

    # batch 多产品解析
    try:
        items = "A=3,6,4,3,5,6;B=形状=4,质感=4,色彩=4,构图=3,光影=3,细节=5;C=5,5,5,5,5,5"
        results = []
        for item in items.split(";"):
            name, dims = parse_compact_values(item.strip(), "phone")
            results.append((name, dims))
        check("batch解析3个产品", len(results) == 3 and results[0][0] == "A" and results[2][0] == "C")
    except Exception as e:
        check(f"batch解析失败({e})", False)

    # 灵敏度分析测试
    a = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
    sens = sensitivity_analysis(a)
    check("灵敏度分析返回所有维度", len(sens) == len(a.dimensions))
    check("灵敏度分析按灵敏度降序排列", all(sens[i]["sensitivity"] >= sens[i+1]["sensitivity"] for i in range(len(sens)-1)))
    check("灵敏度分析包含必要字段", all("wt_plus_1" in r and "wt_minus_1" in r and "sensitivity" in r for r in sens))
    check("灵敏度分析包含分项灵敏度", all("wt_sensitivity" in r and "score_sensitivity" in r for r in sens))
    # W(T)灵敏度最高的维度应该是权重最高的维度（形状/质感 0.25）
    top_wt_sens = max(sens, key=lambda x: x["wt_sensitivity"])["dimension"]
    check("W(T)灵敏度最高为高权重维度", top_wt_sens in ("形状", "质感"))

    # 灵敏度分析带目标
    sens_target = sensitivity_analysis(a, target_wt=0.2)
    check("灵敏度分析带目标包含toward_target", all(r["toward_target"] is not None for r in sens_target))
    # 降低危极时，朝目标方向（t-1）的W(T)变化量与权重成正比，权重最高的维度效果最好
    toward_sorted = sorted([r for r in sens_target if r["toward_target"] > 0], key=lambda x: x["toward_target"], reverse=True)
    if toward_sorted:
        check("朝目标方向最有效的是高权重维度", toward_sorted[0]["weight"] >= 0.25)

    # 灵敏度分析边界值：t=9 时 t+1 应该为0
    a_edge = analyze("phone", "形状=9,质感=9,色彩=9,构图=9,光影=9,细节=9")
    sens_edge = sensitivity_analysis(a_edge)
    check("t=9时t+1变化为0", all(r["wt_plus_1"] == 0 for r in sens_edge))
    # t=1 时 t-1 应该为0
    a_edge2 = analyze("phone", "形状=1,质感=1,色彩=1,构图=1,光影=1,细节=1")
    sens_edge2 = sensitivity_analysis(a_edge2)
    check("t=1时t-1变化为0", all(r["wt_minus_1"] == 0 for r in sens_edge2))

    # 主辅比测试
    a_pr1 = analyze("car", "曲面=2,特征线=3,灯组=4,比例=3,材质=4")
    pr1 = a_pr1.polarity_ratio
    check("主辅比包含必要字段", all(k in pr1 for k in ["plus_ratio", "minus_ratio", "dominant", "primary_secondary_ratio", "is_balanced"]))
    check("亲极主导时dominant正确", pr1["dominant"] == "亲极 P+")
    check("主辅比格式正确", ":" in pr1["primary_secondary_ratio"])

    a_pr2 = analyze("car", "曲面=8,特征线=9,灯组=7,比例=8,材质=7")
    pr2 = a_pr2.polarity_ratio
    check("危极主导时dominant正确", pr2["dominant"] == "危极 T−")

    a_pr3 = analyze("car", "曲面=5,特征线=5,灯组=5,比例=5,材质=5")
    pr3 = a_pr3.polarity_ratio
    # 软划分下 t=5 有 50% 危极隶属度，所以危极主导且主辅比平衡
    check("全t=5时危极主导（软划分）", pr3["dominant"] == "危极 T−")
    check("全t=5时is_balanced为True（软划分）", pr3["is_balanced"] == True)

    # 耐看性测试
    a_end = analyze("car", "曲面=4,特征线=5,灯组=6,比例=3,材质=5")
    end = a_end.endurance
    check("耐看性包含必要字段", all(k in end for k in ["score", "level", "factors", "advice"]))
    check("耐看性分数在0-100范围", 0 <= end["score"] <= 100)
    check("耐看性评级有效", end["level"] in ["极耐看", "耐看", "一般", "易疲劳"])
    check("耐看性包含4个因素", len(end["factors"]) == 4)

    # 高W(T)耐看性应较低
    a_end_high = analyze("car", "曲面=9,特征线=9,灯组=8,比例=8,材质=8")
    check("高W(T)耐看性低于中等W(T)", a_end_high.endurance["score"] < a_end.endurance["score"])

    # 语境适配评分测试
    ctx = a.score_suggestion["评分明细"]["语境适配"]
    check("语境适配包含品类基准分", "品类基准分" in ctx)
    check("语境适配包含范式调整", "范式调整" in ctx)
    check("语境适配包含状态说明", "状态" in ctx)

    # 灵敏度 step=2 测试
    a_sen2 = analyze("car", "曲面=4,特征线=5,灯组=6,比例=3,材质=5")
    sens2 = sensitivity_analysis(a_sen2, step=2)
    check("灵敏度step=2返回所有维度", len(sens2) == len(a_sen2.dimensions))
    check("灵敏度step=2包含step字段", all("step" in r for r in sens2))
    check("灵敏度step=2的step值为2", all(r["step"] == 2 for r in sens2))
    check("灵敏度step=2的wt变化是step=1的2倍", abs(sens2[0]["wt_plus"]) == abs(sensitivity_analysis(a_sen2, step=1)[0]["wt_plus"]) * 2)

    # 多组分析测试
    groups = [
        {"name": "宏观外形", "dimensions": {"曲面": 3, "特征线": 4, "灯组": 5, "比例": 3, "材质": 4}},
        {"name": "微观细节", "dimensions": {"曲面": 6, "特征线": 7, "灯组": 8, "比例": 5, "材质": 6}},
    ]
    mg = multigroup_analysis("car", groups)
    check("多组分析包含必要字段", all(k in mg for k in ["groups", "cross_modal_consistency", "hierarchy", "overall"]))
    check("多组分析返回2组", len(mg["groups"]) == 2)
    check("多组分析识别层级嵌套", mg["hierarchy"] is not None)
    check("多组分析识别微差补偿", "微差补偿" in mg["hierarchy"]["type"])

    # 风格周期律测试
    sc = style_cycle_analysis("car", 0.55)
    check("风格周期律包含必要字段", all(k in sc for k in ["percentile", "position", "advice", "trend_direction"]))
    check("风格周期律百分位在0-100", 0 <= sc["percentile"] <= 100)
    check("风格周期律W(T)=0.55为领先", "领先" in sc["position"])

    sc_mainstream = style_cycle_analysis("car", 0.40)
    check("风格周期律W(T)=0.40为主流", "主流" in sc_mainstream["position"])

    # 自定义权重测试
    custom_weights = {"曲面": 0.4, "特征线": 0.3, "灯组": 0.1, "比例": 0.1, "材质": 0.1}
    a_custom = analyze("car", "曲面=5,特征线=5,灯组=5,比例=5,材质=5", custom_weights)
    check("自定义权重生效", a_custom.weights == custom_weights)
    check("自定义权重W(T)=0.5", abs(a_custom.w_t - 0.5) < 0.001)

    # resolve_weights 优先级测试
    check("resolve_weights默认使用品类权重", resolve_weights("car") == CATEGORY_WEIGHTS["car"])
    check("resolve_weights支持自定义权重", resolve_weights("car", weights_str=json.dumps(custom_weights)) == custom_weights)

    # JSON 输出字段完整性测试
    a_json = analyze("car", "曲面=4,特征线=5,灯组=6,比例=3,材质=5")
    d = a_json.to_dict()
    check("JSON包含polarity_ratio", "polarity_ratio" in d)
    check("JSON包含endurance", "endurance" in d)
    check("JSON包含所有维度", set(d["dimensions"].keys()) == set(CATEGORY_WEIGHTS["car"].keys()))

    # building 品类测试
    a_building = analyze("building", "形体轮廓=5,立面线条=6,比例尺度=4,材质肌理=5,光影空间=3")
    check("building品类分析不报错", a_building.w_t > 0)
    check("building品类有5个维度", len(a_building.dimensions) == 5)

    # 主辅比 is_balanced 修复验证（v2.4.1）
    a_all_plus = analyze("car", "曲面=1,特征线=1,灯组=1,比例=1,材质=1")
    check("全亲极is_balanced为False（从属极不足）", a_all_plus.polarity_ratio["is_balanced"] == False)
    check("全亲极has_subordinate为False", a_all_plus.polarity_ratio["has_subordinate"] == False)

    a_all_minus = analyze("car", "曲面=9,特征线=9,灯组=9,比例=9,材质=9")
    check("全危极is_balanced为False（从属极不足）", a_all_minus.polarity_ratio["is_balanced"] == False)

    a_balanced = analyze("car", "曲面=2,特征线=3,灯组=4,比例=3,材质=4")
    check("正常配比is_balanced为True", a_balanced.polarity_ratio["is_balanced"] == True)

    # t=10 越阈值测试
    a_extreme = analyze("car", "曲面=10,特征线=5,灯组=5,比例=5,材质=5")
    check("t=10被接受（用于分析越阈值）", a_extreme.dimensions["曲面"] == 10)
    check("t=10时W(T)包含该维度", a_extreme.w_t > 0)

    # 版本号一致性：引擎 __version__ == manifest.json 版本 == 头注释版本
    engine_ver = __version__
    header_ver = None
    with open(_ENGINE, encoding="utf-8") as f_self:  # 引擎头注释（拆分后 __file__ 指向本测试文件）
        for line in f_self:
            if "量化引擎 v" in line:
                header_ver = line.split("量化引擎 v")[1].split()[0].strip()
                break
    manifest_path = os.path.join(os.path.dirname(_SCRIPTS), "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as f_manifest:
            manifest_ver = json.load(f_manifest)["version"]
        check(f"引擎版本号({engine_ver})与manifest.json({manifest_ver})一致", engine_ver == manifest_ver)
        check(f"头注释版本号({header_ver})与 __version__({engine_ver})一致", header_ver == engine_ver)
    else:
        check("manifest.json 存在", False)

    # 新病症测试（v2.4.1）
    a_instinct = analyze("car", "曲面=10,特征线=5,灯组=5,比例=5,材质=5")
    check("t=10诊断本能越界", any(d["name"] == "本能越界" for d in a_instinct.diseases))
    check("本能越界时阈值安全为0", a_instinct.score_suggestion["阈值安全"] == 0)

    a_fatigue = analyze("car", "曲面=8,特征线=8,灯组=7,比例=7,材质=8")
    check("全维度>=7且W(T)>=0.65诊断刺激疲劳", any(d["name"] == "刺激疲劳" for d in a_fatigue.diseases))

    # 调整建议策略测试
    a_sug = analyze("car", "曲面=7,特征线=7,灯组=6,比例=6,材质=7")
    steps_focused, _ = suggest_adjustment(a_sug, 0.30, strategy="focused")
    steps_distributed, _ = suggest_adjustment(a_sug, 0.30, strategy="distributed")
    check("集中策略调整维度数<=分散策略", len(steps_focused) <= len(steps_distributed))
    check("两种策略都能达到目标", len(steps_focused) > 0 and len(steps_distributed) > 0)

    # 灵敏度分项测试
    a_sen2 = analyze("car", "曲面=4,特征线=5,灯组=6,比例=3,材质=5")
    sens2 = sensitivity_analysis(a_sen2)
    check("灵敏度包含wt_sensitivity", all("wt_sensitivity" in r for r in sens2))
    check("灵敏度包含score_sensitivity", all("score_sensitivity" in r for r in sens2))

    # 美感生成测试（v2.5.0）
    gen = generate_design("phone", 0.30, strategy="balanced")
    check("美感生成返回维度配置", len(gen["dimensions"]) == 6)
    check("美感生成W(T)接近目标", abs(gen["w_t"] - 0.30) <= 0.05)
    check("美感生成所有t在1-9", all(1 <= v <= 9 for v in gen["dimensions"].values()))

    gen_focused = generate_design("car", 0.50, strategy="focused")
    check("集中策略生成W(T)接近目标", abs(gen_focused["w_t"] - 0.50) <= 0.05)

    gen_distributed = generate_design("brand", 0.35, strategy="distributed")
    check("分散策略生成W(T)接近目标", abs(gen_distributed["w_t"] - 0.35) <= 0.05)

    # 报告格式化回归测试（v2.7.1）：有病症时 markdown 报告不得再报 KeyError
    a_dis = analyze("building", "形体轮廓=8,立面线条=7,比例尺度=6,材质肌理=5,光影空间=6")
    check("该用例确实触发病症", len(a_dis.diseases) > 0)
    md_with_diseases = format_report_markdown(a_dis)
    check("markdown报告(有病症)可生成", "病症诊断" in md_with_diseases and "证据" in md_with_diseases)
    a_clean = analyze("phone", "形状=3,质感=6,色彩=4,构图=3,光影=5,细节=6")
    check("markdown报告(无病症)可生成", "无明显病症" in format_report_markdown(a_clean))
    check("对比报告可生成", "BEA 对比报告" in format_compare(a_dis, a_clean, "甲", "乙"))

    print(f"\n结果：{passed} 通过，{failed} 失败")
    return failed == 0



if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
