#!/usr/bin/env python3
"""Test option symbol formatting."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from icli.helpers import format_option_symbol


def test_compact_mode():
    """Test compact mode formatting."""
    print("=" * 60)
    print("✅ Testing Compact Mode")
    print("=" * 60)

    # Integer strike
    result = format_option_symbol("AAPL", "20240816", 220.0, "C", "compact")
    expected = "AAPL 0816 C220"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ Integer strike: {result}")

    # Decimal strike
    result = format_option_symbol("AAPL", "20240816", 220.5, "C", "compact")
    expected = "AAPL 0816 C220.5"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ Decimal strike: {result}")

    # Put option
    result = format_option_symbol("SPY", "20241220", 450.0, "P", "compact")
    expected = "SPY 1220 P450"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ Put option: {result}")

    print()


def test_minimal_mode():
    """Test minimal mode formatting."""
    print("=" * 60)
    print("✅ Testing Minimal Mode")
    print("=" * 60)

    # Integer strike
    result = format_option_symbol("AAPL", "20240816", 220.0, "C", "minimal")
    expected = "AAPL24C220"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ Integer strike: {result}")

    # Decimal strike
    result = format_option_symbol("AAPL", "20240816", 220.5, "C", "minimal")
    expected = "AAPL24C220.5"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ Decimal strike: {result}")

    # Long symbol name
    result = format_option_symbol("TSLA", "20250117", 300.0, "P", "minimal")
    expected = "TSLA25P300"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ Long symbol: {result}")

    print()


def test_standard_mode():
    """Test standard mode formatting."""
    print("=" * 60)
    print("✅ Testing Standard Mode")
    print("=" * 60)

    result = format_option_symbol("AAPL", "20240816", 220.0, "C", "standard")
    expected = "AAPL 240816 C220.00"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ Standard format: {result}")

    result = format_option_symbol("SPY", "20241220", 450.5, "P", "standard")
    expected = "SPY 241220 P450.50"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ With decimal: {result}")

    print()


def test_occ_mode():
    """Test OCC mode formatting."""
    print("=" * 60)
    print("✅ Testing OCC Mode")
    print("=" * 60)

    result = format_option_symbol("AAPL", "20240816", 220.0, "C", "occ")
    expected = "AAPL240816C00220000"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ OCC format: {result}")

    result = format_option_symbol("SPY", "20241220", 450.5, "P", "occ")
    expected = "SPY241220P00450500"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ With decimal: {result}")

    # Very high strike
    result = format_option_symbol("AMZN", "20250321", 3500.0, "C", "occ")
    expected = "AMZN250321C03500000"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ High strike: {result}")

    print()


def test_width_comparison():
    """Compare widths across modes."""
    print("=" * 60)
    print("✅ Width Comparison")
    print("=" * 60)

    symbol, date, strike, pc = "AAPL", "20240816", 220.0, "C"

    modes = ["minimal", "compact", "standard", "occ"]
    print(f"\n{'Mode':<12} {'Format':<20} {'Width':<6}")
    print("-" * 40)

    for mode in modes:
        result = format_option_symbol(symbol, date, strike, pc, mode)
        width = len(result)
        print(f"{mode:<12} {result:<20} {width:<6}")

    print()


def test_edge_cases():
    """Test edge cases."""
    print("=" * 60)
    print("✅ Testing Edge Cases")
    print("=" * 60)

    # Very small strike
    result = format_option_symbol("SPY", "20240816", 1.5, "P", "compact")
    expected = "SPY 0816 P1.5"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✓ Small strike: {result}")

    # Fractional strike with multiple decimals
    result = format_option_symbol("GLD", "20241115", 185.25, "C", "compact")
    # Should round to 1 decimal
    assert "185.2" in result or "185.3" in result, f"Unexpected result: {result}"
    print(f"✓ Multiple decimals: {result}")

    # Invalid date (too short)
    result = format_option_symbol("TEST", "240816", 100.0, "C", "compact")
    print(f"✓ Short date handled: {result}")

    print()


def test_real_world_examples():
    """Test real-world option examples."""
    print("=" * 60)
    print("✅ Real-World Examples")
    print("=" * 60)

    examples = [
        # (symbol, date, strike, pc, mode, description)
        ("AAPL", "20240816", 175.0, "C", "minimal", "AAPL near-term call"),
        ("SPY", "20241220", 550.0, "P", "compact", "SPY LEAPS put"),
        ("QQQ", "20240920", 380.0, "C", "compact", "QQQ quarterly call"),
        ("TSLA", "20250117", 250.5, "P", "compact", "TSLA fractional strike"),
        ("/ES", "20240913", 5500.0, "C", "compact", "ES future option"),
    ]

    print(f"\n{'Description':<25} {'Mode':<10} {'Result':<25}")
    print("-" * 65)

    for symbol, date, strike, pc, mode, desc in examples:
        result = format_option_symbol(symbol, date, strike, pc, mode)
        print(f"{desc:<25} {mode:<10} {result:<25}")

    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 Option Symbol Formatting Tests")
    print("=" * 60 + "\n")

    try:
        test_compact_mode()
        test_minimal_mode()
        test_standard_mode()
        test_occ_mode()
        test_width_comparison()
        test_edge_cases()
        test_real_world_examples()

        print("=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
        print()

        # Show recommended OCC format for positions and quotes
        print("=" * 60)
        print("📋 OCC Format (Recommended for Positions & Quotes)")
        print("=" * 60)
        print("\nStandard format: SYMBOL + YYMMDD + C/P + STRIKE(8 digits)")
        print("\nExamples:")
        occ_examples = [
            ("AAPL", "20240816", 220.0, "C", "Stock call"),
            ("SPY", "20241220", 450.0, "P", "ETF put"),
            ("TSLA", "20250117", 250.5, "P", "Fractional strike"),
            ("/ES", "20240913", 5500.0, "C", "Future option"),
        ]
        for symbol, date, strike, pc, desc in occ_examples:
            result = format_option_symbol(symbol, date, strike, pc, "occ")
            print(f"  {desc:20s}: {result}")
        print()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
