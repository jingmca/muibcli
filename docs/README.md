# ICLI 文档中心

欢迎来到ICLI（Interactive Brokers CLI）文档中心！本目录包含完整的使用指南和参考文档。

## 📚 文档导航

### 🚀 快速开始

#### [快速入门指南](QUICK_START.md)
**适合人群**：新用户、初次使用ICLI
**内容概要**：
- 5分钟快速开始
- 10分钟核心功能
- 15分钟进阶功能
- 常用命令速查表
- 实战场景演示
- 安全提醒和最佳实践

**推荐学习路径**：从这里开始！

---

### 📖 核心文档

#### [订单类型完整指南](ORDER_TYPES.md)
**适合人群**：需要理解不同订单类型的用户
**内容概要**：
- 12种订单类型详解（LMT, MKT, AF, AS, MID, REL等）
- 订单类型对照表
- 参数说明（GTC, DAY, RTH等）
- 订单类型选择指南
- 实战示例和常见错误

**关键主题**：
- 限价单 vs 市价单 vs 算法单
- 日内交易 vs 波段交易订单选择
- 大额订单执行策略（TWAP, VWAP）

---

#### [GTC和RTH参数使用详解](GTC_RTH_USAGE.md)
**适合人群**：需要理解订单时间参数的用户
**内容概要**：
- GTC（Good Till Cancel）详解
- RTH（Regular Trading Hours）详解
- 四种组合方式（GTC+RTH, DAY+RTH等）
- 支持情况和限制
- 实战案例和最佳实践

**关键主题**：
- 为什么AF不支持GTC？
- 何时使用RTH？
- 盘前盘后交易考虑
- 长期挂单策略

---

#### [止盈止损订单详解](BRACKET_ORDERS.md)
**适合人群**：需要自动化风险管理的用户
**内容概要**：
- Bracket Order工作原理
- ± 语法和 [profit:] [stop:] 语法
- 盈亏比策略（1:1, 2:1, 3:1, 5:1+）
- 止损类型选择（固定、限价、跟踪）
- 高级技巧（分批止盈、移动止损）

**关键主题**：
- 如何设置合理的止损位置
- 盈亏比与胜率的关系
- 日内 vs 波段止盈止损策略
- 风险管理原则（单笔≤2%，总持仓≤10%）

---

#### [帮助系统使用指南](HELP_SYSTEM.md)
**适合人群**：想要充分利用内置帮助的用户
**内容概要**：
- 三层帮助系统（hh, ?, man）
- 命令对比和使用场景
- 模糊搜索和别名支持
- 学习工作流和最佳实践

**关键主题**：
- 如何快速查找命令
- 如何学习新命令
- 如何诊断问题

---

## 📋 文档使用指南

### 按角色选择

#### 新手用户
推荐阅读顺序：
1. ✅ [快速入门指南](QUICK_START.md) - 必读
2. ✅ [帮助系统使用指南](HELP_SYSTEM.md) - 了解如何获取帮助
3. ✅ [订单类型完整指南](ORDER_TYPES.md) - 理解基础订单
4. ⭐ [止盈止损订单详解](BRACKET_ORDERS.md) - 学习风险管理
5. ⭐ [GTC和RTH参数使用详解](GTC_RTH_USAGE.md) - 深入理解参数

#### 日内交易者
推荐重点阅读：
- [快速入门指南](QUICK_START.md) - 场景1：日内快速交易
- [订单类型完整指南](ORDER_TYPES.md) - AF, MID, MKT订单
- [止盈止损订单详解](BRACKET_ORDERS.md) - 1:1盈亏比策略
- 内置帮助：`man buy`, `man af`, `man evict`

关键命令：
```bash
buy <symbol> <qty> AF @ <price> ± <distance>
evict <symbol> 0 0 MKT
```

#### 波段交易者
推荐重点阅读：
- [快速入门指南](QUICK_START.md) - 场景2：波段交易建仓
- [GTC和RTH参数使用详解](GTC_RTH_USAGE.md) - GTC长期挂单
- [止盈止损订单详解](BRACKET_ORDERS.md) - 高盈亏比策略
- [订单类型完整指南](ORDER_TYPES.md) - LMT, TRAIL订单

关键命令：
```bash
buy <symbol> <qty> LMT @ <price> GTC RTH
buy <symbol> <qty> LMT @ <price> [profit:<p>] [stop:<s>] GTC RTH
```

#### 算法交易者
推荐重点阅读：
- [订单类型完整指南](ORDER_TYPES.md) - TWAP, VWAP算法
- [GTC和RTH参数使用详解](GTC_RTH_USAGE.md) - 参数限制
- 内置帮助：`man ifthen`, `man schedule`, `man expand`

