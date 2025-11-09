# ICLI 快速入门指南

## 欢迎使用ICLI

ICLI (Interactive CLI for Interactive Brokers) 是一个强大的命令行交易工具，专为快速交易而设计。本指南将帮助你在15分钟内开始使用ICLI。

## 5分钟快速开始

### 1. 启动ICLI

```bash
# 连接到IBKR Gateway（实盘）
poetry run icli

# 连接到模拟账户
ICLI_IBKR_PORT=4002 poetry run icli
```

### 2. 第一次使用 - 查看帮助

```bash
# 查看快速参考
hh

# 查看所有命令
?

# 查看特定命令帮助
man buy
```

### 3. 查看账户信息

```bash
# 查看持仓
positions

# 查看现金余额
cash

# 查看账户总览
balance
```

### 4. 添加实时行情

```bash
# 添加行情（必须先添加才能交易）
add SPY QQQ AAPL TSLA

# 查看行情
# 行情会自动显示在终端
```

### 5. 第一笔交易（预览模式）

```bash
# 预览买单（不实际提交）
buy SPY 1 MID preview

# 预览卖单
sell SPY 1 MID preview
```

## 10分钟核心功能

### 基础交易命令

```bash
# 1. 市价单（立即成交）
buy SPY 100 MKT

# 2. 限价单（指定价格）
buy AAPL 100 LMT @ 150.50 GTC

# 3. 中间价单（买卖价差中间）
buy AAPL 100 MID

# 4. 算法单（智能执行）
buy AAPL 100 AF @ 150.50

# 5. 卖出
sell AAPL 100 MID

# 6. 清仓
evict AAPL 0 0 MID
```

### 订单管理

```bash
# 查看活跃订单
orders

# 取消订单（交互式选择）
cancel

# 取消所有订单
cancel *

# 修改订单
modify
```

### 查看执行记录

```bash
# 今日执行记录
executions

# 详细执行信息
executions -v
```

## 15分钟进阶功能

### 止盈止损订单

```bash
# 对称止盈止损（±5）
buy AAPL 100 AF @ 150 ± 5
# 止盈：155，止损：145

# 不对称止盈止损
buy AAPL 100 AF @ 150 [profit:157] [stop:147]
# 止盈：157（+7），止损：147（-3），盈亏比 7:3

# 仅止损
buy AAPL 100 AF @ 150 [stop:145]

# 仅止盈
buy AAPL 100 AF @ 150 [profit:155]
```

### 按金额买入

```bash
# 买入价值$10,000的AAPL
buy AAPL $10000 MID

# 系统自动计算股数：$10,000 / AAPL当前价
```

### 批量操作

```bash
# 批量买入多个股票
expand buy {SPY,QQQ,IWM} 100 MID preview

# 批量添加行情
add SPY QQQ AAPL MSFT TSLA NVDA
```

### 计算器功能

```bash
# 计算可买股数（33%保证金）
(/ :BP3 AAPL)

# 计算资金增长
(grow :AF 300)

# 计算总价值
(* AAPL 100)
```

## 常用命令速查表

### 账户查询

| 命令 | 功能 | 示例 |
|------|------|------|
| `positions` | 查看持仓 | `positions` |
| `cash` | 查看现金 | `cash` |
| `balance` | 账户总览 | `balance` |
| `balance SMA` | 保证金信息 | `balance SMA` |
| `pnl` | 盈亏统计 | `pnl` |

### 行情管理

| 命令 | 功能 | 示例 |
|------|------|------|
| `add` | 添加行情 | `add SPY QQQ AAPL` |
| `remove` | 移除行情 | `remove SPY` |
| `qquote` | 快速查询 | `qquote AAPL` |
| `depth` | 市场深度 | `depth AAPL` |
| `qlist` | 当前行情列表 | `qlist` |

### 交易执行

| 命令 | 功能 | 示例 |
|------|------|------|
| `buy` | 买入 | `buy AAPL 100 MID` |
| `sell` | 卖出 | `sell AAPL 100 MID` |
| `evict` | 清仓 | `evict AAPL 0 0 MID` |
| `preview` | 预览订单 | `buy AAPL 100 MID preview` |

