# ICLI 帮助系统使用指南

## 概述

ICLI提供三种层级的帮助系统，从快速参考到详细手册，满足不同深度的查询需求。本文档详细说明如何使用这些帮助功能。

## 帮助系统层级

```
快速参考 (hh)
    ↓ 查看常用命令和快速示例

简要帮助 (?)
    ↓ 查看命令列表和简单说明

详细手册 (man)
    ↓ 查看完整文档、用法示例和注意事项
```

## 1. 快速参考 - hh命令

### 什么是hh？

`hh` (Quick Help) 显示最常用的交易命令和示例，适合快速查阅基础操作。

### 使用方法

```bash
# 在ICLI中输入
hh
```

### 输出内容

```
╔══════════════════════════════════════════════════════════════╗
║                  ICLI - 常用交易命令快速参考                    ║
╚══════════════════════════════════════════════════════════════╝

📊 查看信息命令:
  positions              查看当前持仓
  cash                   查看现金余额
  balance               查看账户总览
  orders                查看活跃订单
  executions            查看今日执行记录

📈 行情管理命令:
  add SPY QQQ           添加实时行情
  remove SPY            移除行情
  qquote AAPL           快速查询报价

💰 交易执行命令:
  # 基础买入/卖出
  buy AAPL 100 MID                      中间价买入
  buy AAPL 100 LMT @ 150.50 GTC         限价单（持续有效）
  buy AAPL 100 AF @ 150.50              算法快速买入
  sell AAPL 100 MID                     中间价卖出

  # 带止盈止损
  buy AAPL 100 AF @ 150 ± 5             对称止盈止损（±5）
  buy AAPL 100 AF @ 150 [profit:155] [stop:145]  自定义止盈止损

  # 按金额买入
  buy AAPL $10000 MID                   按金额买入

  # 平仓
  evict AAPL 0 0 MID                    清空AAPL持仓

🔧 订单管理命令:
  cancel                交互式取消订单
  cancel *              取消所有订单
  modify                修改订单

📚 获取帮助:
  ?                     显示所有命令
  man <命令>            查看命令详细手册
  <命令>?               快速查看命令帮助

⚠️  重要提醒:
  - 所有订单无需确认，输入后立即执行
  - 使用 preview 参数预览订单（不实际提交）
  - GTC：订单持续有效，RTH：仅常规交易时间
  - 算法订单(AF/MID)自动强制DAY，不支持GTC
```

### 适用场景

- 刚开始使用ICLI，需要快速入门
- 忘记常用命令的语法
- 需要快速查看示例
- 向新用户展示ICLI功能

### 示例

```bash
live> hh

[显示快速参考内容]

live> buy AAPL 100 MID
# 根据hh中的示例，成功买入
```

## 2. 简要帮助 - ? 命令

### 什么是?

`?` 显示所有可用命令的列表和简短描述。单独命令后加`?`可查看该命令的简要帮助。

### 使用方法

```bash
# 查看所有命令
?

# 查看特定命令的简要帮助
buy?
positions?
add?
```

### 输出示例

#### 查看所有命令
```bash
live> ?

All commands:
  # 订单管理 (8)
  buy, sell, evict, cancel, modify, orders, preview, attach

  # 投资组合 (6)
  positions, cash, balance, pnl, trades, portfolio

  # 实时行情 (10)
  add, remove, quote, qquote, depth, greeks, ...

  # 条件触发 (7)
  ifthen, if, iflist, ifclear, ifsave, ifload, iftest

  # 实用工具 (19)
  calc, grow, help, hh, man, config, ...

...

Use 'man <command>' for detailed help.
Use '<command>?' for quick help.
```

#### 查看特定命令
```bash
live> buy?

Command: buy
Usage: buy <symbol> <quantity> <type> [@ price] [options]
Description: Buy security with specified quantity and order type

Examples:
  buy AAPL 100 MID              # 中间价买入
  buy AAPL 100 LMT @ 150 GTC    # 限价单
  buy AAPL 100 AF @ 150 ± 5     # 带止盈止损

See 'man buy' for detailed documentation.
```

### 适用场景

