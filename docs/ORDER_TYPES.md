# ICLI 订单类型完整指南

## 概述

ICLI支持多种订单类型，每种类型都有其特定的用途和限制。本文档详细说明所有支持的订单类型、参数和使用场景。

## 订单类型对照表

| 用户输入 | IBKR订单类型 | 支持GTC | 支持RTH | 算法 | 说明 |
|---------|-------------|---------|---------|------|------|
| `LMT`, `LIMIT`, `LIM` | LMT | ✅ | ✅ | 无 | 标准限价单 |
| `MKT` | MKT | ✅ | ✅ | 无 | 市价单 |
| `AF` | LMT + Adaptive | ❌ (强制DAY) | ❌ (强制RTH) | Adaptive Fast | 自适应快速算法 |
| `AS` | LMT + Adaptive | ❌ (强制DAY) | ❌ (强制RTH) | Adaptive Slow | 自适应慢速算法 |
| `AP` | LMT + Adaptive | ❌ (强制DAY) | ❌ (强制RTH) | Adaptive Patient | 自适应耐心算法 |
| `MID`, `MIDPRICE` | MIDPRICE | ❌ (强制DAY) | ❌ (强制RTH) | Midprice | 买卖中间价 |
| `REL` | REL | ✅ | ✅ | 无 | 相对价格单 |
| `STP`, `STOP` | STP | ✅ | ✅ | 无 | 止损单 |
| `STPLMT` | STP LMT | ✅ | ✅ | 无 | 止损限价单 |
| `TRAIL` | TRAIL | ✅ | ✅ | 无 | 跟踪止损单 |
| `TWAP` | LMT + TWAP | ❌ (强制DAY) | 可选 | TWAP | 时间加权平均价格 |
| `VWAP` | LMT + VWAP | ❌ (强制DAY) | 可选 | VWAP | 成交量加权平均价格 |

## 1. 标准限价单 (LMT/LIMIT/LIM)

### 特点
- 最常用的订单类型
- 完全控制执行价格
- 支持GTC和RTH参数
- 适合所有市场条件

### 用法示例

```bash
# 基础限价单（默认GTC，允许盘前盘后）
buy AAPL 100 LMT @ 150.50

# 仅在常规交易时间执行（RTH）
buy AAPL 100 LIMIT @ 150.50 RTH

# 当日有效（DAY）
buy AAPL 100 LIM @ 150.50 DAY

# 持续有效直到取消（GTC）
buy AAPL 100 LMT @ 150.50 GTC

# GTC + RTH 组合
buy AAPL 100 LMT @ 150.50 GTC RTH

# 卖出限价单
sell TSLA 50 LMT @ 300.00 GTC
```

### 参数说明
- `@ price` - 限价价格（必需）
- `GTC` - Good Till Cancel，订单持续有效直到取消
- `DAY` - 仅当日有效
- `RTH` - Regular Trading Hours，仅在常规交易时间执行（9:30-16:00 ET）
- 不加RTH - 允许盘前盘后交易（4:00-20:00 ET）

### 使用场景
- 精确价格控制
- 长期挂单策略
- 波段交易入场
- 分批建仓/减仓

## 2. 市价单 (MKT)

### 特点
- 立即以市场最佳价格成交
- 无价格控制，可能滑点
- 支持GTC和RTH
- 适合快速进出场

### 用法示例

```bash
# 基础市价单
buy SPY 100 MKT

# 仅常规交易时间
buy SPY 100 MKT RTH

# 市价卖出
sell QQQ 200 MKT
```

### 注意事项
- 流动性差的股票可能有显著滑点
- 盘前盘后价差较大，建议使用RTH
- 不适合大额订单（建议使用TWAP/VWAP）

## 3. 自适应算法单 (AF/AS/AP)

### Adaptive Fast (AF) - 自适应快速

#### 特点
- IBKR智能算法，优先速度
- 自动强制DAY（当日有效）
- 自动强制RTH（常规交易时间）
- 不支持GTC参数

#### 用法示例

```bash
# 基础AF订单
buy AAPL 100 AF @ 150.00

# 带止盈止损的AF订单
buy AAPL 100 AF @ 150.00 ± 5

# AF不支持GTC，以下会失败
buy AAPL 100 AF @ 150.00 GTC  # ❌ 错误：AF强制DAY
```

#### 使用场景
- 日内交易快速入场
- 追逐突破行情
- 快速止损出场
- 流动性好的大盘股

### Adaptive Slow (AS) - 自适应慢速

#### 特点
- 优先价格而非速度
- 减少市场冲击
- 强制DAY + RTH
- 适合中大额订单

#### 用法示例

```bash
# 慢速建仓
buy TSLA 500 AS @ 250.00

# 分散卖出
sell NVDA 1000 AS @ 500.00
```

### Adaptive Patient (AP) - 自适应耐心

