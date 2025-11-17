# ICLI 帮助命令使用说明

## 概述

新增了两个帮助命令，方便随时查阅交易命令的使用方法。

## 命令列表

### 1. `hh` - 常用命令快速参考

显示最常用的交易命令和示例，适合快速查阅。

**用法**:
```bash
hh
```

**显示内容**:
- 📊 查看信息命令（positions, cash, balance, orders, executions）
- 📈 股票交易示例（市价单、限价单、止盈止损）
- 📈 订单类型说明（MID, MKT, AF, REL, LIMIT）
- 📈 订单时效（GTC, RTH）
- 💼 平仓命令（evict）
- 🎯 期权交易
- 📊 行情管理
- 🔔 条件单（ifthen）
- 🧮 计算器功能

### 2. `hhh` - 命令详细帮助

查询具体命令的详细帮助信息，包括功能说明、用法示例和注意事项。

**用法**:
```bash
# 列出所有命令（按类别分组）
hhh

# 查询具体命令的详细帮助
hhh buy
hhh positions
hhh ifthen
```

**支持的命令类别**:

1. **订单管理** (12个命令)
   - buy, sell, cancel, orders, modify, evict, limit, expand, fast, scale, simulate, paper

2. **投资组合** (5个命令)
   - positions, balance, cash, executions, ls

3. **行情管理** (7个命令)
   - add, remove, qpos, qquote, depth, info, chains

4. **行情组管理** (7个命令)
   - qadd, qsave, qrestore, qlist, qdelete, qclean, qsnapshot, qloadsnapshot

5. **条件触发** (6个命令)
   - ifthen (if), auto, iflist (ifls), ifrm, ifclear, ifgroup

6. **实用工具** (9个命令)
   - cls, hh, hhh, math, set, unset, reconnect, say, clear

7. **计划任务** (3个命令)
   - sched-add, sched-list (slist), sched-cancel (scancel)

8. **后台任务** (2个命令)
   - tasklist, taskcancel

9. **其他** (20+个命令)
   - calendar, details, meta, report, reporter, advice, alert, alias, colorset, 等

## 使用示例

### 示例1: 查看常用帮助

```bash
live> hh
```

输出：
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ICLI - 常用交易命令快速参考                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 查看信息命令:
  positions              查看当前持仓
  cash                   查看现金余额
  ...
```

### 示例2: 列出所有命令

```bash
live> hhh
```

输出：
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ICLI 命令完整列表                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

【订单管理】
  buy, cancel, evict, expand, fast, limit, modify, orders, paper, scale, sell, simulate

【投资组合】
  balance, cash, executions, ls, positions

【行情管理】
  add, chains, depth, info, qpos, qquote, remove
...
```

### 示例3: 查看buy命令详细帮助

```bash
live> hhh buy
```

输出：
```
╔══════════════════════════════════════════════════════════════════════════════╗
║  命令: buy                                                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

📂 分类: 订单管理
📝 描述: 买入或卖出股票/期权

📋 用法示例:
  buy AAPL 100 MID              # 中间价买入100股
  buy AAPL 100 MKT              # 市价买入100股
  buy AAPL 100 AF               # 自适应算法买入
  buy AAPL $10000 MID           # 买入价值$10000的股票
  buy AAPL -100 MID             # 卖出100股
  buy AAPL 100 AF @ 233.33      # 限价$233.33买入
  buy AAPL 100 AF @ 233.33 + 10 # 限价买入+止盈
  buy AAPL 100 AF @ 233.33 - 10 # 限价买入+止损
  buy AAPL 100 AF @ 233.33 ± 10 # 限价买入+OCO括号单
  buy AAPL 100 MID GTC          # 买入，订单有效直到取消
  buy AAPL 100 MID RTH          # 买入，仅常规交易时段
  buy AAPL 100 AF preview       # 预览订单，不执行

📌 注意事项:
  • 正数表示买入，负数表示卖出
  • 支持$金额或股数
  • @ 后指定限价价格
  • + 后指定止盈价差
  • - 后指定止损价差
  • ± 后指定止盈止损价差

═══════════════════════════════════════════════════════════════════════════════
```

