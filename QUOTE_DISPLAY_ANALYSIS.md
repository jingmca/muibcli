# 报价区显示分析

## 📊 当前报价显示字段

通过分析 `icli/cli.py` 的 `formatTicker()` 函数（line 4062-4773），当前报价区显示的字段如下：

### 股票/期货行情（line 4752-4772）

```python
return " ".join([
    f"{ls:<9}",                    # 1. 标的代码 (9字符)
    f"{e100:>10,.{decimals}f}",    # 2. 15分钟EMA
    f"({e100diff:>6,.2f})",        # 3. EMA100差价
    f"{trend}",                     # 4. 趋势标志 (>, <, =)
    f"{e300:>10,.{decimals}f}",    # 5. 65分钟EMA
    f"({e300diff:>6,.2f})",        # 6. EMA300差价
    f"{usePrice:>10,.{decimals}f} ±{spread:<6}",  # 7. 当前价 ± 价差
    f"{high:>10,.{decimals}f}",    # 8. 最高价
    f"{low:>10,.{decimals}f}",     # 9. 最低价
    f"{bid:>10,.{decimals}f} x {bidSize} {ask:>10,.{decimals}f} x {askSize}",  # 10. 买卖盘
    f"({atr})",                     # 11. ATR波动率
    f"({pctVWAP} {amtVWAP})",      # 12. VWAP偏离
    f"{close:>10,.{decimals}f}",   # 13. 收盘价
    f"({ago:>7})",                 # 14. 数据时间
    f"@ ({agoLastTrade})",         # 15. 最后交易时间（可选）
    "HALTED!" if halted else "",   # 16. 停牌标志
])
```

**总宽度**：约 150-180 字符

### 期权行情（line 4625-4644）

```python
return " ".join([
    rowName,                        # 1. 合约名称（支持多行spread）
    f"[u {und:>8,.2f} ({itm} {underlyingStrikeDifference:>7,.2f}%)]",  # 2. 标的价 + ITM + 偏离%
    f"[iv {iv:.2f}]",              # 3. 隐含波动率
    f"[d {delta:>5.2f}]",          # 4. Delta
    f"{e100:>6}",                   # 5. 15分钟EMA
    f"{trend}",                     # 6. 趋势
    f"{e300:>6}",                   # 7. 65分钟EMA
    f"{mark:>6} ±{spread:<4}",     # 8. 标记价 ± 价差
    f"{bid:>6} x {bidSize} {ask:>6} x {askSize}",  # 9. 买卖盘
    f"{amtVWAP}",                   # 10. VWAP偏离
    f"({ago:>7})",                  # 11. 数据时间
    f"(s {compensated:>8,.2f} @ {compdiff:>6,.2f})",  # 12. 行权成本
    f"({when:>3.2f} d)",           # 13. 到期天数
    "HALTED!" if halted else "",   # 14. 停牌标志
])
```

**总宽度**：约 200+ 字符（单腿）

---

## 💡 报价区预设建议

基于实际显示字段和使用场景，建议以下预设：

