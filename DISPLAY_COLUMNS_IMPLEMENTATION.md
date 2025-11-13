# Display Columns Implementation Guide

本文档说明如何实现灵活的列显示控制系统。

## 📋 已创建的文件

1. **`icli/display_config.py`** - 显示配置核心模块
2. **`icli/cmds/utilities/displayset.py`** - `set` 命令实现

## 🎯 功能设计

### 1. 预设模板

```python
POSITION_PRESETS = {
    "minimal": ["sym", "position", "PNL", "%"],
    "compact": ["type", "sym", "position", "avgCost", "mktPrice", "mktValue", "PNL", "%", "w%"],
    "trading": ["type", "sym", "position", "avgCost", "mktPrice", "closeOrder", "PNL", "%", "w%"],
    "analysis": ["sym", "position", "marketValue", "totalCost", "unrealizedPNL", "dailyPNL", "%", "w%"],
    "spread": ["type", "PC", "strike", "position", "avgCost", "mktPrice", "marketValue", "PNL", "%"],
    "full": None,  # 显示所有列
}
```

### 2. 使用方式

#### 方式A: 运行时 `set` 命令

```bash
# 查看当前设置
set

# 设置预设
set positions.preset compact
set positions.preset minimal
set positions.preset full

# 自定义列
set positions.columns type,sym,position,PNL,%,w%

# 启用/禁用自动宽度
set positions.autowidth true
```

#### 方式B: 命令行参数（推荐修改）

```bash
# 使用预设
positions --preset compact
positions -p minimal

# 自定义列
positions --columns type,sym,position,PNL,%
positions -c type,sym,PNL

# 强制模式
positions --compact
positions --full
```

#### 方式C: 环境变量（全局配置）

在 `.env.icli` 中添加：
```bash
ICLI_POSITION_PRESET=compact
ICLI_POSITION_COLUMNS=
ICLI_POSITION_AUTO_WIDTH=true
```

### 3. 优先级

```
命令行参数 > set命令 > 环境变量 > 默认值（auto）
```

## 🔧 修改 positions.py 的方法

### 步骤1: 添加导入

在 `icli/cmds/portfolio/positions.py` 顶部添加：

```python
from icli.display_config import display_config
```

### 步骤2: 扩展 argmap

修改 `argmap()` 方法：

```python
def argmap(self):
    return [
        DArg("*symbols", convert=lambda x: set([sym.upper() for sym in x])),
        DArg(
            "--preset", "-p",
            desc="Display preset: minimal, compact, trading, analysis, spread, full",
            default=None
        ),
        DArg(
            "--columns", "-c",
            desc="Custom columns (comma-separated)",
            default=None,
            convert=lambda x: [c.strip() for c in x.split(",")]
        ),
        DArg(
            "--compact",
            desc="Force compact mode",
            action="store_true"
        ),
        DArg(
            "--full", "-f",
            desc="Show all columns",
            action="store_true"
        ),
    ]
```

### 步骤3: 修改 run() 方法中的列选择逻辑

在显示逻辑部分（约 line 375），替换原有的硬编码列选择：

```python
# 原代码（line 375左右）
if terminal_width <= 120:
    compact_cols = ["type", "sym", "position", "avgCost", "mktPrice", "mktValue", "PNL", "%", "w%"]
    # ...

# 修改为：
# 获取应该显示的列
display_cols = display_config.get_position_columns(
    override_preset=self.preset if hasattr(self, 'preset') else None,
    override_columns=self.columns if hasattr(self, 'columns') else None,
    current_terminal_width=terminal_width
)

# 如果指定了 --compact 标志
if hasattr(self, 'compact') and self.compact:
    display_cols = POSITION_PRESETS["compact"]

# 如果指定了 --full 标志
if hasattr(self, 'full') and self.full:
    display_cols = None  # None = show all

# 应用列过滤
if display_cols is not None:
    # 创建紧凑视图
    compact_cols = display_cols
    # ... 原有的列映射和格式化代码
else:
    # 显示所有列（full模式）
    display_df = allPositions.copy()
```

## 📝 完整的修改示例

这是一个完整的修改示例片段：

```python
# 在 IOpPositions 类中添加新字段
@command(names=["positions", "ls"])
@dataclass
class IOpPositions(IOp):
    """Print datatable of all positions."""

    symbols: set[str] = field(init=False)
    preset: str | None = field(init=False, default=None)
    columns: list[str] | None = field(init=False, default=None)
    compact: bool = field(init=False, default=False)
    full: bool = field(init=False, default=False)

    def argmap(self):
        return [
            DArg("*symbols", convert=lambda x: set([sym.upper() for sym in x])),
            DArg("--preset", "-p", default=None),
            DArg("--columns", "-c", default=None,
                 convert=lambda x: [c.strip() for c in x.split(",")] if x else None),
            DArg("--compact", action="store_true", default=False),
            DArg("--full", "-f", action="store_true", default=False),
        ]
```

