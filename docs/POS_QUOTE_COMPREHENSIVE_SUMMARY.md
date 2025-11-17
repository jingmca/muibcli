# Position和Quote区完整修改总结

**修改范围**: 持仓区（positions）+ 报价区（quotes）
**核心功能**: Preset系统 + OCC期权格式
**文件涉及**: positions.py, cli.py, display_config.py, helpers.py, __main__.py

---

## 📍 PART 1: Position区（持仓）修改总结

### 1.1 单个持仓显示（All Positions）

#### 场景A: Preset模式 (minimal/compact/trading/analysis)

**触发条件**:
- 显式设置preset (`--position-preset` 或 `display positions.preset`)
- 或终端宽度 <= 120

**代码位置**: `positions.py` line 376-459

**显示特点**:
```python
# 使用preset指定的列
POSITION_PRESETS = {
    "minimal": ["sym", "position", "avgCost", "mktPrice", "PNL", "%"],
    "compact": ["sym", "position", "avgCost", "mktPrice", "mktValue", "PNL", "%", "w%"],
    "trading": ["sym", "position", "avgCost", "mktPrice", "closeOrder", "PNL", "dailyPNL", "%", "w%"],
    "analysis": ["sym", "position", "marketValue", "totalCost", "unrealizedPNL", "dailyPNL", "%", "w%"],
}
```

**期权符号格式**: ✅ **OCC格式**
```
sym列显示: AAPL251121C00265000 (19字符)
而不是: AAPL
```

**实现代码** (line 413-429):
```python
for idx in compact_df.index:
    if idx != "Total":
        row = allPositions.loc[idx]
        if row["type"] in {"OPT", "FOP"} and pd.notna(row.get("strike")):
            # Use OCC format
            compact_df.at[idx, "sym"] = format_option_symbol(
                symbol, date_str, strike, pc, "occ"
            )
```

**示例输出** (trading preset):
```
  sym                   position  avgCost  mktPrice closeOrder    PNL dailyPNL      %     w%
  AAPL251121C00265000         1     7.58      9.35             176.55   -48.54  23.28  12.89
  AAPL251121P00250000         1     6.11      0.20            -591.05     2.00 -96.73 -43.16
Total                         2    13.69      9.55            -414.50   -46.54 -35.66 -65.93
```

---

#### 场景B: Full模式（宽终端，无preset）

**触发条件**:
- 终端宽度 > 120
- 且preset = "auto" 或 "full"

**代码位置**: `positions.py` line 463-486

**显示特点**:
- 显示所有列（包括type, PC, date, strike, conId, exch等）
- 隐藏部分列: closeOrder, closeOrderValue, closeOrderProfit, conId, exch

**期权符号格式**: ✅ **OCC格式** (新增修复)

**实现代码** (line 468-481):
```python
# Wide terminal - show more details
display_df = allPositions.drop(columns=drop_cols).copy()

# Format option symbols to OCC even in full/wide mode
for idx in display_df.index:
    if idx != "Total":
        row = allPositions.loc[idx]
        if row["type"] in {"OPT", "FOP"} and pd.notna(row.get("strike")):
            # Use OCC format for options in wide display too
            display_df.at[idx, "sym"] = format_option_symbol(
                symbol, date_str, strike, pc, "occ"
            )
```

**示例输出** (full模式):
```
type  sym                   PC    date      strike  position  avgCost  mktPrice  mktValue  totalCost  PNL        dailyPNL   %       w%
OPT   AAPL251121C00265000   C   20251121   265.0        1      7.58      9.35     935.00    758.45   176.55     -48.54   23.28   12.89
OPT   AAPL251121P00250000   P   20251121   250.0        1      6.11      0.20      20.00    611.05  -591.05       2.00  -96.73  -43.16
```

---

### 1.2 期权组合显示（Spread）

#### 场景C: 窄终端Spread显示 (<=120)

**触发条件**: 检测到同symbol同到期日有多个期权腿

**代码位置**: `positions.py` line 488-545

**显示特点**:
- 使用compact列: ["type", "PC", "strike", "position", "avgCost", "mktPrice", "mktValue", "PNL", "%", "w%"]
- 日期格式: MM/DD

**期权符号格式**: ❌ **不使用OCC**（保留原sym）
- 因为已经有PC和strike列，sym只显示标的符号