### 示例4: 查看条件单帮助

```bash
live> hhh ifthen
```

输出：
```
╔══════════════════════════════════════════════════════════════════════════════╗
║  命令: ifthen                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📂 分类: 条件触发
📝 描述: 创建条件单（单次触发）

📋 用法示例:
  if QQQ last < 500: buy AAPL 100 MID
  if AAPL bid > 300: buy AAPL -100 AF
  if SPY ema60 > ema300: buy SPY 100 MID

📌 注意事项:
  • 支持条件：last, bid, ask, high, low, ema, atr
  • 触发一次后自动删除

🔗 别名: if

═══════════════════════════════════════════════════════════════════════════════
```

### 示例5: 查找相似命令

```bash
live> hhh pos
```

输出：
```
❌ 命令 'pos' 未找到。

🔍 你是否想查找以下命令？
  - positions
  - qpos

💡 使用 'hhh' 查看所有可用命令
```

## 与其他帮助方式的对比

| 方式 | 用途 | 示例 |
|------|------|------|
| `?` | 列出所有可用命令 | `?` |
| `命令?` | 查看命令原生帮助 | `buy?` |
| `hh` | 查看常用命令快速参考 | `hh` |
| `hhh` | 列出所有命令（分类） | `hhh` |
| `hhh 命令` | 查看命令详细中文帮助 | `hhh buy` |

## 启动提示

程序启动并连接成功后会显示：

```
✅ 已连接到IBKR！
💡 输入 'hh' 查看常用命令帮助
💡 输入 'hhh <命令>' 查看具体命令详细帮助
```

## 文件位置

- `hh` 命令: `/icli/cmds/utilities/hh.py`
- `hhh` 命令: `/icli/cmds/utilities/hhh.py`
- 启动提示: `/icli/cli.py` (line 5696-5698)

## 扩展说明

### 添加新命令帮助

如果需要为新命令添加详细帮助，编辑 `hhh.py` 文件中的 `COMMAND_HELP` 字典：

```python
COMMAND_HELP = {
    "新命令名": {
        "category": "命令类别",
        "desc": "功能描述",
        "usage": [
            "用法示例1",
            "用法示例2",
        ],
        "notes": [
            "注意事项1",
            "注意事项2",
        ],
        "alias": ["别名1", "别名2"],  # 可选
    },
}
```

### 命令帮助信息包含内容

每个命令的帮助信息包括：
1. **分类** (category) - 命令所属类别
2. **描述** (desc) - 简短功能说明
3. **用法示例** (usage) - 具体使用方法
4. **注意事项** (notes) - 重要提示（可选）
5. **别名** (alias) - 命令别名（可选）

## 已覆盖的命令

`hhh` 命令目前提供了以下命令的详细帮助（共60+个）：

**核心交易命令**:
- buy, sell, cancel, orders, modify, evict, limit
- positions, balance, cash, executions, ls
- add, remove, qpos, qquote, depth, info, chains

**高级功能**:
- expand, fast, scale, straddle, simulate, paper
- ifthen (if), auto, iflist, ifrm, ifclear, ifgroup

**行情组管理**:
- qadd, qsave, qrestore, qlist, qdelete, qclean
- qsnapshot, qloadsnapshot

**工具命令**:
- cls, hh, hhh, math, set, unset, reconnect, say
- sched-add, sched-list, sched-cancel
- tasklist, taskcancel

**其他命令**:
- calendar, details, meta, report, reporter, advice
- alert, alias, colorset, colorsload, daydumper
- oadd, prequalify, qualify, range, rid, sadd, align

## 使用建议

1. **新手**：先用 `hh` 查看常用命令
2. **查找命令**：用 `hhh` 列出所有命令
3. **学习命令**：用 `hhh 命令名` 查看详细用法
4. **快速查询**：用 `命令?` 查看原生帮助

## 总结

- ✅ `hh` - 快速参考最常用的命令
- ✅ `hhh` - 查看所有命令列表或具体命令详情
- ✅ 启动时简短提示，不影响体验
- ✅ 覆盖60+个命令的详细中文帮助
- ✅ 支持模糊搜索相似命令
- ✅ 分类清晰，便于查找
