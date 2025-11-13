#!/usr/bin/env python3
"""Test display configuration system."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from icli.display_config import (
    display_config,
    get_available_presets,
    validate_columns,
)

def test_presets():
    """Test preset configurations."""
    print("=" * 60)
    print("✅ Testing presets...")
    print("=" * 60)

    # Test minimal preset (updated to match new POSITION_PRESETS)
    cols = display_config.get_position_columns(override_preset="minimal")
    expected_minimal = ["sym", "position", "averageCost", "marketPrice", "unrealizedPNL", "%"]
    assert cols == expected_minimal, f"Expected {expected_minimal}, got {cols}"
    print(f"✓ minimal: {cols}")

    # Test compact preset (updated: removed 'type' column, now 8 columns)
    cols = display_config.get_position_columns(override_preset="compact")
    assert len(cols) == 8, f"Expected 8 columns in compact, got {len(cols)}"
    print(f"✓ compact: {cols}")

    # Test trading preset (updated: 9 columns)
    cols = display_config.get_position_columns(override_preset="trading")
    assert len(cols) == 9, f"Expected 9 columns in trading, got {len(cols)}"
    print(f"✓ trading: {cols}")

    # Test full preset
    cols = display_config.get_position_columns(override_preset="full")
    assert cols is None, "Full preset should return None (all columns)"
    print(f"✓ full: All columns (None)")

    print()

def test_custom_columns():
    """Test custom column specification."""
    print("=" * 60)
    print("✅ Testing custom columns...")
    print("=" * 60)

    custom = ["type", "sym", "position", "unrealizedPNL"]
    cols = display_config.get_position_columns(override_columns=custom)
    assert cols == custom, f"Expected {custom}, got {cols}"
    print(f"✓ custom columns: {cols}")

    print()

def test_column_aliases():
    """Test column name aliases."""
    print("=" * 60)
    print("✅ Testing column aliases...")
    print("=" * 60)

    # Use aliases
    custom = ["type", "sym", "position", "PNL", "mktPrice", "avgCost"]
    cols = display_config.get_position_columns(override_columns=custom)

    # Check aliases are resolved
    assert "marketPrice" in cols, f"marketPrice not found in {cols}"
    assert "averageCost" in cols, f"averageCost not found in {cols}"
    assert "unrealizedPNL" in cols, f"unrealizedPNL not found in {cols}"
    print(f"✓ aliased columns: {cols}")

    print()

def test_auto_width():
    """Test automatic width detection."""
    print("=" * 60)
    print("✅ Testing auto width detection...")
    print("=" * 60)

    # Save original settings
    orig_preset = display_config.position_preset
    orig_auto = display_config.position_auto_width

    # Enable auto mode
    display_config.position_preset = "auto"
    display_config.position_auto_width = True

    # Narrow terminal
    cols_narrow = display_config.get_position_columns(current_terminal_width=80)
    print(f"✓ 80 cols (narrow): {len(cols_narrow) if cols_narrow else 'all'} fields → {cols_narrow[:3] if cols_narrow else 'all'}...")

    # Wide terminal
    cols_wide = display_config.get_position_columns(current_terminal_width=200)
    print(f"✓ 200 cols (wide): {len(cols_wide) if cols_wide else 'all'} fields")

    # Restore settings
    display_config.position_preset = orig_preset
    display_config.position_auto_width = orig_auto

    print()

def test_validation():
    """Test column validation."""
    print("=" * 60)
    print("✅ Testing column validation...")
    print("=" * 60)

    # Valid columns
    valid, invalid = validate_columns(["type", "sym", "PNL", "mktPrice"])
    assert valid, "Valid columns should pass validation"
    print(f"✓ Valid columns: passed (no invalid columns)")

    # Invalid columns
    valid, invalid = validate_columns(["type", "sym", "INVALID", "BADCOL"])
    assert not valid, "Invalid columns should fail validation"
    assert "INVALID" in invalid, "INVALID should be in invalid list"
    assert "BADCOL" in invalid, "BADCOL should be in invalid list"
    print(f"✓ Invalid columns detected: {invalid}")

    print()

def test_set_operations():
    """Test set operations."""
    print("=" * 60)
    print("✅ Testing set operations...")
    print("=" * 60)

    # Save original
    orig_preset = display_config.position_preset

    # Test set preset
    result = display_config.set_position_preset("minimal")
    assert result, "Should be able to set valid preset"
    assert display_config.position_preset == "minimal"
    print(f"✓ Set preset to 'minimal'")

    # Test invalid preset
    result = display_config.set_position_preset("INVALID")
    assert not result, "Should reject invalid preset"
    print(f"✓ Rejected invalid preset")

    # Test set columns
    display_config.set_position_columns("type,sym,PNL,%")
    assert display_config.position_columns == ["type", "sym", "PNL", "%"]
    print(f"✓ Set custom columns: {display_config.position_columns}")

    # Restore
    display_config.position_preset = orig_preset
    display_config.position_columns = None

    print()

def test_all_presets():
    """Test all available presets."""
    print("=" * 60)
    print("✅ Testing all available presets...")
    print("=" * 60)

    presets = get_available_presets("position")
    for name, cols in presets.items():
        result = display_config.get_position_columns(override_preset=name)
        col_count = len(result) if result else "all"
        col_count_str = str(col_count)
        print(f"✓ {name:12s}: {col_count_str:>4s} columns")

    print()

def test_priority_order():
    """Test priority order: override_columns > override_preset > config."""
    print("=" * 60)
    print("✅ Testing priority order...")
    print("=" * 60)

    # Set config
    display_config.position_preset = "compact"
    display_config.position_columns = None

    # Test: config only (updated: compact is 8 columns now)
    cols = display_config.get_position_columns()
    assert len(cols) == 8, "Should use config preset"
    print(f"✓ Config only (compact): {len(cols)} columns")

    # Test: override_preset beats config
    cols = display_config.get_position_columns(override_preset="minimal")
    assert len(cols) == 6, "Override preset should beat config"
    print(f"✓ Override preset (minimal): {len(cols)} columns")

    # Test: override_columns beats everything
    custom = ["type", "sym"]
    cols = display_config.get_position_columns(
        override_preset="compact",
        override_columns=custom
    )
    assert cols == custom, "Override columns should beat everything"
    print(f"✓ Override columns: {cols}")

    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 Display Configuration System Tests")
    print("=" * 60 + "\n")

    try:
        test_presets()
        test_custom_columns()
        test_column_aliases()
        test_auto_width()
        test_validation()
        test_set_operations()
        test_all_presets()
        test_priority_order()

        print("=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
        print()

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