**示例输出**:
```
[AAPL 11/21] Spread
type  PC  strike  position  avgCost  mktPrice  mktValue    PNL      %     w%
OPT   C   265.0          1     7.58      9.35    935.00  176.55  23.28  12.89
OPT   P   250.0          1     6.11      0.20     20.00 -591.05 -96.73 -43.16
Total               2    13.69      9.55    955.00 -414.50 -35.66 -65.93
```

---

#### 场景D: 宽终端Spread显示 (>120)

**触发条件**: 同上，但终端宽度>120

**代码位置**: `positions.py` line 546-565

**显示特点**:
- 显示所有列（full格式）

**期权符号格式**: ✅ **OCC格式** (新增修复)

**实现代码** (line 547-565):
```python
else:
    # Wide terminal spread display - also format option symbols to OCC
    spread_occ = spread.copy()

    # Format option symbols to OCC format
    for idx in spread_occ.index:
        if idx != "Total":
            row = spread.loc[idx]
            if row["type"] in {"OPT", "FOP"} and pd.notna(row.get("strike")):
                spread_occ.at[idx, "sym"] = format_option_symbol(
                    symbol, date_str, strike, pc, "occ"
                )

    printFrame(spread_occ, f"[{sym}] Potential Spread Identified")
```

**示例输出**:
```
[AAPL] Potential Spread Identified
type  sym                   PC    date      strike  position  avgCost  mktPrice  mktValue  totalCost  PNL        %       w%
OPT   AAPL251121C00265000   C   20251121   265.0        1      7.58      9.35     935.00    758.45   176.55   23.28   12.89
OPT   AAPL251121P00250000   P   20251121   250.0        1      6.11      0.20      20.00    611.05  -591.05  -96.73  -43.16
Total                                             2    13.69      9.55     955.00  1,369.49 -414.50  -35.66  -65.93
```

---

### 1.3 Position区修改汇总表

| 场景 | 触发条件 | 列数/内容 | 期权符号 | 代码位置 |
|------|----------|----------|----------|----------|
| **Preset显示** | preset≠auto/full 或 width≤120 | 6-9列（根据preset） | ✅ OCC | line 376-459 |
| **Full显示** | width>120 且 preset=auto/full | 所有列（除5个隐藏列） | ✅ OCC | line 463-486 |
| **窄Spread** | 检测到spread 且 width≤120 | 10列compact | ❌ 原sym | line 488-545 |
| **宽Spread** | 检测到spread 且 width>120 | 所有列full | ✅ OCC | line 546-565 |

---

## 📡 PART 2: Quote区（报价）修改总结

### 2.1 股票/ETF报价

**代码位置**: `cli.py` line 4826-4897

#### Preset模式对比

| Preset | 字段数 | 显示内容 | 宽度估算 | 代码行 |
|--------|--------|----------|----------|--------|
| **minimal** | 4 | sym, price, bid x ask, change% | ~50字符 | 4836-4843 |
| **compact** | 5 | sym, ema100, trend, price±spread, bid/ask+size | ~70字符 | 4844-4852 |
| **scalping** | 5 | 同compact | ~70字符 | 4844-4852 |
| **trading** | 7 | sym, ema100>ema300, price±spread, high/low, bid/ask+size, atr | ~100字符 | 4853-4863 |
| **analysis** | 7 | sym, ema100(diff)>ema300(diff), price±spread, vwap, bid/ask | ~120字符 | 4864-4874 |
| **full** | 15 | 所有字段（原始格式） | ~180字符 | 4875-4894 |

#### 详细示例

**Minimal** (~50字符):
```
SPY          675.57     675.74 x     675.75  -0.24%    -1.60
```

**Compact** (~70字符):
```
SPY          675.57 =     675.75 ±  0.00     675.74 x    280     675.75 x    600
│            │      │      │          │         │                │
│            │      │      │          │         └─ ask price x ask size
│            │      │      │          └─ bid price x bid size
│            │      │      └─ mark price ± spread
│            │      └─ trend (= < >)
│            └─ ema100
└─ symbol
```

