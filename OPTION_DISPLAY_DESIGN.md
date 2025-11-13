# 期权显示优化设计

## 📋 需求

### 1. 期权符号显示格式

**Minimal/Compact/Trading 模式**：
- 使用标准 OCC 期权符号格式
- 例如：`AAPL240816C00220000`
- 或简化格式：`AAPL 240816 C220` (更紧凑)

**Full 模式**：
- 分列显示：Symbol, ExpDate, C/P, Strike
- 保持当前的详细格式

### 2. 报价区持仓成本显示

在报价区需要显示：
- 如果有该标的的持仓，显示持仓平均成本
- 显示当前价格相对持仓成本的盈亏百分比
- 便于快速判断浮盈浮亏

---

## 🎯 期权符号格式规范

### OCC 标准格式

```
[Symbol][YY][MM][DD][C/P][Strike_8位]
例如：AAPL  24  08  16  C  00220000
```

### 建议的紧凑格式

对于不同宽度的终端，提供不同的紧凑级别：

```python
# Ultra Compact (<=80字符终端)
"AAPL24C220"           # 符号+年份+C/P+strike整数部分

# Compact (<=120字符终端)
"AAPL 0816 C220"       # 符号 月日 C/P+strike

# Standard (>120字符终端)
"AAPL 240816 C220.00"  # 符号 年月日 C/P+strike带小数

# Full (full模式)
分列显示所有字段
```

---

## 🔧 实现方案

### 方案1: positions.py 期权符号格式化

**当前实现**（line 403-418）：
```python
# Format: SYMBOL EXPDATE STRIKE PC
exp_date = f"{date_str[4:6]}{date_str[6:8]}"  # MMDD
strike_val = f"{row['strike']:.0f}"
pc = row.get("PC", "")
symbol = str(row["sym"])[:6]
compact_df.at[idx, "sym"] = f"{symbol} {exp_date} {strike_val}{pc}"
# 结果: "AAPL 0816 220C"
```

**改进建议**：

```python
def format_option_symbol(
    symbol: str,
    date: str,
    strike: float,
    pc: str,
    mode: str = "compact"
) -> str:
    """Format option symbol based on display mode.

    Args:
        symbol: Underlying symbol (e.g., 'AAPL')
        date: Expiration date in YYYYMMDD format
        strike: Strike price
        pc: Put/Call flag ('P' or 'C')
        mode: Display mode ('minimal', 'compact', 'standard', 'full')

    Returns:
        Formatted option symbol
    """
    # Extract date components
    if len(date) >= 8:
        yy = date[2:4]    # YY
        mm = date[4:6]    # MM
        dd = date[6:8]    # DD
        mmdd = mm + dd    # MMDD
    else:
        yy = mm = dd = mmdd = ""

    # Format strike
    strike_int = int(strike)
    strike_decimal = strike - strike_int

    if mode == "minimal":
        # Ultra compact: AAPL24C220
        if strike_decimal == 0:
            return f"{symbol}{yy}{pc}{strike_int}"
        else:
            return f"{symbol}{yy}{pc}{strike:.1f}"

    elif mode == "compact":
        # Compact: AAPL 0816 C220 or AAPL 0816 C220.5
        if strike_decimal == 0:
            return f"{symbol} {mmdd} {pc}{strike_int}"
        else:
            return f"{symbol} {mmdd} {pc}{strike:.1f}"

    elif mode == "standard":
        # Standard: AAPL 240816 C220.00
        return f"{symbol} {yy}{mmdd} {pc}{strike:.2f}"

    elif mode == "occ":
        # Full OCC: AAPL240816C00220000
        strike_padded = f"{int(strike * 1000):08d}"
        return f"{symbol}{yy}{mm}{dd}{pc}{strike_padded}"

    else:
        # Default to compact
        return f"{symbol} {mmdd} {pc}{strike_int if strike_decimal == 0 else strike:.1f}"


# 使用示例
format_option_symbol("AAPL", "20240816", 220.0, "C", "compact")
# 返回: "AAPL 0816 C220"

format_option_symbol("AAPL", "20240816", 220.5, "C", "compact")
# 返回: "AAPL 0816 C220.5"

format_option_symbol("AAPL", "20240816", 220.0, "C", "occ")
# 返回: "AAPL240816C00220000"
```

**集成到 positions.py**：