### 订单管理

| 命令 | 功能 | 示例 |
|------|------|------|
| `orders` | 活跃订单 | `orders` |
| `cancel` | 取消订单 | `cancel` |
| `cancel *` | 取消所有 | `cancel *` |
| `modify` | 修改订单 | `modify` |
| `executions` | 执行记录 | `executions` |

### 帮助系统

| 命令 | 功能 | 示例 |
|------|------|------|
| `hh` | 快速参考 | `hh` |
| `?` | 命令列表 | `?` |
| `man` | 详细手册 | `man buy` |
| `<cmd>?` | 命令帮助 | `buy?` |

## 订单类型详解

### 常用订单类型

| 类型 | 全称 | 特点 | 适用场景 |
|------|------|------|---------|
| `MKT` | Market | 市价单，立即成交 | 快速进出场 |
| `LMT` | Limit | 限价单，指定价格 | 精确控制价格 |
| `MID` | Midprice | 中间价，节省价差 | 非紧急订单 |
| `AF` | Adaptive Fast | 算法快速单 | 日内快速交易 |
| `AS` | Adaptive Slow | 算法慢速单 | 大额减少冲击 |

### 订单参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `GTC` | 持续有效直到取消 | `buy AAPL 100 LMT @ 150 GTC` |
| `DAY` | 仅当日有效（默认） | `buy AAPL 100 LMT @ 150 DAY` |
| `RTH` | 仅常规交易时间 | `buy AAPL 100 LMT @ 150 RTH` |
| `preview` | 预览不提交 | `buy AAPL 100 MID preview` |

## 实战场景

### 场景1：日内快速交易

```bash
# 早盘准备
add SPY QQQ          # 添加行情
positions            # 检查持仓
cash                 # 确认现金

# 看到机会，快速入场
buy SPY 100 AF @ 450 ± 2

# 持仓管理
orders               # 检查订单状态
positions            # 查看持仓盈亏

# 收盘前清仓
evict SPY 0 0 MKT

# 复盘
executions           # 查看今日交易
pnl                  # 查看盈亏统计
```

### 场景2：波段交易建仓

```bash
# 1. 在支撑位挂单
add AAPL
buy AAPL 500 LMT @ 145.00 GTC RTH

# 2. 等待成交（可能数天）...

# 3. 成交后自动设置止盈止损
sell AAPL 500 LMT @ 155.00 GTC RTH  # 止盈
sell AAPL 500 STP @ 142.00 GTC      # 止损

# 4. 持有等待...

# 5. 定期检查
orders               # 检查订单
positions            # 检查持仓
```

### 场景3：分批建仓

```bash
# 1. 计划在145-150区间买入2000股
add AAPL

buy AAPL 500 LMT @ 150.00 GTC RTH
buy AAPL 500 LMT @ 148.00 GTC RTH
buy AAPL 500 LMT @ 146.00 GTC RTH
buy AAPL 500 LMT @ 145.00 GTC RTH

# 2. 等待分批成交

# 3. 定期检查
orders               # 查看哪些成交了
positions            # 查看持仓成本
cancel *             # 取消未成交的（如果需要）
```

### 场景4：财报交易

```bash
# 财报盘前7:00发布

# 1. 盘前准备（6:00-9:00）
add AAPL
qquote AAPL          # 查看盘前价格

# 2. 盘前入场（允许盘前交易，不加RTH）
buy AAPL 100 LMT @ 155.00 GTC

# 3. 设置止损
sell AAPL 100 TRAIL @ 3.00 GTC

# 4. 盘中管理
positions            # 监控盈亏
orders               # 检查止损订单
```

## 交易策略模板

### 模板1：日内突破策略

```bash
# 设置
add SPY
positions

# 执行（突破450）
buy SPY 100 AF @ 450.50 ± 2

# 结果
# 入场：450.50
# 止盈：452.50（+2）
# 止损：448.50（-2）
# 盈亏比：1:1
```