**Trading** (~100字符):
```
SPY          675.57 >     675.40     675.75 ±  0.00     680.86     674.22     675.74 x    280     675.75 x    600 ( 0.24)
│            │      │      │          │          │         │          │                │                │         │
│            │      │      │          │          │         │          │                │                │         └─ ATR
│            │      │      │          │          │         │          │                │                └─ ask
│            │      │      │          │          │         │          │                └─ bid
│            │      │      │          │          │         │          └─ low
│            │      │      │          │          │         └─ high
│            │      │      │          │          └─ mark price ± spread
│            │      │      │          └─ ema300
│            │      │      └─ trend
│            │      └─ ema100
└─ symbol
```

**Full** (~180字符，原格式):
```
SPY          675.57 (  0.17) =     675.57 (  0.17)     675.75 ±  0.00     680.86     674.22     675.74 x    280     675.75 x    600 ( 0.18) ( -0.24%    -1.60)     683.38 ( 0.12 s) @ (0.35 s)
```

---

### 2.2 期权报价（单腿）

**代码位置**: `cli.py` line 4633-4720

**期权符号格式**: ✅ **所有模式都使用OCC**

#### Preset模式对比

| Preset | 字段数 | 显示内容 | 宽度估算 | 代码行 |
|--------|--------|----------|----------|--------|
| **minimal** | 4 | sym, mark, bid x ask, change% | ~40字符 | 4646-4653 |
| **compact** | 5 | sym, [u], [d], mark±spread, bid/ask+size | ~65字符 | 4654-4662 |
| **scalping** | 5 | 同compact | ~65字符 | 4654-4662 |
| **trading** | 7 | sym, [u ITM], [d], ema>ema, mark±spread, bid/ask+size, dte | ~80字符 | 4663-4674 |
| **options** | 6 | sym, [u ITM %], [iv d g t], mark±spread, bid/ask+size, dte | ~95字符 | 4675-4687 |
| **analysis** | 7 | sym, [u], ema details, mark±spread, vwap, bid/ask, dte | ~85字符 | 4688-4699 |
| **full** | 14 | 所有字段（原始格式） | ~180字符 | 4700-4717 |

#### 详细示例

**Minimal** (~40字符):
```
AAPL251121C00265000    5.80    5.75 x   5.85  +10.5%
```

**Compact** (~65字符):
```
AAPL251121C00265000  [u 225.5] [d+0.65]   5.80± 0.15   5.75x   10   5.85x   15
│                     │          │          │             │            │
│                     │          │          │             │            └─ ask x askSize
│                     │          │          │             └─ bid x bidSize
│                     │          │          └─ mark ± spread
│                     │          └─ delta
│                     └─ underlying price
└─ OCC symbol
```

**Trading** (~80字符):
```
AAPL251121C00265000  [u 225.5 I] [d+0.65]   5.25>  5.10   5.80± 0.15   5.75x   10   5.85x   15  8d
│                     │           │          │       │      │             │            │         │
│                     │           │          │       │      │             │            │         └─ days to expiry
│                     │           │          │       │      │             │            └─ ask
│                     │           │          │       │      │             └─ bid
│                     │           │          │       │      └─ mark ± spread
│                     │           │          │       └─ ema300
│                     │           │          └─ ema100 > (trend)
│                     │           └─ delta
│                     └─ underlying + ITM flag
└─ OCC symbol
```

**Options** (~95字符，含完整希腊值):
```
AAPL251121C00265000  [u 225.5 I +2.5%] [iv0.25 d+0.65 g0.03 t-0.15]   5.80± 0.15   5.75x   10   5.85x   15  8d
│                     │                 │                              │             │            │         │
│                     │                 │                              │             │            │         └─ DTE
│                     │                 │                              │             │            └─ ask
│                     │                 │                              │             └─ bid
│                     │                 │                              └─ mark ± spread
│                     │                 └─ IV, Delta, Gamma, Theta
│                     └─ underlying + ITM + % from strike
└─ OCC symbol
```

**Full** (~180字符，原格式):
```
AAPL251121C00265000  : [u  225.50 (I   +2.50%)] [iv 0.25] [d +0.65]   5.65=  5.65   5.80±  0.05     5.75 x   447     5.85 x   252       ( 0.10) ( 2s ago) (s  260.20 @   +5.15) (8.00 d)
```

---

### 2.3 期权组合报价（Spread/Bag）

**状态**: ❌ **未修改**

