# ICLI 条件单功能说明

## 概述

ICLI支持两种类型的条件单功能：

1. **客户端条件单 (ifthen)** - 已实现 ✅
2. **IB API原生条件单 (OrderCondition)** - 待实现 ⚠️

## 1. 客户端条件单 (ifthen) - 已实现

### 功能描述

ICLI的`ifthen`系统是一个客户端实现的条件触发系统，当市场数据满足指定条件时，自动执行交易命令。

### 优势

- **功能强大**：支持复杂的技术指标条件
  - 价格条件：`last`, `bid`, `ask`, `high`, `low`
  - 技术指标：`ema`, `atr`, `vwap`
  - 期权希腊值：`delta`, `gamma`, `theta`, `vega`, `iv`
- **灵活组合**：可以组合多个条件
- **实时监控**：每次行情更新都会检查条件

### 缺点

- **需要客户端运行**：如果客户端断线，条件单会失效
- **网络依赖**：依赖行情数据流的稳定性

### 使用示例

#### 基础价格条件

```bash
# 当QQQ跌到500以下时，买入AAPL 100股
if QQQ last < 500: buy AAPL 100 MID

# 当AAPL涨到300以上时，卖出100股
if AAPL last > 300: buy AAPL -100 MID

# 使用bid/ask价格
if SPY bid < 670: buy SPY 100 AF
if SPY ask > 680: buy SPY -100 AF
```

#### 技术指标条件

```bash
# EMA交叉
if AAPL ema60 > ema300: buy AAPL 100 MID

# ATR条件
if AAPL atr > 5: buy AAPL 100 MID
```

#### GTC（持续有效）条件

使用`auto`命令创建持续有效的条件：

```bash
# 创建持续有效的条件单程序
auto if AAPL last > 300: buy AAPL -100 MID; if AAPL last < 280: buy AAPL 100 MID
```

### 管理命令

```bash
iflist          # 查看所有活跃的条件
ifrm <id>       # 删除指定条件
ifclear         # 清除所有条件
```

## 2. IB API原生条件单 (OrderCondition) - 待实现

### 功能描述

IB API原生支持服务器端条件单，订单提交到IBKR服务器后，由服务器监控条件并在满足时自动激活订单。

### 优势

- **服务器端执行**：即使客户端断线，条件单仍然有效
- **官方支持**：IBKR官方功能，稳定可靠
- **不占用API连接**：条件检查在服务器端进行

### 缺点

- **功能受限**：只支持IBKR提供的基本条件类型
- **不支持技术指标**：无法使用EMA、ATR等自定义指标

### IB API支持的条件类型

根据[IB API文档](https://interactivebrokers.github.io/tws-api/order_conditions.html)，支持以下条件类型：

1. **PriceCondition** - 价格条件
   - 监控指定合约的价格
   - 支持大于/小于比较
   - 可指定触发方式（Last, Bid, Ask等）

2. **TimeCondition** - 时间条件
   - 在指定时间触发

3. **MarginCondition** - 保证金条件
   - 基于账户保证金百分比

4. **ExecutionCondition** - 执行条件
   - 在其他订单执行后触发

5. **VolumeCondition** - 成交量条件
   - 基于成交量阈值

6. **PercentChangeCondition** - 百分比变化条件
   - 价格变化百分比

### ib_insync实现示例（参考）

```python
from ib_insync import *

# 创建价格条件：当QQQ价格低于500时触发
priceCondition = PriceCondition(
    condType=1,           # Price condition
    isMore=False,         # 小于（False）或大于（True）
    price=500,           # 触发价格
    conId=320227571,     # QQQ的合约ID
    exch='SMART',        # 交易所
    triggerMethod=0      # 0=Default, 1=DoubleBid/Ask, 2=Last, 3=DoubleLast
)

# 创建订单
order = LimitOrder('BUY', 100, 233.33)
order.conditions = [priceCondition]
order.conditionsIgnoreRth = False  # RTH时段外是否忽略条件
order.conditionsCancelOrder = False # 条件不满足时是否取消订单

# 提交订单
trade = ib.placeOrder(contract, order)
```

## 实现建议

### 短期方案（当前可用）

使用`ifthen`系统实现条件单功能：

```bash
# 方案1：单次触发
if QQQ last < 500: buy AAPL 100 MID GTC

# 方案2：持续监控（使用auto）
auto if QQQ last < 500: buy AAPL 100 MID GTC
```

**注意**：
- 需要保持客户端运行
- 建议在稳定的服务器或VPS上运行
- 使用`tmux`或`screen`保持会话

### 长期方案（未来开发）

可以考虑实现IB API原生条件单支持：

1. 创建新的订单命令参数，支持条件设置
2. 在`buy`/`sell`命令中添加条件参数解析
3. 将条件转换为IB API的`OrderCondition`对象
4. 提交带条件的订单到IBKR服务器

示例命令语法（概念设计）：

```bash
# 使用--condition参数
buy AAPL 100 MID GTC --condition "QQQ price < 500"

# 或者使用专门的条件单命令
condorder buy AAPL 100 MID if QQQ < 500
```

## 对比总结

| 特性 | ifthen (客户端) | IB API条件单 (服务器端) |
|------|----------------|----------------------|
| 实现状态 | ✅ 已实现 | ⚠️ 未实现 |
| 客户端依赖 | ❌ 需要持续运行 | ✅ 无需持续运行 |
| 条件类型 | ✅ 丰富（技术指标、希腊值等） | ⚠️ 受限（基本条件） |
| 稳定性 | ⚠️ 依赖网络和客户端 | ✅ 服务器端保证 |
| 学习曲线 | ✅ 简单直观 | ⚠️ 需要理解IB API |

## 使用建议

1. **日内交易**：使用`ifthen`，可以利用实时技术指标
2. **隔夜条件单**：考虑使用IB TWS的原生条件单功能（通过TWS界面设置）
3. **复杂策略**：使用`auto`创建持续监控的条件单程序
4. **简单价格触发**：两种方式都可以，`ifthen`更简单直接

## 参考资料

- [ICLI条件单示例](README.md#ifthen-predicates)
- [IB API条件单文档](https://interactivebrokers.github.io/tws-api/order_conditions.html)
- [ib_insync OrderCondition文档](https://ib-insync.readthedocs.io/api.html#order)
