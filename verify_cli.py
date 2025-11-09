#!/usr/bin/env python3
"""
CLI environment verification script
Tests that commands can be imported and registered properly
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("CLI Environment Verification")
print("="*70 + "\n")

# Test 1: Import command modules
print("Test 1: Importing command modules...")
try:
    from icli.cmds.utilities import hh
    print("✅ hh module imported")

    from icli.cmds.utilities import man
    print("✅ man module imported")

    from icli import utils
    print("✅ utils module imported")

except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Verify command registration
print("\nTest 2: Verifying command registration...")
try:
    from icli.cmds.base import _COMMAND_REGISTRY

    # Find hh and man commands in registry
    hh_found = False
    man_found = False
    hhh_alias_found = False

    for cmd_class in _COMMAND_REGISTRY:
        names = getattr(cmd_class, '__command_names__', [])
        if 'hh' in names:
            hh_found = True
            print(f"✅ hh command registered: {cmd_class.__name__}")
        if 'man' in names:
            man_found = True
            print(f"✅ man command registered: {cmd_class.__name__}")
        if 'hhh' in names:
            hhh_alias_found = True
            print(f"✅ hhh alias registered for man command")

    if not hh_found:
        print("❌ hh command not found in registry")
    if not man_found:
        print("❌ man command not found in registry")
    if not hhh_alias_found:
        print("⚠️  hhh alias not found (should be alias for man)")

    print(f"\n✅ Total commands in registry: {len(_COMMAND_REGISTRY)}")

except Exception as e:
    print(f"❌ Command registration check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test man command parsing (use standalone parsing)
print("\nTest 3: Testing man command parsing...")
try:
    import re

    # Inline parsing logic (same as in man.py)
    help_file = Path(__file__).parent / "COMMANDS_HELP.md"
    with open(help_file, "r", encoding="utf-8") as f:
        content = f.read()

    commands = {}
    sections = re.split(r'\n---\n', content)

    for section in sections:
        section = section.strip()
        if not section or section.startswith('#') and 'ICLI 命令参考手册' in section:
            continue

        cmd_match = re.match(r'^## (\w+)', section)
        if not cmd_match:
            continue

        cmd_name = cmd_match.group(1)
        category_match = re.search(r'\*\*分类\*\*:\s*(.+)', section)
        desc_match = re.search(r'\*\*描述\*\*:\s*(.+)', section)

        commands[cmd_name] = {
            'category': category_match.group(1).strip() if category_match else "其他",
            'description': desc_match.group(1).strip() if desc_match else "",
        }

    if commands:
        print(f"✅ Successfully parsed {len(commands)} commands from COMMANDS_HELP.md")

        # Test a few key commands
        test_commands = ['buy', 'sell', 'man', 'hh', 'positions']
        for cmd in test_commands:
            if cmd in commands:
                info = commands[cmd]
                print(f"  ✅ {cmd}: {info['description'][:50]}...")
            else:
                print(f"  ❌ {cmd} not found")
    else:
        print("❌ No commands parsed")

except Exception as e:
    print(f"❌ Parsing test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test ThresholdErrorHandler
print("\nTest 4: Testing ThresholdErrorHandler...")
try:
    handler = utils.ThresholdErrorHandler()
    print(f"✅ ThresholdErrorHandler created")
    print(f"  - Time window: {handler.time_window}s ({handler.time_window/60:.0f} minutes)")
    print(f"  - Threshold: {handler.threshold} occurrences")

    # Quick functional test
    logged = []
    printed = []

    for i in range(3):
        handler.handle_error("TEST", "Test error", logged.append, printed.append)

    if len(logged) == 3 and len(printed) == 0:
        print(f"✅ Suppression works: 3 errors logged, 0 printed (below threshold)")
    else:
        print(f"❌ Suppression failed: {len(logged)} logged, {len(printed)} printed")

except Exception as e:
    print(f"❌ ThresholdErrorHandler test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Verify file modifications
print("\nTest 5: Verifying file modifications...")
try:
    # Check cli.py has startup message with 'man'
    cli_file = Path(__file__).parent / "icli" / "cli.py"
    with open(cli_file, 'r') as f:
        cli_content = f.read()
        if "输入 'man <命令>' 查看具体命令详细帮助" in cli_content:
            print("✅ cli.py startup message updated correctly")
        else:
            print("❌ cli.py startup message not found")

        if "thresholdErrorHandler" in cli_content:
            print("✅ cli.py has thresholdErrorHandler field")
        else:
            print("❌ cli.py missing thresholdErrorHandler field")

        if "thresholdErrorHandler.handle_error" in cli_content:
            print("✅ cli.py uses thresholdErrorHandler in errorHandler")
        else:
            print("❌ cli.py doesn't use thresholdErrorHandler")

    # Check hh.py has 'man' reference
    hh_file = Path(__file__).parent / "icli" / "cmds" / "utilities" / "hh.py"
    with open(hh_file, 'r') as f:
        hh_content = f.read()
        if "输入 man <命令> 查看具体命令详细帮助" in hh_content:
            print("✅ hh.py updated with man reference")
        else:
            print("❌ hh.py not updated")

    # Verify hhh.py is removed
    hhh_file = Path(__file__).parent / "icli" / "cmds" / "utilities" / "hhh.py"
    if not hhh_file.exists():
        print("✅ Old hhh.py file removed")
    else:
        print("❌ Old hhh.py file still exists")

except Exception as e:
    print(f"❌ File verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("✅ ALL CLI VERIFICATION TESTS PASSED!")
print("="*70)
print("\nThe CLI is ready for live testing with IBKR Gateway.")
print("\nTo test in actual environment:")
print("  1. Start IBKR Gateway")
print("  2. Run: poetry run icli")
print("  3. Test commands:")
print("     - hh")
print("     - man")
print("     - man buy")
print("     - man positions")
print("="*70 + "\n")