**原因**:
- Spread报价使用多行格式，每腿单独显示
- 已经很紧凑，不需要preset
- 保持现有显示逻辑

**示例**（未变）:
```
   BUY   CALL    1 AAPL 240816C00220000
   SELL  CALL    1 AAPL 240816C00225000
```

---

## 🔑 关键修改点总结

### Position区（3处修改）

| # | 位置 | 修改内容 | 状态 |
|---|------|----------|------|
| 1 | line 376-394 | Preset优先级逻辑 + 移除强制type列 | ✅ 完成 |
| 2 | line 413-429 | Preset模式期权OCC格式化 | ✅ 完成 |
| 3 | line 468-481 | Full模式期权OCC格式化 | ✅ 完成 |
| 4 | line 547-565 | Spread显示期权OCC格式化 | ✅ 完成 |

### Quote区（2处修改）

| # | 位置 | 修改内容 | 状态 |
|---|------|----------|------|
| 1 | line 4633-4720 | 期权报价preset + OCC格式 | ✅ 完成 |
| 2 | line 4826-4897 | 股票报价preset | ✅ 完成 |

---

## 📋 使用场景速查表

### 我想看紧凑的持仓
```bash
icli -p minimal
# 或
display positions.preset minimal
pos
```
**结果**: 6列显示，期权使用OCC符号

---

### 我想看紧凑的报价
```bash
icli -q compact
# 或
display quotes.preset compact
```
**结果**:
- 股票: ~70字符
- 期权: ~65字符（OCC符号）

---

### 我想看日内交易重点信息
```bash
icli -p trading -q trading
```
**结果**:
- 持仓: 9列（含closeOrder, dailyPNL）
- 股票报价: 含ema趋势、high/low、ATR
- 期权报价: 含ema趋势、ITM标志、DTE

---

### 我想看完整的期权希腊值
```bash
icli -q options
add AAPL251219C00220000
```
**结果**: 显示IV, Delta, Gamma, Theta

---

### 我想看所有信息（调试）
```bash
icli -p full -q full
```
**结果**:
- 持仓: 显示所有列（含type, PC, date, strike）
- 报价: 显示所有字段（~180字符）

---

## ⚙️ 配置优先级

```
命令行参数 > display命令 > 环境变量 > 默认值
     -p           display         ICLI_*      auto
     -q      positions.preset                compact
```

---

## 🎯 设计原则总结

### 期权符号OCC格式
- ✅ **所有期权符号统一使用OCC** (AAPL251219C00220000)
- ✅ 适用于: 持仓（所有模式）、报价（所有模式）、Spread（宽终端）
- ❌ 例外: Spread窄终端（因为已有PC/strike列）

### Preset系统
- ✅ **持仓**: 5种preset（minimal/compact/trading/analysis/full）
- ✅ **报价**: 7种preset（minimal/compact/trading/scalping/analysis/options/full）
- ✅ **优先级**: 显式preset > 终端宽度
- ✅ **一致性**: 同类资产（股票/期权）使用相同字段结构

### 宽度适配
- **窄终端** (<80): 推荐minimal
- **中等终端** (80-120): 推荐compact/trading
- **宽终端** (>120): 可用所有preset，默认会走preset逻辑

---

## 📦 Git提交历史

```bash
4581d24 - Add stock quote preset support and fix option OCC format in all views
30cfa5a - Add documentation for display preset system
051c6af - Implement quote preset system for option display
fcb52dc - Remove forced 'type' column from preset displays
8b0d31a - Fix position preset not applying on wide terminals
f809866 - Use OCC format for option display in positions and quotes
```

---

## 🧪 测试覆盖

### Position区测试
- [x] Preset模式（minimal/compact/trading/analysis）
- [x] Full模式（宽终端）
- [x] 期权OCC格式（所有模式）
- [x] Spread显示（窄/宽终端）
- [x] Type列移除（preset模式）

### Quote区测试
- [x] 股票minimal/compact/trading/analysis/full
- [x] 期权minimal/compact/trading/options/analysis/full
- [x] 期权OCC格式（所有模式）
- [x] 命令行参数 (-p/-q)
- [x] 运行时切换 (display命令)

---

**文档版本**: v1.0
**最后更新**: 2025-11-14
**完整性**: ✅ 所有场景已覆盖