### 模板2：波段高盈亏比

```bash
# 设置
add AAPL

# 执行（支撑位145）
buy AAPL 500 LMT @ 145 [profit:155] [stop:142] GTC RTH

# 结果
# 入场：145
# 止盈：155（+10，+6.9%）
# 止损：142（-3，-2.1%）
# 盈亏比：3.33:1
```

### 模板3：按金额建仓

```bash
# 设置
add AAPL MSFT NVDA

# 每个股票$10,000
buy AAPL $10000 MID
buy MSFT $10000 MID
buy NVDA $10000 MID

# 统一止损（按价格）
sell AAPL <qty> STP @ <stop_price> GTC
sell MSFT <qty> STP @ <stop_price> GTC
sell NVDA <qty> STP @ <stop_price> GTC
```

## 风险管理清单

### 交易前检查

- [ ] 确认账户余额充足（`cash`）
- [ ] 添加标的行情（`add`）
- [ ] 确定入场价格和数量
- [ ] 计算止损位置
- [ ] 确保单笔风险≤2%账户
- [ ] 使用`preview`预览订单

### 交易中管理

- [ ] 定期检查持仓（`positions`）
- [ ] 监控活跃订单（`orders`）
- [ ] 盈利后考虑移动止损
- [ ] 不要随意移动原定止损
- [ ] 控制总持仓风险≤10%

### 交易后复盘

- [ ] 查看执行记录（`executions`）
- [ ] 分析盈亏统计（`pnl`）
- [ ] 清理未使用订单（`cancel *`）
- [ ] 移除不需要的行情（`remove`）
- [ ] 记录交易日志

## 常见错误和避免方法

### 错误1：忘记添加行情

```bash
# ❌ 错误
buy AAPL 100 MID
# Error: No market data for AAPL

# ✅ 正确
add AAPL
buy AAPL 100 MID
```

### 错误2：AF订单使用GTC

```bash
# ❌ 错误
buy AAPL 100 AF @ 150 GTC
# Error: AF不支持GTC

# ✅ 正确
buy AAPL 100 LMT @ 150 GTC
```

### 错误3：忘记设置止损

```bash
# ❌ 错误（没有止损）
buy AAPL 100 AF @ 150

# ✅ 正确（有止损保护）
buy AAPL 100 AF @ 150 [stop:145]
```

### 错误4：实际交易前未预览

```bash
# ❌ 错误（直接提交）
buy AAPL 100 AF @ 150 ± 5
# 订单立即提交！

# ✅ 正确（先预览）
buy AAPL 100 AF @ 150 ± 5 preview
# 检查订单参数后再提交
buy AAPL 100 AF @ 150 ± 5
```

### 错误5：止损位置不合理

```bash
# ❌ 错误（止损太近，容易触发）
buy AAPL 100 @ 150 [stop:149.5]

# ✅ 正确（基于技术位或ATR）
buy AAPL 100 @ 150 [stop:147]
```

## 键盘快捷键和技巧

### 命令行技巧

```bash
# 上下箭头 - 历史命令
↑/↓

# Tab - 命令补全
bu<Tab>  → buy

# Ctrl+R - 搜索历史
Ctrl+R "buy AAPL"

# Ctrl+C - 取消当前输入
Ctrl+C

# Ctrl+L - 清屏
Ctrl+L
```

### 快速命令

```bash
# 使用别名
b AAPL 100 MID      # b是buy的别名
s AAPL 100 MID      # s是sell的别名

# 使用历史命令
!!                  # 重复上一条命令
!buy                # 重复最近的buy命令
```

## 日常使用流程

### 早盘流程

```bash
# 1. 启动ICLI
poetry run icli

# 2. 检查账户
positions            # 持仓
cash                 # 现金
orders               # 昨日未成交订单

# 3. 添加今日关注
add SPY QQQ AAPL TSLA

# 4. 开始交易
# ...
```

### 盘中流程

```bash
# 定期检查（每30分钟或每小时）
positions            # 持仓盈亏
orders               # 订单状态

# 根据需要调整
modify               # 修改订单
cancel               # 取消订单
```