#### 特点
- 最大化价格优势
- 执行时间较长
- 可能部分成交
- 适合非紧急订单

#### 用法示例

```bash
# 耐心等待更好价格
buy META 200 AP @ 350.00
```

## 4. 中间价订单 (MID/MIDPRICE)

### 特点
- 使用买卖价差的中间价
- 强制DAY + RTH
- 减少买卖价差成本
- 可能需要时间成交

### 用法示例

```bash
# 基础中间价订单
buy AAPL 100 MID

# 中间价带止盈止损
buy AAPL 100 MIDPRICE ± 5

# 不需要指定价格，自动使用中间价
sell SPY 200 MID
```

### 计算方式
```
中间价 = (最佳买价 + 最佳卖价) / 2
```

### 使用场景
- 价差较大的股票
- 非紧急订单
- 降低交易成本
- 提高成交率

## 5. 相对价格单 (REL)

### 特点
- 相对于市场价的偏移量
- 支持GTC和RTH
- 自动跟随市场价格
- 适合动态定价

### 用法示例

```bash
# 相对卖价下方0.01
buy AAPL 100 REL @ -0.01

# 相对买价上方0.01
sell AAPL 100 REL @ 0.01
```

## 6. 止损单 (STP/STOP)

### 特点
- 价格触发后转为市价单
- 用于止损或突破入场
- 支持GTC和RTH
- 可能有滑点

### 用法示例

```bash
# 止损卖出（价格跌破145触发）
sell AAPL 100 STP @ 145.00 GTC

# 突破买入（价格涨破155触发）
buy AAPL 100 STOP @ 155.00 GTC
```

## 7. 止损限价单 (STPLMT)

### 特点
- 价格触发后转为限价单
- 控制止损滑点
- 支持GTC和RTH
- 可能不成交

### 用法示例

```bash
# 止损限价（触发价145，限价144）
sell AAPL 100 STPLMT @ 145 : 144 GTC
```

## 8. 跟踪止损单 (TRAIL)

### 特点
- 跟随市场价移动止损点
- 锁定利润，限制损失
- 支持GTC
- 可用金额或百分比

### 用法示例

```bash
# 跟踪止损$5
sell AAPL 100 TRAIL @ 5.00 GTC

# 跟踪止损5%
sell AAPL 100 TRAIL @ 5% GTC
```

## 9. 算法订单 (TWAP/VWAP)

### TWAP - 时间加权平均价格

#### 特点
- 均匀分散订单
- 减少市场冲击
- 适合大额订单
- 强制DAY

#### 用法示例

```bash
# TWAP订单，30分钟内执行
buy AAPL 10000 TWAP @ 150.00

# 指定结束时间
buy AAPL 10000 TWAP @ 150.00 end:16:00
```

### VWAP - 成交量加权平均价格

#### 特点
- 跟随市场成交量
- 减少对价格影响
- 大额订单最佳
- 强制DAY

#### 用法示例

```bash
# VWAP订单
buy TSLA 5000 VWAP @ 250.00

# 指定时间段
buy TSLA 5000 VWAP @ 250.00 start:10:00 end:15:00
```

## 订单参数详解

### 时间有效性 (Time In Force)

| 参数 | 说明 | 持续时间 | 适用场景 |
|------|------|----------|----------|
| `GTC` | Good Till Cancel | 直到取消或成交（最长90天） | 长期挂单，波段交易 |
| `DAY` | Day Order | 当日收盘前 | 日内交易，快速进出 |
| `IOC` | Immediate or Cancel | 立即成交，未成交部分取消 | 快速部分成交 |
| `FOK` | Fill or Kill | 必须全部成交否则取消 | 全部成交要求 |
| `GTD` | Good Till Date | 指定日期前有效 | 计划订单 |

### 交易时间限制

| 参数 | 说明 | 交易时间 |
|------|------|----------|
| 无RTH | 允许盘前盘后 | 4:00-20:00 ET |
| `RTH` | Regular Trading Hours | 9:30-16:00 ET |

### 止盈止损 (Bracket Orders)

```bash
# 基础语法
buy AAPL 100 AF @ 150 ± 5
#                      ^ 止损  ^ 止盈距离

# 完整语法
buy AAPL 100 AF @ 150 [stop:145] [profit:155]

# 仅止损
buy AAPL 100 AF @ 150 [stop:145]

# 仅止盈
buy AAPL 100 AF @ 150 [profit:155]
```

详见 [BRACKET_ORDERS.md](BRACKET_ORDERS.md)

## 订单类型选择指南

### 按交易风格选择

| 交易风格 | 推荐订单类型 | 原因 |
|---------|-------------|------|
| 日内交易 (Scalping) | AF, MID, MKT | 速度优先，快速进出 |
| 波段交易 (Swing) | LMT + GTC, REL | 价格控制，长期有效 |
| 大额交易 | TWAP, VWAP, AS | 减少市场冲击 |
| 自动化策略 | LMT + GTC, TRAIL | 无需人工干预 |