关键功能：
- 条件触发系统（ifthen）
- 批量操作（expand）
- 计划任务（schedule）

---

### 按问题查找

#### "我想学习如何..."

| 问题 | 推荐文档 | 章节 |
|------|---------|------|
| 快速开始使用ICLI | [快速入门指南](QUICK_START.md) | 5分钟快速开始 |
| 理解不同订单类型 | [订单类型完整指南](ORDER_TYPES.md) | 订单类型对照表 |
| 设置止盈止损 | [止盈止损订单详解](BRACKET_ORDERS.md) | 基础概念 |
| 使用GTC参数 | [GTC和RTH参数使用详解](GTC_RTH_USAGE.md) | GTC详解 |
| 获取命令帮助 | [帮助系统使用指南](HELP_SYSTEM.md) | 三层帮助系统 |
| 日内快速交易 | [快速入门指南](QUICK_START.md) | 场景1 |
| 波段建仓策略 | [快速入门指南](QUICK_START.md) | 场景2 |
| 控制交易风险 | [止盈止损订单详解](BRACKET_ORDERS.md) | 风险管理原则 |

#### "为什么..."

| 问题 | 推荐文档 | 章节 |
|------|---------|------|
| AF订单不支持GTC？ | [GTC和RTH参数使用详解](GTC_RTH_USAGE.md) | Q1: 为什么AF不支持GTC |
| MID订单强制RTH？ | [GTC和RTH参数使用详解](GTC_RTH_USAGE.md) | Q2: MID为什么强制RTH |
| 需要设置止损？ | [止盈止损订单详解](BRACKET_ORDERS.md) | 核心要点 |
| 止损被频繁触发？ | [止盈止损订单详解](BRACKET_ORDERS.md) | 错误1：止损太近 |
| 订单没有成交？ | [订单类型完整指南](ORDER_TYPES.md) | 常见错误 |

#### "如何..."

| 问题 | 推荐文档 | 快速命令 |
|------|---------|---------|
| 查看持仓？ | [快速入门指南](QUICK_START.md) | `positions` |
| 设置止损？ | [止盈止损订单详解](BRACKET_ORDERS.md) | `buy AAPL 100 AF @ 150 [stop:145]` |
| 长期挂单？ | [GTC和RTH参数使用详解](GTC_RTH_USAGE.md) | `buy AAPL 100 LMT @ 150 GTC RTH` |
| 预览订单？ | [快速入门指南](QUICK_START.md) | `buy AAPL 100 MID preview` |
| 取消所有订单？ | [快速入门指南](QUICK_START.md) | `cancel *` |
| 清空仓位？ | [快速入门指南](QUICK_START.md) | `evict AAPL 0 0 MID` |

---

## 🔍 快速查找

### 命令速查

```bash
# 查看帮助
hh                              # 快速参考
?                               # 命令列表
man <command>                   # 详细手册

# 账户查询
positions                       # 持仓
cash                            # 现金
balance                         # 总览
orders                          # 活跃订单
executions                      # 执行记录

# 基础交易
buy <symbol> <qty> MID                           # 中间价买入
buy <symbol> <qty> LMT @ <price> GTC             # 限价单
buy <symbol> <qty> AF @ <price> ± <dist>         # 带止盈止损
sell <symbol> <qty> MID                          # 卖出
evict <symbol> 0 0 MID                           # 清仓

# 订单管理
cancel                          # 取消订单
cancel *                        # 取消所有
modify                          # 修改订单

# 行情管理
add SPY QQQ AAPL               # 添加行情
remove SPY                      # 移除行情
qquote AAPL                     # 快速查询
```

### 订单类型速查

| 简写 | 全称 | 用途 | GTC | RTH |
|------|------|------|-----|-----|
| LMT | Limit | 限价单 | ✅ | ✅ |
| MKT | Market | 市价单 | ✅ | ✅ |
| AF | Adaptive Fast | 快速算法 | ❌ | 强制 |
| MID | Midprice | 中间价 | ❌ | 强制 |
| AS | Adaptive Slow | 慢速算法 | ❌ | 强制 |

详见：[订单类型完整指南](ORDER_TYPES.md)

### 参数速查

| 参数 | 说明 | 示例 |
|------|------|------|
| GTC | 持续有效 | `buy AAPL 100 LMT @ 150 GTC` |
| DAY | 当日有效 | `buy AAPL 100 LMT @ 150 DAY` |
| RTH | 常规时间 | `buy AAPL 100 LMT @ 150 RTH` |
| preview | 预览订单 | `buy AAPL 100 MID preview` |

