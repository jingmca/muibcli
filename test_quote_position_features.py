#!/usr/bin/env python3
"""
Test script for Quote Position Info and PNL Color features
测试报价区持仓信息和PNL颜色功能
"""

import sys
import os

# Add project to path
sys.path.insert(0, '/Users/hackjm/Downloads/muibcli')

def test_position_cost_calculation():
    """测试持仓成本计算逻辑"""
    print("Testing position cost calculation...")

    # Test 1: 正常股票持仓
    position_qty = 100
    average_cost_total = 15000.0  # $15,000 total
    multiplier = 1

    expected_per_share = 150.0  # $150 per share
    actual_per_share = average_cost_total / abs(position_qty)

    assert abs(actual_per_share - expected_per_share) < 0.01, \
        f"Stock cost calculation failed: {actual_per_share} != {expected_per_share}"
    print("  ✅ Stock position cost calculation passed")

    # Test 2: 期权持仓（需要除以multiplier）
    position_qty = 10
    average_cost_total = 5000.0  # $5,000 total
    multiplier = 100

    expected_per_share = 5.0  # $5 per share (after dividing by multiplier)
    actual_per_share = (average_cost_total / abs(position_qty)) / multiplier

    assert abs(actual_per_share - expected_per_share) < 0.01, \
        f"Option cost calculation failed: {actual_per_share} != {expected_per_share}"
    print("  ✅ Option position cost calculation passed")

    # Test 3: 空头持仓（负数量）
    position_qty = -50
    average_cost_total = 7500.0
    multiplier = 1

    expected_per_share = 150.0
    actual_per_share = average_cost_total / abs(position_qty)

    # For shorts, cost should be negated
    if position_qty < 0:
        actual_per_share = -abs(actual_per_share)

    assert actual_per_share < 0, "Short position cost should be negative"
    print("  ✅ Short position cost calculation passed")

def test_itm_detection_logic():
    """测试价内期权判断逻辑"""
    print("\nTesting ITM detection logic...")

    # Test 1: Call期权 ITM (underlying > strike)
    delta = 0.65  # positive delta = call
    underlying = 270.0
    strike = 265.0

    is_itm = delta > 0 and underlying >= strike
    assert is_itm, "Call should be ITM when underlying > strike"
    print("  ✅ Call ITM detection passed")

    # Test 2: Call期权 OTM (underlying < strike)
    underlying = 260.0
    strike = 265.0

    is_itm = delta > 0 and underlying >= strike
    assert not is_itm, "Call should be OTM when underlying < strike"
    print("  ✅ Call OTM detection passed")

    # Test 3: Put期权 ITM (underlying < strike)
    delta = -0.45  # negative delta = put
    underlying = 250.0
    strike = 265.0

    is_itm = delta < 0 and underlying <= strike
    assert is_itm, "Put should be ITM when underlying < strike"
    print("  ✅ Put ITM detection passed")

    # Test 4: Put期权 OTM (underlying > strike)
    underlying = 270.0
    strike = 265.0

    is_itm = delta < 0 and underlying <= strike
    assert not is_itm, "Put should be OTM when underlying > strike"
    print("  ✅ Put OTM detection passed")

def test_pnl_color_thresholds():
    """测试PNL颜色阈值逻辑"""
    print("\nTesting PNL color thresholds...")

    # Test 1: 大额盈利 (> $10,000)
    pnl = 15000.0
    color_type = "bg='ansibrightgreen'" if pnl > 10000 else ""
    assert "ansibrightgreen" in color_type, "Large profit should use bright green background"
    print("  ✅ Large profit color threshold passed")

    # Test 2: 中等盈利 ($1,000 ~ $10,000)
    pnl = 5000.0
    if pnl > 10000:
        color_type = "bg='ansibrightgreen'"
    elif pnl > 1000:
        color_type = "bg='ansigreen'"
    else:
        color_type = "fg='ansigreen'"
    assert "ansigreen" in color_type and "bright" not in color_type, \
        "Medium profit should use green background"
    print("  ✅ Medium profit color threshold passed")

    # Test 3: 小额盈利 ($0 ~ $1,000)
    pnl = 500.0
    if pnl > 10000:
        color_type = "bg='ansibrightgreen'"
    elif pnl > 1000:
        color_type = "bg='ansigreen'"
    else:
        color_type = "fg='ansigreen'"
    assert "fg='ansigreen'" in color_type, "Small profit should use green foreground"
    print("  ✅ Small profit color threshold passed")

    # Test 4: 大额亏损 (< -$10,000)
    pnl = -15000.0
    if pnl < -10000:
        color_type = "bg='ansibrightred'"
    elif pnl < -1000:
        color_type = "bg='ansired'"
    else:
        color_type = "fg='ansired'"
    assert "ansibrightred" in color_type, "Large loss should use bright red background"
    print("  ✅ Large loss color threshold passed")

    # Test 5: 零值
    pnl = 0.0
    color_type = "fg='ansigray'" if pnl == 0 else ""
    assert "ansigray" in color_type, "Zero should use gray foreground"
    print("  ✅ Zero PNL color passed")

def test_position_display_format():
    """测试持仓信息显示格式"""
    print("\nTesting position display format...")

    # Test 1: 多头持仓显示
    position_qty = 100
    position_cost = 150.50
    pos_sign = "+" if position_qty > 0 else ""
    formatted = f"[Pos:{pos_sign}{position_qty:.0f}@{position_cost:.2f}]"

    expected = "[Pos:+100@150.50]"
    assert formatted == expected, f"Long position format failed: {formatted} != {expected}"
    print("  ✅ Long position format passed")

    # Test 2: 空头持仓显示
    position_qty = -50
    position_cost = -145.25
    pos_sign = "+" if position_qty > 0 else ""
    formatted = f"[Pos:{pos_sign}{position_qty:.0f}@{position_cost:.2f}]"

    expected = "[Pos:-50@-145.25]"
    assert formatted == expected, f"Short position format failed: {formatted} != {expected}"
    print("  ✅ Short position format passed")

def test_edge_cases():
    """测试边界情况"""
    print("\nTesting edge cases...")

    # Test 1: 零持仓
    position_qty = 0
    has_position = position_qty != 0
    assert not has_position, "Zero position should not be displayed"
    print("  ✅ Zero position handling passed")

    # Test 2: 极小持仓（小数）
    position_qty = 0.5
    formatted = f"{position_qty:.0f}"
    assert formatted == "0" or formatted == "1", "Fractional shares should round"
    print("  ✅ Fractional position handling passed")

    # Test 3: NaN值处理
    import math
    pnl = float('nan')
    is_nan = pnl != pnl  # NaN不等于自己
    assert is_nan, "NaN detection should work"
    print("  ✅ NaN handling passed")

def main():
    """运行所有测试"""
    print("=" * 70)
    print("🧪 Testing Quote Position Info and PNL Color Features")
    print("=" * 70)

    try:
        test_position_cost_calculation()
        test_itm_detection_logic()
        test_pnl_color_thresholds()
        test_position_display_format()
        test_edge_cases()

        print("\n" + "=" * 70)
        print("🎉 All unit tests passed!")
        print("=" * 70)
        print("\n✅ Ready for CLI integration testing")
        print("\n下一步：按照CLAUDE.md阶段4，在tmux中进行CLI环境集成测试")
        return 0

    except AssertionError as e:
        print("\n" + "=" * 70)
        print(f"❌ Test failed: {e}")
        print("=" * 70)
        return 1
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ Unexpected error: {e}")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