- 想要查看所有可用命令
- 快速查看命令语法
- 不确定命令名称时浏览
- 需要简短提示而非完整文档

## 3. 详细手册 - man命令

### 什么是man？

`man` (Manual，类似Unix系统的man命令) 显示命令的完整文档，包括功能描述、用法示例、参数说明和注意事项。

### 使用方法

```bash
# 查看所有命令列表（按类别分组）
man

# 查看特定命令的详细手册
man buy
man positions
man add
man ifthen
```

### 无参数调用 - 命令列表

```bash
live> man

╔══════════════════════════════════════════════════════════════╗
║                    ICLI 命令完整列表                           ║
╚══════════════════════════════════════════════════════════════╝

【订单管理】
  buy, sell, evict, cancel, modify, orders, preview, attach

【投资组合】
  positions, cash, balance, pnl, trades, portfolio

【实时行情】
  add, remove, quote, qquote, depth, greeks, chains, spread,
  snap, watch, qpos

【条件触发】
  ifthen, if, iflist, ifclear, ifsave, ifload, iftest

【行情管理】
  qadd, qremove, qlist, qclear, qsave, qload, qreload,
  qexport, qimport, qstats, qgroup, qsort

【计划任务】
  schedule, sched, schedlist, schedclear, schedsave, schedload

【后台任务】
  tasks, taskskill

【连接管理】
  reconnect

【实用工具】
  calc, grow, help, hh, man, config, log, version, exit, quit,
  clear, reload, status, time, date, cls, pwd, cd, ls

💡 使用方法:
  man <命令名>     查看具体命令的详细帮助
  例如: man buy

  也可以使用: <命令>? 查看帮助（如 buy?）
```

### 查看特定命令

```bash
live> man buy

╔══════════════════════════════════════════════════════════════╗
║  命令: buy                                                    ║
╚══════════════════════════════════════════════════════════════╝

📂 分类: 订单管理
🔗 别名: b
📝 描述: 买入证券，支持多种订单类型和参数

📋 用法示例:
  buy AAPL 100 MID
  buy AAPL 100 LMT @ 150.50 GTC
  buy AAPL 100 AF @ 150.50
  buy AAPL 100 AF @ 150 ± 5
  buy AAPL 100 LMT @ 150 [profit:155] [stop:145] GTC RTH
  buy AAPL $10000 MID
  expand buy {AAPL,MSFT,NVDA} 100 MID preview

📌 注意事项:
  • 所有订单立即执行，无需确认
  • 使用 preview 参数预览订单而不实际提交
  • AF/MID 等算法订单自动强制 DAY，不支持 GTC
  • GTC 订单持续有效直到取消（最长90天）
  • RTH 限制订单仅在常规交易时间执行（9:30-16:00）
  • 止盈止损语法：± 表示对称，[profit:] [stop:] 表示不对称

═══════════════════════════════════════════════════════════════
```

### 模糊搜索

```bash
live> man ad

❌ 命令 'ad' 未找到。

🔍 你是否想查找以下命令？
  - add
  - qadd

💡 使用 'man' 查看所有可用命令
```

### 别名支持

```bash
live> man b

# 自动识别别名，显示 buy 命令的帮助
╔══════════════════════════════════════════════════════════════╗
║  命令: buy                                                    ║
╚══════════════════════════════════════════════════════════════╝
...
```

### 适用场景

- 第一次使用某个命令
- 需要详细的参数说明
- 想要查看完整的用法示例
- 忘记命令的特殊注意事项
- 需要了解命令的类别和别名

## 帮助系统对比

| 特性 | hh | ? | man |
|------|-----|---|-----|
| **显示内容** | 最常用命令 | 所有命令列表 | 完整文档 |
| **详细程度** | 简要示例 | 简要描述 | 详细说明 |
| **适用场景** | 快速入门 | 浏览命令 | 深入学习 |
| **查看单个命令** | ❌ | ✅ (`cmd?`) | ✅ (`man cmd`) |
| **查看所有命令** | ❌ | ✅ | ✅ |
| **分类显示** | ✅ | ✅ | ✅ |
| **用法示例** | ✅ | 简单 | 详细 |
| **注意事项** | ✅ | ❌ | ✅ |
| **别名信息** | ❌ | ❌ | ✅ |
| **搜索功能** | ❌ | ❌ | ✅ 模糊搜索 |