```python
QUOTE_PRESETS = {
    # 最小化模式 - 只看关键信息（~80字符）
    "minimal": [
        "sym",           # 标的
        "last",          # 当前价
        "bid",           # 买价
        "ask",           # 卖价
        "change",        # 涨跌额
        "%",             # 涨跌幅
    ],

    # 紧凑模式 - 日常交易（~120字符）
    "compact": [
        "sym",           # 标的
        "last",          # 当前价
        "bid",           # 买价
        "ask",           # 卖价
        "bidSize",       # 买量
        "askSize",       # 卖量
        "change",        # 涨跌额
        "%",             # 涨跌幅
        "volume",        # 成交量
    ],

    # 交易模式 - 重点关注盘口（~140字符）
    "trading": [
        "sym",           # 标的
        "ema100",        # 15分钟EMA
        "trend",         # 趋势标志
        "last",          # 当前价
        "spread",        # 价差
        "bid",           # 买价
        "ask",           # 卖价
        "bidSize",       # 买量
        "askSize",       # 卖量
        "atr",           # ATR
        "%",             # 涨跌幅
    ],

    # 技术分析模式 - 完整技术指标（~180字符）
    "analysis": [
        "sym",           # 标的
        "ema100",        # 15分钟EMA
        "ema100diff",    # EMA100差价
        "trend",         # 趋势
        "ema300",        # 65分钟EMA
        "last",          # 当前价
        "high",          # 最高
        "low",           # 最低
        "vwap",          # VWAP
        "vwapDiff",      # VWAP偏离
        "atr",           # ATR
        "%",             # 涨跌幅
        "volume",        # 成交量
    ],

    # 期权模式 - 希腊值+盘口
    "options": [
        "sym",           # 合约名称
        "underlying",    # 标的价
        "itm",           # 实值标志
        "iv",            # 隐含波动率
        "delta",         # Delta
        "gamma",         # Gamma（可选）
        "theta",         # Theta（可选）
        "mark",          # 标记价
        "bid",           # 买价
        "ask",           # 卖价
        "spread",        # 价差
        "dte",           # 到期天数
    ],

    # 日内scalping模式 - 极简快速（~100字符）
    "scalping": [
        "sym",           # 标的
        "ema100",        # 快速EMA
        "last",          # 当前价
        "spread",        # 价差
        "bid",           # 买价
        "ask",           # 卖价
        "bidSize",       # 买量
        "askSize",       # 卖量
        "atr",           # 波动率
        "%",             # 涨跌幅
    ],

    # 完整模式 - 所有字段
    "full": None,
}
```

---

## 🎯 字段分组说明

### 核心价格信息
- `sym` - 标的代码
- `last` / `current` - 当前价（实际是mid价）
- `bid` - 买价
- `ask` - 卖价
- `spread` - 买卖价差
- `close` - 收盘价

### 盘口深度
- `bidSize` - 买盘量
- `askSize` - 卖盘量
- `volume` - 成交量

### 技术指标
- `ema100` - 15分钟EMA（900秒）
- `ema300` - 65分钟EMA（3900秒）
- `ema100diff` - 当前价与EMA100差价
- `ema300diff` - 当前价与EMA300差价
- `trend` - 趋势标志（>, <, =）
- `atr` - ATR波动率（1小时）
- `vwap` - VWAP价格
- `vwapDiff` - 与VWAP偏离

### 日内价格
- `high` - 最高价
- `low` - 最低价
- `change` - 涨跌额
- `%` - 涨跌幅

### 期权希腊值
- `underlying` - 标的价格
- `itm` - 实值标志（I）
- `iv` - 隐含波动率
- `delta` - Delta
- `gamma` - Gamma
- `theta` - Theta
- `vega` - Vega
- `mark` - 标记价（期权）
- `compensated` - 行权成本
- `dte` - 到期天数

### 元数据
- `ago` - 数据更新时间
- `lastTradeAgo` - 最后交易时间
- `halted` - 停牌标志

---

## 🔧 实现建议

### 1. 字段映射表

由于报价显示是动态生成的字符串，需要重构代码提取字段：

```python
# 在 display_config.py 中添加
QUOTE_FIELD_MAPPING = {
    # 基础字段
    "sym": "symbol",
    "last": "current_price",
    "bid": "bid",
    "ask": "ask",
    "spread": "ask_bid_spread",

    # 技术指标
    "ema100": "ema_900",
    "ema300": "ema_3900",
    "trend": "ema_trend",
    "atr": "atr_3600",

    # 期权希腊值
    "iv": "implied_volatility",
    "delta": "option_delta",
    "gamma": "option_gamma",
    "theta": "option_theta",

    # 简写别名
    "chg": "change",
    "pct": "%",
    "vol": "volume",
}
```

### 2. 重构 formatTicker()

建议创建结构化的报价数据类：

```python
@dataclass
class QuoteData:
    """Structured quote data for flexible display."""
    symbol: str
    last: float
    bid: float | None
    ask: float | None
    bidSize: int | None
    askSize: int | None
    high: float | None
    low: float | None
    close: float | None
    volume: int | None

    # Technical indicators
    ema100: float | None
    ema300: float | None
    ema100diff: float | None
    ema300diff: float | None
    trend: str | None
    atr: float | None
    vwap: float | None
    vwapDiff: float | None

    # Greeks (for options)
    underlying: float | None = None
    iv: float | None = None
    delta: float | None = None
    # ...

    def to_display_string(self, columns: list[str] | None = None) -> str:
        """Format quote according to column selection."""
        if columns is None:
            # Use full format
            return self._format_full()

        parts = []
        for col in columns:
            if hasattr(self, col):
                parts.append(self._format_field(col, getattr(self, col)))

        return " ".join(parts)
```