```python
# 在 positions.py 的 line 403 附近

from icli.helpers import format_option_symbol  # 添加导入

# 替换当前的格式化逻辑
if row["type"] in {"OPT", "FOP"} and pd.notna(row.get("strike")):
    date_str = str(row.get("date", ""))
    strike = row.get("strike", 0)
    pc = row.get("PC", "")
    symbol = str(row["sym"])

    # 根据 display_config 选择格式
    if display_config.position_preset in ["minimal"]:
        mode = "minimal"
    elif display_config.position_preset in ["compact", "trading"]:
        mode = "compact"
    elif display_config.position_preset in ["full"]:
        # Full 模式不格式化，保持分列显示
        continue
    else:
        mode = "compact"

    compact_df.at[idx, "sym"] = format_option_symbol(
        symbol, date_str, strike, pc, mode
    )
```

---

### 方案2: 报价区显示持仓成本

**需要修改的位置**：`cli.py` 的 `formatTicker()` 函数（line 4062+）

**实现思路**：

1. **在 formatTicker() 中访问持仓数据**：

```python
def formatTicker(c):
    # ... 现有代码 ...

    # 获取持仓信息（如果有）
    position_cost = None
    position_size = None

    if pos := self.positionsDB.get(c.contract.conId):
        position_cost = pos.avgCost
        position_size = pos.position

    # ... 继续现有的报价格式化逻辑 ...
```

2. **显示持仓成本和盈亏**：

```python
# 在报价显示字符串中添加持仓成本

# 对于股票/期货（line 4752附近）
if position_cost and position_size:
    # 计算盈亏
    pnl_amt = (usePrice - position_cost) * position_size
    pnl_pct = ((usePrice - position_cost) / position_cost) * 100

    # 添加到显示字符串
    position_info = f"[pos@{position_cost:>8,.2f} {pnl_pct:>+6.2f}% ${pnl_amt:>+10,.0f}]"
else:
    position_info = ""

return " ".join([
    f"{ls:<9}",
    position_info,  # 新增：持仓成本信息
    f"{e100:>10,.{decimals}f}",
    # ... 其余字段 ...
])
```

3. **期权的持仓成本显示**（line 4625附近）：

```python
# 对于期权
if position_cost and position_size:
    # 期权的盈亏计算
    pnl_amt = (mark - position_cost) * position_size * multiplier
    pnl_pct = ((mark - position_cost) / position_cost) * 100 if position_cost else 0

    position_info = f"[{position_size:>+5,.0f}@{position_cost:>6.2f} {pnl_pct:>+6.1f}%]"
else:
    position_info = ""

return " ".join([
    rowName,
    position_info,  # 新增：持仓成本信息
    f"[u {und:>8,.2f} ({itm} {underlyingStrikeDifference:>7,.2f}%)]",
    # ... 其余字段 ...
])
```

**颜色编码**：

```python
# 根据盈亏添加颜色
if pnl_pct > 0:
    position_info = f"<aaa bg='green'>[pos@{position_cost:>8,.2f} {pnl_pct:>+6.2f}%]</aaa>"
elif pnl_pct < 0:
    position_info = f"<aaa bg='red'>[pos@{position_cost:>8,.2f} {pnl_pct:>+6.2f}%]</aaa>"
else:
    position_info = f"[pos@{position_cost:>8,.2f} {pnl_pct:>+6.2f}%]"
```

---

### 方案3: 获取持仓数据的详细实现

**查找 positionsDB 结构**：

```python
# 在 cli.py 中
@property
def positionsDB(self):
    """Access positions database."""
    return self.ib.wrapper.positions[self.accountId]

# 返回的数据结构是 dict[conId, Position]
# Position 包含：
# - avgCost: 平均成本
# - position: 持仓数量
# - account: 账户ID
# - contract: 合约对象
```

**安全访问示例**：

```python
def get_position_info(self, contract) -> tuple[float | None, float | None]:
    """Get position average cost and size for a contract.

    Returns:
        (avg_cost, position_size) or (None, None) if no position
    """
    try:
        if pos := self.positionsDB.get(contract.conId):
            return (pos.avgCost, pos.position)
    except:
        pass

    return (None, None)

# 使用
avg_cost, pos_size = self.get_position_info(c.contract)
if avg_cost and pos_size:
    # 显示持仓信息
    ...
```

---

## 📊 显示效果对比

### 当前 positions 显示（compact）

```
type  sym              position  avgCost   mktPrice  mktValue    PNL      %      w%
----  ---------------  --------  --------  --------  --------  ------  ------  ------
OPT   AAPL 0816 220C      10.0     5.25      5.80     5800.0   550.0   10.48   2.15
```

### 优化后 positions 显示（compact with OCC format）

```
sym                 position  avgCost  mktPrice  mktValue    PNL      %      w%
------------------  --------  -------  --------  --------  ------  ------  ------
AAPL 0816 C220        10.0     5.25     5.80     5800.0   550.0   10.48   2.15
```

### 优化后 positions 显示（minimal - ultra compact）

```
sym             pos   cost   price   value    PNL     %
--------------  ----  -----  ------  ------  ------  -----
AAPL24C220      10    5.25   5.80    5800    550     10.5
```