详见：[GTC和RTH参数使用详解](GTC_RTH_USAGE.md)

---

## 🎯 学习路径

### 初级（第1-3天）

**目标**：掌握基础交易操作

1. 阅读 [快速入门指南](QUICK_START.md)
2. 练习基础命令：
   ```bash
   positions, cash, balance
   add, remove
   buy, sell (使用preview)
   orders, cancel
   ```
3. 理解基础概念：
   - 订单类型（LMT, MKT, MID）
   - 预览功能
   - 订单管理

**检查点**：能够使用preview测试订单，查看持仓和余额

### 中级（第4-7天）

**目标**：掌握止盈止损和参数使用

1. 阅读 [止盈止损订单详解](BRACKET_ORDERS.md)
2. 阅读 [GTC和RTH参数使用详解](GTC_RTH_USAGE.md)
3. 练习进阶命令：
   ```bash
   buy AAPL 100 AF @ 150 ± 5
   buy AAPL 100 LMT @ 150 [profit:155] [stop:145] GTC RTH
   ```
4. 理解进阶概念：
   - 止盈止损策略
   - 盈亏比计算
   - GTC vs DAY
   - RTH限制

**检查点**：能够设置合理的止盈止损，理解GTC和RTH的使用场景

### 高级（第8-14天）

**目标**：掌握高级功能和策略

1. 阅读 [订单类型完整指南](ORDER_TYPES.md)（完整版）
2. 探索高级功能：
   ```bash
   man ifthen      # 条件触发
   man expand      # 批量操作
   man schedule    # 计划任务
   ```
3. 实践复杂策略：
   - 分批建仓
   - 条件触发
   - 跟踪止损
   - 大额订单算法

**检查点**：能够使用高级功能，实现自动化交易策略

### 专家级（持续）

**目标**：优化策略，提高效率

1. 深入研究：
   - 不同市场条件下的订单选择
   - 风险管理优化
   - 执行效率提升
2. 自动化策略开发
3. 持续学习和改进

---

## 📖 额外资源

### 项目文档

```
muibcli/
├── README.md              # 项目概述和安装指南
├── CLAUDE.md              # 开发文档和修改原则
├── COMMANDS_HELP.md       # 所有命令的帮助文档
└── docs/                  # 本目录
    ├── README.md          # 本文档
    ├── QUICK_START.md     # 快速入门
    ├── ORDER_TYPES.md     # 订单类型
    ├── GTC_RTH_USAGE.md   # GTC/RTH参数
    ├── BRACKET_ORDERS.md  # 止盈止损
    └── HELP_SYSTEM.md     # 帮助系统
```

### 内置帮助

在ICLI中随时使用：
```bash
hh                    # 快速参考
?                     # 命令列表
man                   # 所有命令分类列表
man <command>         # 特定命令详细帮助
<command>?            # 命令简要帮助
```

### 外部资源

- [IBKR API官方文档](https://interactivebrokers.github.io/tws-api/)
- [ib_async文档](https://ib-insync.readthedocs.io/)
- [项目GitHub](https://github.com/mattsta/icli)
- [IBKR交易者大学](https://www.interactivebrokers.com/campus/)

---

## ⚠️ 重要提醒

### 安全第一

1. **无确认机制** - ICLI命令立即执行，没有二次确认
2. **先用模拟账户** - 熟悉后再使用实盘
3. **使用preview** - 养成预览订单的习惯
4. **设置止损** - 始终设置止损保护
5. **控制风险** - 单笔≤2%，总持仓≤10%

### 最佳实践

1. **阅读文档** - 使用新功能前先查看文档
2. **小额测试** - 从小额开始测试新策略
3. **定期复盘** - 检查交易记录和盈亏
4. **持续学习** - 不断改进交易策略

---

## 🤝 贡献和反馈

发现文档错误或有改进建议？

1. 查看项目GitHub Issues
2. 提交问题或建议
3. 参与文档改进

---

## 📌 快速链接

- **新用户必读**：[快速入门指南](QUICK_START.md)
- **最常查阅**：[订单类型完整指南](ORDER_TYPES.md)
- **风险管理**：[止盈止损订单详解](BRACKET_ORDERS.md)
- **参数详解**：[GTC和RTH参数使用详解](GTC_RTH_USAGE.md)
- **获取帮助**：[帮助系统使用指南](HELP_SYSTEM.md)

---

**祝交易顺利！Happy Trading! 📈**

*最后更新：2025-11-09*