## 使用工作流

### 新用户学习路径

```bash
# 第1步：快速了解常用命令
hh

# 第2步：浏览所有可用命令
?

# 第3步：查看感兴趣命令的详细文档
man buy
man positions
man add

# 第4步：实际使用命令
buy AAPL 100 MID preview  # 先预览

# 第5步：忘记语法时快速查询
buy?  # 或 man buy
```

### 日常使用流程

```bash
# 快速查看语法
<command>?

# 需要详细信息时
man <command>

# 忘记命令列表时
?  # 或 man
```

### 问题诊断流程

```bash
# 1. 命令不工作，检查语法
man <command>

# 2. 查看注意事项部分
# （在 man 输出的底部）

# 3. 尝试示例命令
# （从 man 输出中复制）

# 4. 使用 preview 测试
<command> ... preview
```

## 帮助文档位置

### COMMANDS_HELP.md

所有命令的详细帮助都存储在项目根目录的 `COMMANDS_HELP.md` 文件中。

```bash
# 文件位置
/Users/jingming/Downloads/muibcli/COMMANDS_HELP.md

# 格式
## command_name

**分类**: 类别
**别名**: 别名列表

**描述**: 命令功能描述

**用法示例**:
```bash
command example 1
command example 2
```

**注意事项**:
- 注意事项1
- 注意事项2
```

### 手动查看

```bash
# 使用任何文本编辑器
vim COMMANDS_HELP.md
code COMMANDS_HELP.md
cat COMMANDS_HELP.md

# 搜索特定命令
grep -A 20 "## buy" COMMANDS_HELP.md
```

## 扩展文档资源

除了内置帮助系统，还有以下文档资源：

### 项目文档

```bash
# 主文档
README.md                  # 项目概述和快速入门

# 开发文档
CLAUDE.md                  # 开发指南和修改原则

# 专题文档（docs/目录）
docs/ORDER_TYPES.md        # 订单类型详解
docs/GTC_RTH_USAGE.md      # GTC和RTH参数使用
docs/BRACKET_ORDERS.md     # 止盈止损订单详解
docs/QUICK_START.md        # 快速入门指南
```

### 在线资源

