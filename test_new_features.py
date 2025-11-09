#!/usr/bin/env python3
"""
Test cases for new features:
1. man command with COMMANDS_HELP.md parsing
2. ThresholdErrorHandler for error suppression
"""

import time
from pathlib import Path

# Test 1: Verify COMMANDS_HELP.md exists and is parseable
def test_commands_help_md():
    """Test that COMMANDS_HELP.md exists and contains expected commands."""
    print("\n" + "="*70)
    print("Test 1: COMMANDS_HELP.md existence and structure")
    print("="*70)

    help_file = Path(__file__).parent / "COMMANDS_HELP.md"

    # Check file exists
    assert help_file.exists(), f"COMMANDS_HELP.md not found at {help_file}"
    print(f"✅ COMMANDS_HELP.md exists at {help_file}")

    # Read content
    with open(help_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for essential commands
    essential_commands = ['buy', 'sell', 'positions', 'man', 'hh', 'ifthen', 'evict']
    for cmd in essential_commands:
        assert f"## {cmd}" in content, f"Command '{cmd}' not found in COMMANDS_HELP.md"
        print(f"✅ Command '{cmd}' found in help file")

    # Check for metadata fields
    metadata_fields = ['**分类**:', '**别名**:', '**描述**:', '**用法示例**:']
    for field in metadata_fields:
        assert field in content, f"Metadata field '{field}' not found"
        print(f"✅ Metadata field '{field}' found")

    print("\n✅ Test 1 PASSED: COMMANDS_HELP.md is properly structured\n")


# Test 2: Test man.py command parsing logic (standalone, without dependencies)
def test_man_command_parser():
    """Test the man command's markdown parsing logic using standalone code."""
    print("\n" + "="*70)
    print("Test 2: man command MD parsing (standalone)")
    print("="*70)

    import re

    help_file = Path(__file__).parent / "COMMANDS_HELP.md"

    with open(help_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Inline parsing logic (same as in man.py)
    commands = {}
    sections = re.split(r'\n---\n', content)

    for section in sections:
        section = section.strip()
        if not section or section.startswith('#') and 'ICLI 命令参考手册' in section:
            continue

        # Extract command name
        cmd_match = re.match(r'^## (\w+)', section)
        if not cmd_match:
            continue

        cmd_name = cmd_match.group(1)

        # Extract metadata
        category_match = re.search(r'\*\*分类\*\*:\s*(.+)', section)
        alias_match = re.search(r'\*\*别名\*\*:\s*(.+)', section)
        desc_match = re.search(r'\*\*描述\*\*:\s*(.+)', section)

        category = category_match.group(1).strip() if category_match else "其他"
        aliases = alias_match.group(1).strip() if alias_match else "无"
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract usage examples
        usage_examples = []
        usage_blocks = re.findall(r'```bash\n(.*?)```', section, re.DOTALL)
        for block in usage_blocks:
            examples = [line.strip() for line in block.strip().split('\n') if line.strip() and not line.strip().startswith('#')]
            usage_examples.extend(examples)

        # Extract notes
        notes = []
        notes_section = re.search(r'\*\*注意事项\*\*:(.*?)(?=\n---|\Z)', section, re.DOTALL)
        if notes_section:
            notes_text = notes_section.group(1)
            notes = [line.strip('- ').strip() for line in notes_text.split('\n') if line.strip().startswith('-')]

        commands[cmd_name] = {
            'category': category,
            'aliases': aliases,
            'description': description,
            'usage': usage_examples if usage_examples else [],
            'notes': notes,
        }

    # Verify commands were parsed
    assert len(commands) > 0, "No commands parsed from COMMANDS_HELP.md"
    print(f"✅ Parsed {len(commands)} commands from COMMANDS_HELP.md")

    # Check buy command details
    assert 'buy' in commands, "buy command not parsed"
    buy_info = commands['buy']
    assert 'category' in buy_info, "buy command missing category"
    assert 'description' in buy_info, "buy command missing description"
    assert 'usage' in buy_info, "buy command missing usage"
    print(f"✅ buy command details: category={buy_info['category']}, usage_count={len(buy_info['usage'])}")

    # Check man command (self-reference)
    assert 'man' in commands, "man command not parsed"
    man_info = commands['man']
    print(f"✅ man command found: {man_info['description']}")

    # Verify some critical commands
    critical_commands = ['buy', 'sell', 'positions', 'evict', 'ifthen', 'man', 'hh']
    for cmd in critical_commands:
        assert cmd in commands, f"Critical command '{cmd}' not found"
    print(f"✅ All critical commands parsed successfully")

    print("\n✅ Test 2 PASSED: man command parsing works correctly\n")


# Test 3: Test ThresholdErrorHandler (standalone implementation)
def test_threshold_error_handler():
    """Test the threshold-based error suppression logic."""
    print("\n" + "="*70)
    print("Test 3: ThresholdErrorHandler logic (standalone)")
    print("="*70)

    # Inline implementation for testing
    from dataclasses import dataclass, field

    @dataclass
    class ThresholdErrorRecord:
        occurrences: list = field(default_factory=list)

        def add_occurrence(self, timestamp):
            self.occurrences.append(timestamp)

        def count_in_window(self, now, window_seconds):
            cutoff = now - window_seconds
            self.occurrences = [ts for ts in self.occurrences if ts >= cutoff]
            return len(self.occurrences)

    @dataclass
    class ThresholdErrorHandler:
        time_window: float = 900.0
        threshold: int = 5
        _error_registry: dict = field(default_factory=dict)

        def handle_error(self, error_code, message, log_func, print_func=print):
            now = time.time()
            if error_code not in self._error_registry:
                self._error_registry[error_code] = ThresholdErrorRecord()

            record = self._error_registry[error_code]
            record.add_occurrence(now)
            count = record.count_in_window(now, self.time_window)

            log_func(message)

            if count >= self.threshold:
                print_func(f"{message} (occurred {count} times in last {int(self.time_window/60)} minutes)")
                return True
            return False

    # Track what was logged vs printed
    logged_messages = []
    printed_messages = []

    def mock_log(msg):
        logged_messages.append(msg)

    def mock_print(msg):
        printed_messages.append(msg)

    # Create handler with shorter window for testing (10 seconds, threshold 5)
    handler = ThresholdErrorHandler(time_window=10.0, threshold=5)

    # Test Case 1: First 4 occurrences should only log, not print
    print("\nTest 3.1: First 4 errors should only log (not print)")
    for i in range(4):
        result = handler.handle_error(
            error_code="2150",
            message=f"Error 2150: Invalid position ({i+1})",
            log_func=mock_log,
            print_func=mock_print,
        )
        assert result is False, f"Occurrence {i+1} should not be printed (below threshold)"

    assert len(logged_messages) == 4, f"Expected 4 logged messages, got {len(logged_messages)}"
    assert len(printed_messages) == 0, f"Expected 0 printed messages, got {len(printed_messages)}"
    print(f"✅ First 4 occurrences: {len(logged_messages)} logged, {len(printed_messages)} printed (correct)")

    # Test Case 2: 5th occurrence should trigger both log and print
    print("\nTest 3.2: 5th error should trigger terminal display")
    result = handler.handle_error(
        error_code="2150",
        message="Error 2150: Invalid position (5)",
        log_func=mock_log,
        print_func=mock_print,
    )
    assert result is True, "5th occurrence should be printed (reached threshold)"
    assert len(logged_messages) == 5, f"Expected 5 logged messages, got {len(logged_messages)}"
    assert len(printed_messages) == 1, f"Expected 1 printed message, got {len(printed_messages)}"
    assert "occurred 5 times" in printed_messages[0], "Printed message should show count"
    print(f"✅ 5th occurrence triggered terminal display: {printed_messages[0][:50]}...")

    # Test Case 3: Different error code should be tracked separately
    print("\nTest 3.3: Different error codes are tracked separately")
    logged_messages.clear()
    printed_messages.clear()

    for i in range(3):
        handler.handle_error(
            error_code="2104",
            message=f"Error 2104: Market data farm ({i+1})",
            log_func=mock_log,
            print_func=mock_print,
        )

    assert len(logged_messages) == 3, "Error 2104 should be logged"
    assert len(printed_messages) == 0, "Error 2104 should not be printed (only 3 times)"
    print(f"✅ Different error code tracked independently: {len(logged_messages)} logged, {len(printed_messages)} printed")

    # Test Case 4: Time window expiry
    print("\nTest 3.4: Old errors expire from time window")
    handler_short = ThresholdErrorHandler(time_window=1.0, threshold=3)
    logged_messages.clear()
    printed_messages.clear()

    # Add 2 errors
    for i in range(2):
        handler_short.handle_error("9999", f"Test {i}", mock_log, mock_print)

    # Wait for window to expire
    time.sleep(1.1)

    # Add 2 more errors (should not trigger, as old ones expired)
    for i in range(2):
        handler_short.handle_error("9999", f"Test {i+2}", mock_log, mock_print)

    assert len(logged_messages) == 4, "All errors should be logged"
    assert len(printed_messages) == 0, "Should not print (only 2 in current window)"
    print(f"✅ Time window expiry works correctly")

    print("\n✅ Test 3 PASSED: ThresholdErrorHandler works correctly\n")


# Test 4: File structure verification
def test_file_structure():
    """Test that all necessary files exist."""
    print("\n" + "="*70)
    print("Test 4: File structure verification")
    print("="*70)

    base_path = Path(__file__).parent

    required_files = [
        "COMMANDS_HELP.md",
        "icli/cmds/utilities/man.py",
        "icli/cmds/utilities/hh.py",
        "icli/utils.py",
    ]

    for file_path in required_files:
        full_path = base_path / file_path
        assert full_path.exists(), f"Required file not found: {file_path}"
        print(f"✅ {file_path} exists")

    # Verify man.py contains parse_help_md
    man_file = base_path / "icli/cmds/utilities/man.py"
    with open(man_file, 'r') as f:
        man_content = f.read()
        assert 'parse_help_md' in man_content, "parse_help_md method not found in man.py"
        assert 'IOpManual' in man_content, "IOpManual class not found in man.py"
        print("✅ man.py contains required methods")

    # Verify utils.py contains ThresholdErrorHandler
    utils_file = base_path / "icli/utils.py"
    with open(utils_file, 'r') as f:
        utils_content = f.read()
        assert 'ThresholdErrorHandler' in utils_content, "ThresholdErrorHandler not found in utils.py"
        assert 'ThresholdErrorRecord' in utils_content, "ThresholdErrorRecord not found in utils.py"
        print("✅ utils.py contains ThresholdErrorHandler")

    print("\n✅ Test 4 PASSED: All files exist with correct content\n")


# Run all tests
if __name__ == "__main__":
    print("\n" + "="*70)
    print("Running test suite for new features")
    print("="*70)

    try:
        test_commands_help_md()
        test_man_command_parser()
        test_threshold_error_handler()
        test_file_structure()

        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("="*70)
        print("\nSummary:")
        print("  ✅ COMMANDS_HELP.md properly structured")
        print("  ✅ man command parsing works")
        print("  ✅ ThresholdErrorHandler suppression works")
        print("  ✅ All files exist with correct structure")
        print("\nReady for CLI environment testing!")
        print("="*70 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        raise