### 按市场条件选择

| 市场条件 | 推荐订单类型 | 原因 |
|---------|-------------|------|
| 高流动性 | MKT, AF | 滑点小，快速成交 |
| 低流动性 | LMT, MID, AP | 控制价格，耐心等待 |
| 高波动 | LMT, STPLMT | 避免滑点 |
| 价差大 | MID, AP | 节省价差成本 |

### 按紧急程度选择

| 紧急程度 | 推荐订单类型 | 预计成交时间 |
|---------|-------------|-------------|
| 极紧急 | MKT | 立即 |
| 紧急 | AF | 数秒 |
| 正常 | LMT, AS | 数分钟 |
| 不紧急 | AP, MID | 数十分钟 |
| 计划性 | TWAP, VWAP | 数小时 |

## 常见错误和解决方案

### 错误1：AF订单使用GTC参数
```bash
buy AAPL 100 AF @ 150 GTC  # ❌ 错误
```
**原因**：AF算法强制DAY，不支持GTC

**解决**：
```bash
# 使用标准限价单
buy AAPL 100 LMT @ 150 GTC  # ✅ 正确
```

### 错误2：MID订单盘后执行
```bash
buy AAPL 100 MID  # ❌ 盘后可能无法成交
```
**原因**：MID强制RTH，盘后不执行

**解决**：
```bash
# 盘后使用限价单
buy AAPL 100 LMT @ 150 GTC  # ✅ 正确
```

### 错误3：大额市价单滑点大
```bash
buy TSLA 10000 MKT  # ❌ 可能有显著滑点
```
**原因**：大额市价单会消耗多个价位的流动性

**解决**：
```bash
# 使用算法订单
buy TSLA 10000 VWAP @ 250  # ✅ 更好
buy TSLA 10000 AS @ 250    # ✅ 也可以
```

## 实战示例

### 场景1：日内快速入场
```bash
# 看到突破信号，立即入场
buy SPY 100 AF @ 450.50 ± 2

# 解释：
# - AF：快速成交
# - ± 2：自动止损448.50，止盈452.50
# - DAY + RTH：日内交易，自动失效
```

### 场景2：波段交易建仓
```bash
# 在支撑位挂单，耐心等待
buy AAPL 500 LMT @ 145.00 GTC RTH

# 解释：
# - LMT：精确价格控制
# - GTC：可以等待数天
# - RTH：避免盘前盘后价格异常
```

### 场景3：大额分散买入
```bash
# 避免市场冲击
buy NVDA 5000 VWAP @ 500.00

# 解释：
# - VWAP：跟随市场成交量
# - 全天执行，减少价格影响
# - 自动分批，优化成交价
```

### 场景4：止损保护
```bash
# 持有AAPL，设置跟踪止损
sell AAPL 100 TRAIL @ 5.00 GTC

# 解释：
# - TRAIL：跟随最高价下移
# - $5：始终保持$5止损距离
# - GTC：长期有效
```

### 场景5：突破策略
```bash
# 突破152入场，最高153止盈，最低150止损
buy AAPL 100 STP @ 152 [profit:153] [stop:150] GTC

# 解释：
# - STP @ 152：价格突破152触发
# - profit:153：到达153获利了结
# - stop:150：跌破150止损出场
```

## 订单监控和管理

### 查看活跃订单
```bash
orders           # 所有活跃订单
orders AAPL      # AAPL的订单
```

### 取消订单
```bash
cancel           # 交互式选择取消
cancel *         # 取消所有订单
cancel 123       # 取消订单ID 123
```

### 修改订单
```bash
modify           # 交互式修改订单
modify 123       # 修改订单ID 123
```

### 查看执行记录
```bash
executions       # 今日执行
executions -v    # 详细信息
executions AAPL  # AAPL的执行记录
```

## 参考资源

- [GTC和RTH使用详解](GTC_RTH_USAGE.md)
- [止盈止损订单详解](BRACKET_ORDERS.md)
- [快速入门指南](QUICK_START.md)
- [IBKR订单类型官方文档](https://www.interactivebrokers.com/en/index.php?f=4985)

## 总结

选择正确的订单类型对交易成功至关重要：

1. **日内交易** → AF, MID, MKT
2. **波段交易** → LMT + GTC
3. **大额订单** → TWAP, VWAP, AS
4. **价格控制** → LMT, STPLMT
5. **快速执行** → MKT, AF

记住：
- 不是所有订单类型都支持GTC
- 算法订单（AF, MID, TWAP, VWAP）有时间限制
- 始终考虑流动性和市场条件
- 使用预览功能测试订单：`buy AAPL 100 AF @ 150 preview`