- [IBKR API官方文档](https://interactivebrokers.github.io/tws-api/)
- [ib_async文档](https://ib-insync.readthedocs.io/)
- [项目GitHub](https://github.com/mattsta/icli)

## 实战示例

### 示例1：学习buy命令

```bash
# 步骤1：快速查看
live> buy?
# 输出：简要用法

# 步骤2：详细学习
live> man buy
# 输出：完整文档

# 步骤3：测试理解
live> buy AAPL 100 MID preview
# 输出：订单预览（不实际提交）

# 步骤4：实际使用
live> buy AAPL 100 MID
# 执行：实际买入
```

### 示例2：忘记命令名

```bash
# 情况：想查看持仓，忘记命令名

# 方式1：浏览命令列表
live> ?
# 找到：positions

# 方式2：查看分类列表
live> man
# 找到：【投资组合】positions

# 方式3：尝试猜测
live> man pos
# 找到：positions（模糊搜索）
```

### 示例3：理解复杂命令

```bash
# 命令：ifthen（条件触发）

# 步骤1：查看详细文档
live> man ifthen
# 理解：条件触发的工作原理

# 步骤2：查看示例
# （从 man 输出中学习）
if AAPL last > 150: buy AAPL 100 MID

# 步骤3：测试简单情况
live> if SPY last > 450: print "SPY above 450"

# 步骤4：实际使用
live> if AAPL last > 155: buy AAPL 100 AF
```

## 帮助系统维护

### 更新帮助内容

帮助内容由 `COMMANDS_HELP.md` 维护。添加新命令或修改现有命令时，需要同步更新此文件。

```markdown
## new_command

**分类**: 类别
**别名**: alias1, alias2

**描述**: 命令功能描述

**用法示例**:
```bash
new_command arg1
new_command arg1 arg2 option
```

**注意事项**:
- 重要的注意事项
- 常见错误和避免方法
```

### 格式规范

1. **分类** - 必须是已知类别之一
2. **别名** - 无别名时写"无"
3. **描述** - 简洁明确，一句话说明功能
4. **用法示例** - 至少3个示例，从简单到复杂
5. **注意事项** - 重要提示、限制、常见错误

## 常见问题

### Q1: hh和man有什么区别？

**A:**
- `hh` - 快速参考，显示最常用的20个命令和示例
- `man` - 详细手册，可以查看任何命令的完整文档

```bash
hh      # 快速入门，看常用命令
man     # 浏览所有命令
man buy # 学习buy命令的详细用法
```

### Q2: ?和man都能查看命令列表，该用哪个？

**A:**
- `?` - 简洁列表，快速浏览
- `man` - 分类列表，更易查找

```bash
?       # 快速查看命令列表
man     # 按类别查看，更有条理
```

### Q3: 如何快速查询命令语法？

**A:** 使用 `<command>?` 格式：

```bash
buy?        # 查看buy命令语法
positions?  # 查看positions命令语法
add?        # 查看add命令语法
```

### Q4: man命令的模糊搜索是如何工作的？

**A:** 当输入的命令不存在时，man会搜索包含该字符串的所有命令：

```bash
live> man pos
❌ 命令 'pos' 未找到。
🔍 你是否想查找以下命令？
  - positions
  - qpos

live> man if
❌ 命令 'if' 未找到。
🔍 你是否想查找以下命令？
  - ifthen
  - iflist
  - ifclear
  - ifsave
  - ifload
  - iftest
```

### Q5: 如何查看命令的别名？

**A:** 使用 `man <command>` 查看详细信息，其中包含别名：

```bash
live> man buy

...
🔗 别名: b
...

# 可以使用别名
live> b AAPL 100 MID  # 等同于 buy AAPL 100 MID
```

### Q6: 帮助文档会自动更新吗？

**A:**
- `hh` 和 `man` 的内容来自 `COMMANDS_HELP.md`
- 修改该文件后，需要重启ICLI或使用 `reload` 命令
- 动态命令列表（`?`）会自动更新

## 最佳实践

### 1. 新手学习路径

```bash
第1天：
  hh                    # 了解基础命令
  buy AAPL 1 MID preview  # 尝试预览订单
  positions             # 查看持仓

第2天：
  ?                     # 浏览所有命令
  man buy               # 深入学习buy命令
  man sell              # 学习sell命令
  man positions         # 学习positions命令

第3天：
  man add               # 学习行情管理
  man orders            # 学习订单管理
  man ifthen            # 学习条件触发

持续：
  遇到问题时使用 man <command>
```

### 2. 日常使用技巧

```bash
# 忘记语法时
<command>?              # 快速提示

# 需要详细信息时
man <command>           # 完整文档

# 忘记命令名时
?                       # 浏览列表
man                     # 分类列表
```

### 3. 问题诊断技巧

```bash
# 1. 命令不按预期工作
man <command>           # 查看完整文档

# 2. 查看注意事项
# man输出底部的"注意事项"部分

# 3. 使用preview测试
<command> ... preview   # 预览而不执行

# 4. 查看日志
tail -f icli-*.log      # 实时日志
```

## 总结

ICLI提供三层帮助系统，从快到详：

1. **hh** - 快速参考，常用命令
2. **?** - 命令列表，快速浏览
3. **man** - 详细手册，完整文档

### 快速参考

| 需求 | 命令 | 说明 |
|------|------|------|
| 快速入门 | `hh` | 最常用命令 |
| 浏览命令 | `?` | 所有命令列表 |
| 分类浏览 | `man` | 按类别列表 |
| 快速语法 | `<cmd>?` | 命令简要帮助 |
| 详细学习 | `man <cmd>` | 完整文档 |

### 记住

- ✅ 新手先看 `hh`
- ✅ 忘记命令用 `?` 或 `man`
- ✅ 学习命令用 `man <command>`
- ✅ 快速查询用 `<command>?`
- ✅ 测试订单用 `preview`

**Happy Trading with ICLI! 📈**