### 3. 渐进式重构

由于 `formatTicker()` 很复杂，建议分阶段：

**Phase 1**: 添加字段选择（保持现有格式）
```python
def formatTicker(c, show_fields: list[str] | None = None):
    # ... 现有代码 ...

    # 在最后返回前，根据 show_fields 过滤
    if show_fields:
        return filter_fields(full_output, show_fields)
    return full_output
```

**Phase 2**: 提取数据和格式化分离
```python
def extract_quote_data(c) -> QuoteData:
    """Extract structured data from ticker."""
    # 提取所有字段到结构化对象

def format_quote_data(data: QuoteData, columns: list[str] | None) -> str:
    """Format quote data according to column selection."""
    # 格式化输出
```

**Phase 3**: 完全重构为列驱动

---

## 📌 快速实现方案

**最简单的方案**（不重构 formatTicker）：

在 `display_config.py` 中添加：

```python
QUOTE_DISPLAY_MODES = {
    "minimal": "MINIMAL",      # 使用简化的字符串过滤
    "compact": "COMPACT",      # 当前默认显示
    "trading": "TRADING",      # 突出显示bid/ask
    "analysis": "ANALYSIS",    # 显示所有技术指标
    "options": "OPTIONS",      # 期权优化显示
    "full": "FULL",           # 完整显示
}
```

在 `cli.py` 中的 formatTicker 添加模式参数，根据模式调整字段宽度和显示内容。

---

## ⚙️ 启动参数实现

修改 `icli/__main__.py` 添加启动参数：

```python
import argparse

# 添加参数解析
parser = argparse.ArgumentParser(description='ICLI - Interactive Brokers CLI')
parser.add_argument(
    '--position-preset', '-p',
    choices=['minimal', 'compact', 'trading', 'analysis', 'full'],
    default='auto',
    help='Position display preset (default: auto)'
)
parser.add_argument(
    '--quote-preset', '-q',
    choices=['minimal', 'compact', 'trading', 'analysis', 'options', 'scalping', 'full'],
    default='compact',
    help='Quote display preset (default: compact)'
)
parser.add_argument(
    '--position-columns',
    type=str,
    help='Custom position columns (comma-separated)'
)

args = parser.parse_args()

# 应用到 display_config
from icli.display_config import display_config
if args.position_preset != 'auto':
    display_config.position_preset = args.position_preset
if args.position_columns:
    display_config.position_columns = args.position_columns.split(',')
if args.quote_preset:
    display_config.quote_preset = args.quote_preset
```

**使用示例**：
```bash
# 启动时指定预设
poetry run icli --position-preset minimal --quote-preset trading

# 自定义列
poetry run icli --position-columns sym,position,PNL,%

# 组合使用
poetry run icli -p compact -q scalping
```

---

## 📋 推荐实施顺序

1. **立即**：更新 POSITION_PRESETS（已完成）
2. **本周**：添加启动参数到 __main__.py
3. **下周**：定义 QUOTE_PRESETS 字段映射
4. **后续**：逐步重构 formatTicker() 支持列选择

---

## 🎯 总结建议

### 报价区预设（按使用频率）

1. **compact** (默认) - 日常交易，显示核心价格+盘口
2. **trading** - 日内交易，添加EMA趋势+ATR
3. **scalping** - 超短线，极简快速
4. **options** - 期权专用，希腊值优先
5. **analysis** - 技术分析，完整指标
6. **minimal** - 超窄终端应急
7. **full** - 完整显示所有字段

### 字段优先级

**必备** (minimal): sym, last, bid, ask, change, %
**推荐** (compact): + bidSize, askSize, volume
**进阶** (trading): + ema100, trend, atr, spread
**完整** (analysis): + ema300, high, low, vwap, close
**期权** (options): underlying, iv, delta, mark, dte

选择哪种实现方式？
