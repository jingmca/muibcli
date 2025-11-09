#!/usr/bin/env python3
"""
Quick test for the fixes:
1. Error suppression mechanism
2. man command parameter handling
"""

import time

print("\n" + "="*70)
print("Testing Fixes")
print("="*70)

# Test 1: Error suppression mechanism
print("\nTest 1: Error Suppression Mechanism")
print("-" * 70)

from icli import utils

handler = utils.ThresholdErrorHandler(time_window=10.0, threshold=5)

# Test should_display_error returns correct values
print("Adding 4 errors...")
for i in range(4):
    should_display, count = handler.should_display_error("2150")
    assert should_display == False, f"Error {i+1} should not display"
    assert count == i+1, f"Count should be {i+1}, got {count}"
    print(f"  Error {i+1}: display={should_display}, count={count} ✓")

print("\nAdding 5th error (should trigger display)...")
should_display, count = handler.should_display_error("2150")
assert should_display == True, "5th error should display"
assert count == 5, f"Count should be 5, got {count}"
print(f"  Error 5: display={should_display}, count={count} ✓")

print("\n✅ Test 1 PASSED: Error suppression works correctly\n")

# Test 2: man command parameter handling
print("\nTest 2: man Command Parameter Handling")
print("-" * 70)

# We can't fully test without the full CLI, but we can check the argmap
from icli.cmds.utilities.man import IOpManual

# Check field type
import inspect
from dataclasses import fields

man_fields = {f.name: f.type for f in fields(IOpManual)}
print(f"IOpManual.cmd field type: {man_fields['cmd']}")
assert man_fields['cmd'] == list[str], "cmd field should be list[str]"
print("✅ cmd field is correctly typed as list[str]")

# Check argmap
class MockState:
    pass

# Can't instantiate without state, but we can check argmap structure
argmap = IOpManual.argmap(None)
print(f"argmap: {argmap}")
assert len(argmap) == 1, "Should have 1 argument"
assert argmap[0].name == "*cmd", "Argument should be *cmd"
print("✅ argmap uses *cmd for variable arguments")

print("\n✅ Test 2 PASSED: man command parameter structure is correct\n")

print("="*70)
print("🎉 ALL FIXES VERIFIED!")
print("="*70)
print("\nReady for live testing:")
print("  1. Restart ICLI: poetry run icli")
print("  2. Test error suppression: observe error messages")
print("  3. Test man command:")
print("     - man          (should list all commands)")
print("     - man add      (should show add command help)")
print("     - man buy      (should show buy command help)")
print("  4. Test hh command:")
print("     - hh           (should show quick reference)")
print("="*70 + "\n")