### 收盘流程

```bash
# 1. 检查持仓
positions

# 2. 决定是否持仓过夜
evict <symbol> 0 0 MKT  # 平仓

# 3. 清理订单
cancel *             # 取消所有DAY订单（自动）

# 4. 复盘
executions           # 今日交易
pnl                  # 盈亏统计

# 5. 退出
exit
```

## 学习资源

### 内置帮助

```bash
hh                   # 快速参考
?                    # 命令列表
man <command>        # 详细手册
```

### 文档目录

```bash
docs/
├── ORDER_TYPES.md        # 订单类型详解
├── GTC_RTH_USAGE.md      # GTC和RTH参数
├── BRACKET_ORDERS.md     # 止盈止损订单
├── HELP_SYSTEM.md        # 帮助系统使用
└── QUICK_START.md        # 本文档
```

### 在线资源

- [IBKR API文档](https://interactivebrokers.github.io/tws-api/)
- [项目GitHub](https://github.com/mattsta/icli)
- [IBKR交易者大学](https://www.interactivebrokers.com/campus/)

## 进阶主题

准备好探索更多功能了吗？查看以下主题：

1. **条件触发** - `man ifthen`
   - 自动化交易策略
   - 价格触发、技术指标

2. **批量操作** - `man expand`
   - 批量买入多个股票
   - 批量管理订单

3. **期权交易** - `man chains`
   - 期权链查询
   - 期权希腊值

4. **计划任务** - `man schedule`
   - 定时执行命令
   - 自动化策略

5. **行情管理** - `man qadd`
   - 保存行情列表
   - 批量管理行情

## 安全提醒

### ⚠️ 重要：无确认机制

ICLI的设计理念是"you type it, it happens"（输入即执行），**没有二次确认**。

```bash
# 这条命令会立即提交！
buy AAPL 100 MKT

# 不会有"确认吗？"的提示
# 订单直接发送到IBKR
```

### 🛡️ 安全建议

1. **使用模拟账户练习**
   ```bash
   ICLI_IBKR_PORT=4002 poetry run icli
   ```

2. **始终使用preview测试**
   ```bash
   buy AAPL 100 MID preview  # 先预览
   buy AAPL 100 MID          # 确认无误后执行
   ```

3. **设置止损保护**
   ```bash
   buy AAPL 100 AF @ 150 [stop:145]  # 始终带止损
   ```

4. **控制单笔风险**
   ```bash
   # 单笔风险≤2%账户
   # 总持仓风险≤10%账户
   ```

5. **定期检查订单**
   ```bash
   orders               # 检查活跃订单
   cancel *             # 清理不需要的订单
   ```

## 快速参考卡片

### 最常用命令（前10）

```bash
positions            # 1. 查看持仓
cash                 # 2. 查看现金
orders               # 3. 查看订单
add SPY              # 4. 添加行情
buy AAPL 100 MID     # 5. 买入
sell AAPL 100 MID    # 6. 卖出
cancel               # 7. 取消订单
executions           # 8. 执行记录
man buy              # 9. 查看帮助
hh                   # 10. 快速参考
```

### 最常用订单

```bash
# 日内交易
buy <symbol> <qty> AF @ <price> ± <dist>

# 波段交易
buy <symbol> <qty> LMT @ <price> [profit:<p>] [stop:<s>] GTC RTH

# 快速买入
buy <symbol> <qty> MID

# 预览订单
buy <symbol> <qty> <type> @ <price> preview
```

## 下一步

恭喜！你已经掌握了ICLI的基础使用。接下来：

1. **在模拟账户练习** - 熟悉命令和流程
2. **阅读专题文档** - 深入理解订单类型和参数
3. **探索高级功能** - 条件触发、批量操作等
4. **实盘小额测试** - 从小额开始实盘交易
5. **逐步增加规模** - 建立信心后增加交易规模

**祝交易顺利！Happy Trading! 📈**

---

**问题反馈**：如有任何问题或建议，请查看项目GitHub或使用 `man <topic>` 查找答案。