## 🧪 测试用例

创建测试文件 `test_display_config.py`：

```python
#!/usr/bin/env python3
"""Test display configuration system."""

from icli.display_config import (
    display_config,
    get_available_presets,
    validate_columns,
)

def test_presets():
    """Test preset configurations."""
    print("✅ Testing presets...")

    # Test minimal preset
    cols = display_config.get_position_columns(override_preset="minimal")
    assert cols == ["sym", "position", "PNL", "%"]
    print(f"   minimal: {cols}")

    # Test compact preset
    cols = display_config.get_position_columns(override_preset="compact")
    assert len(cols) == 9
    print(f"   compact: {cols}")

    # Test full preset
    cols = display_config.get_position_columns(override_preset="full")
    assert cols is None  # None means all columns
    print(f"   full: All columns")

def test_custom_columns():
    """Test custom column specification."""
    print("\n✅ Testing custom columns...")

    custom = ["type", "sym", "position", "PNL"]
    cols = display_config.get_position_columns(override_columns=custom)
    assert cols == custom
    print(f"   custom: {cols}")

def test_column_aliases():
    """Test column name aliases."""
    print("\n✅ Testing column aliases...")

    # Use aliases
    custom = ["type", "sym", "position", "PNL", "mktPrice", "avgCost"]
    cols = display_config.get_position_columns(override_columns=custom)

    # Check aliases are resolved
    assert "marketPrice" in cols
    assert "averageCost" in cols
    assert "unrealizedPNL" in cols
    print(f"   aliased: {cols}")

def test_auto_width():
    """Test automatic width detection."""
    print("\n✅ Testing auto width detection...")

    # Enable auto mode
    display_config.position_preset = "auto"
    display_config.position_auto_width = True

    # Narrow terminal
    cols = display_config.get_position_columns(current_terminal_width=80)
    print(f"   80 cols: {len(cols) if cols else 'all'} fields")

    # Wide terminal
    cols = display_config.get_position_columns(current_terminal_width=200)
    print(f"   200 cols: {len(cols) if cols else 'all'} fields")

def test_validation():
    """Test column validation."""
    print("\n✅ Testing column validation...")

    # Valid columns
    valid, invalid = validate_columns(["type", "sym", "PNL", "mktPrice"])
    assert valid
    print(f"   Valid columns: {valid}")

    # Invalid columns
    valid, invalid = validate_columns(["type", "sym", "INVALID", "BADCOL"])
    assert not valid
    assert "INVALID" in invalid
    print(f"   Invalid columns: {invalid}")

if __name__ == "__main__":
    test_presets()
    test_custom_columns()
    test_column_aliases()
    test_auto_width()
    test_validation()
    print("\n🎉 All tests passed!")
```

## 🚀 实施步骤

### Phase 1: 基础设施（已完成）
- [x] 创建 `display_config.py`
- [x] 创建 `set` 命令
- [x] 定义预设模板

### Phase 2: 修改 positions 命令
- [ ] 添加命令行参数支持
- [ ] 集成 `display_config`
- [ ] 测试各种模式

### Phase 3: 修改 quotes 显示
- [ ] 找到实时报价显示代码（在 cli.py 中）
- [ ] 应用相同的配置系统
- [ ] 添加报价预设

### Phase 4: 持久化
- [ ] 从 `.env.icli` 加载配置
- [ ] 添加 `set --save` 功能

## 💡 使用示例

```bash
# 示例1: 使用预设
positions --preset minimal
positions -p trading

# 示例2: 自定义列
positions --columns type,sym,position,PNL,%,w%
positions -c sym,PNL,%

# 示例3: 组合过滤
positions AAPL MSFT --preset compact
positions AAPL --columns sym,position,PNL

# 示例4: 运行时配置
set positions.preset trading
positions                    # 使用 trading 预设

set positions.columns type,sym,PNL,%
positions                    # 使用自定义列

# 示例5: 强制模式
positions --compact         # 强制紧凑
positions --full           # 强制显示所有列
```

## 📊 列别名参考

```python
"avgCost"   -> "averageCost"
"mktPrice"  -> "marketPrice"
"mktValue"  -> "marketValue"
"PNL"       -> "unrealizedPNL"
"pnl"       -> "unrealizedPNL"
"cost"      -> "averageCost"
"price"     -> "marketPrice"
"value"     -> "marketValue"
"pct"       -> "%"
"weight"    -> "w%"
```

这样用户可以用更简短的名字，系统会自动映射到实际的列名。

## 🔍 下一步

1. **测试基础模块**：运行 `test_display_config.py`
2. **修改 positions.py**：按照上面的步骤集成
3. **测试实际使用**：在 tmux 中测试各种参数组合
4. **扩展到 quotes**：找到报价显示代码并应用
5. **文档更新**：更新 COMMANDS_HELP.md