### 当前 quote 显示（期权）

```
AAPL 240816C220: [u 225.50 (I +2.50%)] [iv 0.25] [d +0.65] ...
```

### 优化后 quote 显示（期权 + 持仓成本）

```
AAPL 0816 C220: [+10@5.25 +10.5%] [u 225.50 (I +2.50%)] [iv 0.25] [d +0.65] ...
                 ^^^^^^^^^^^^^^^^^^^^
                 新增：持仓数量@成本 盈亏%
```

---

## 🎨 颜色方案

**持仓成本显示的颜色**：

```python
# 盈利 - 绿色背景
[+10@5.25 +10.5%]  →  <aaa bg='green'>[+10@5.25 +10.5%]</aaa>

# 亏损 - 红色背景
[-10@5.25 -5.2%]   →  <aaa bg='red'>[-10@5.25 -5.2%]</aaa>

# 持平 - 无颜色
[+10@5.25 +0.0%]   →  [+10@5.25 +0.0%]
```

---

## 📐 宽度计算

### 持仓成本字段宽度

```
格式：[+10@5.25 +10.5%]
宽度：约 18 字符

组成：
[     = 1
+10   = 3 (position size)
@     = 1
5.25  = 5 (avg cost, 2 decimals)
      = 1 (space)
+10.5 = 5 (pnl %, 1 decimal)
%     = 1
]     = 1
------
总计  = 18 字符
```

### 不同模式的总宽度

```
Minimal quote (no position info):
  sym(9) + fields(~100) = ~110 chars

Compact quote (with position info):
  sym(15) + pos(18) + fields(~100) = ~135 chars

Trading quote (with position info):
  sym(15) + pos(18) + fields(~120) = ~155 chars
```

---

## 🚀 实施步骤

### Phase 1: 期权符号格式化（优先）

1. **创建 `format_option_symbol()` 函数**
   - 位置：`icli/helpers.py`
   - 支持 minimal, compact, standard, occ 四种模式

2. **修改 `positions.py`**
   - 集成 `format_option_symbol()`
   - 根据 `display_config.position_preset` 选择模式
   - Full 模式保持分列显示

3. **测试**
   - 测试不同预设下的期权符号显示
   - 验证宽度是否合适

### Phase 2: 报价区持仓成本（次要）

1. **添加持仓数据访问方法**
   - 位置：`cli.py` IBKRCmdlineApp 类
   - 方法：`get_position_info(contract)`

2. **修改 `formatTicker()`**
   - 在股票/期货部分添加持仓成本显示
   - 在期权部分添加持仓成本显示
   - 添加颜色编码

3. **测试**
   - 测试有持仓和无持仓的显示
   - 验证盈亏计算正确性
   - 检查宽度和对齐

### Phase 3: 配置和优化

1. **添加配置选项**
   - `display_config.show_position_cost = True/False`
   - 允许用户关闭持仓成本显示

2. **优化宽度**
   - 根据终端宽度自动调整显示格式
   - 窄终端时隐藏部分字段

3. **文档更新**
   - 更新 COMMANDS_HELP.md
   - 添加使用示例

---

## 💡 使用示例

### 启动时指定期权显示模式

```bash
# 紧凑模式（推荐日内交易）
poetry run icli -p compact

# 最小模式（超窄终端）
poetry run icli -p minimal

# 完整模式（详细分析）
poetry run icli -p full
```

### 运行时调整

```bash
# 在 icli 中
display positions.preset compact
display positions.preset minimal
display positions.preset full
```

---

## ❓ 常见问题

### Q1: 如何在 Full 模式显示完整的期权信息？

在 Full 模式下，期权不会被格式化为单一符号，而是分列显示：
- Symbol: AAPL
- Date: 20240816
- PC: C
- Strike: 220.00
- Position: 10.0
- AvgCost: 5.25
- ... 等等

### Q2: 持仓成本会占用多少宽度？

约 18 字符。建议在 >120 字符宽度的终端使用。

### Q3: 如果没有持仓，报价区会显示什么？

不显示持仓成本字段，节省宽度。

### Q4: 可以自定义期权符号格式吗？

目前支持 4 种预设格式。如需更多自定义，可以修改 `format_option_symbol()` 函数。

---

## 🎯 优先级建议

**高优先级**：
1. ✅ 实现 `format_option_symbol()` - 立即提升可读性
2. ✅ 修改 positions.py 集成期权符号格式化

**中优先级**：
3. 添加报价区持仓成本显示 - 实用但非必需

**低优先级**：
4. 配置选项和优化 - 锦上添花

---

选择从哪里开始？我建议先实现 Phase 1，因为期权符号格式化改进最明显且风险最低。
