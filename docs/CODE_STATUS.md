# 📊 ICLI 代码库当前状态

生成时间: 2025-11-14

---

## 🌿 Git 状态

**当前分支**: `main`
**远程仓库**: `https://github.com/jingmca/muibcli.git`
**状态**: ✅ 已同步到远程

### 最近提交历史

```
87a82ed - 1
15446fa - Fix position sorting and spread preset display
4581d24 - Add stock quote preset support and fix option OCC format in all views
30cfa5a - Add documentation for display preset system
051c6af - Implement quote preset system for option display
fcb52dc - Remove forced 'type' column from preset displays
8b0d31a - Fix position preset not applying on wide terminals
f809866 - Use OCC format for option display in positions and quotes
22343be - Implement flexible option symbol formatting (Phase 1)
ad8396f - Add startup parameters and update display presets
```

---

## 📁 项目结构

### 命令系统 (9个类别, 72个命令)

| 类别 | 命令数 | 说明 |
|------|--------|------|
| utilities | 24 | 工具命令 (info, man, expand, etc.) |
| quote_mgmt | 13 | 行情管理 (qadd, qremove, qsave, etc.) |
| quotes | 10 | 实时行情 (add, remove, depth, etc.) |
| orders | 8 | 订单管理 (buy, sell, cancel, modify, etc.) |
| predicates | 6 | 条件触发 (ifthen, iflist, etc.) |
| portfolio | 5 | 投资组合 (positions, balance, executions, etc.) |
| schedule | 3 | 计划任务 |
| tasks | 2 | 后台任务 |
| connection | 1 | 连接管理 (rid) |

### 目录结构

```
muibcli/
├── icli/                       # 主程序包
│   ├── __main__.py            # 入口点
│   ├── cli.py                 # 核心CLI应用 (5,950行)
│   ├── helpers.py             # 辅助函数 (2,851行)
│   ├── orders.py              # 订单定义 (717行)
│   ├── calc.py                # 计算器 (298行)
│   ├── futsexchanges.py       # 期货交易所 (2,937行)
│   ├── instrumentdb.py        # 工具数据库 (621行)
│   ├── utils.py               # 工具函数 (221行)
│   └── cmds/                  # 命令系统
│       ├── base.py            # 命令基类
│       ├── dispatch.py        # 命令分发
│       ├── orders/            # 订单命令
│       ├── portfolio/         # 组合命令
│       ├── quotes/            # 行情命令
│       ├── predicates/        # 条件命令
│       ├── quote_mgmt/        # 行情管理
│       ├── utilities/         # 工具命令
│       ├── schedule/          # 计划任务
│       ├── tasks/             # 后台任务
│       └── connection/        # 连接管理
├── docs/                      # 文档目录
├── .env.icli                  # 环境配置
├── .gitignore                 # Git忽略规则
├── pyproject.toml             # Poetry配置
├── start_icli_multi.sh        # 多账户启动脚本 (已修复bash 3.2兼容)
└── icli_accounts.conf         # 账户配置 (已保护)
```

---

## 📈 代码量统计

### 核心文件

| 文件 | 行数 | 说明 |
|------|------|------|
| `icli/cli.py` | 5,950 | 核心CLI应用 |
| `icli/futsexchanges.py` | 2,937 | 期货交易所映射 |
| `icli/helpers.py` | 2,851 | 辅助函数集合 |
| `icli/orders.py` | 717 | 订单类型定义 |
| `icli/instrumentdb.py` | 621 | 金融工具数据库 |
| `icli/calc.py` | 298 | 计算器功能 |
| `icli/utils.py` | 221 | 工具函数 |
| **总计** | **~15,000+** | icli/ 目录总代码量 |

### 命令文件统计

- 总命令文件: **75个** Python文件
- 平均每个命令: ~100-200行代码
- 最大命令文件: `buy.py` (1,106行) - 包含自动价格追踪

---

## 📄 文档文件

| 文档 | 大小 | 说明 |
|------|------|------|
| `README.md` | 33K | 项目主文档 |
| `CLAUDE.md` | 16K | Claude Code开发指南 |
| `POS_QUOTE_COMPREHENSIVE_SUMMARY.md` | 16K | 持仓和报价显示总结 |
| `COMMANDS_HELP.md` | 16K | 命令帮助文档 |
| `DOCUMENTATION_COMPLETION.md` | 19K | 文档完成度报告 |
| `OPTION_QUOTE_TRADING_STYLE.md` | 11K | 期权报价交易风格 |
| `OPTION_DISPLAY_DESIGN.md` | 12K | 期权显示设计 |
| `CHANGELOG.md` | 11K | 更新日志 |
| `QUOTE_DISPLAY_ANALYSIS.md` | 11K | 报价显示分析 |
| `COLUMN_CONTROL_SUMMARY.md` | 10K | 列控制总结 |

---

## 🔧 配置文件

### `.gitignore` (已更新)

```gitignore
cache*/                      # 缓存目录
positions-*/                 # 持仓数据
icli_accounts.conf          # 账户配置 (敏感)
*.log                        # 日志文件
__pycache__/                # Python缓存
.DS_Store                   # macOS文件
```

### `pyproject.toml`

**Python版本**: 3.12+
**主要依赖**:
- `ib_async >= 2.0.1` - IBKR API
- `pandas > 2.1.0` - 数据处理
- `prompt-toolkit ^3.0.29` - CLI界面
- `loguru > 0.6.0` - 日志系统
- `asyncio` - 异步编程

### `icli_accounts.conf` (已保护)

4个账户配置:
- 867 (Port 4001, ClientID 1)
- fut (Port 4002, ClientID 2)
- 053 (Port 4003, ClientID 3)
- 786 (Port 4004, ClientID 4)

---

## 🚀 最近的重要更新

### 显示系统改进
- ✅ 实现期权Preset系统 (minimal/compact/trading/analysis)
- ✅ OCC格式期权符号显示
- ✅ 自适应终端宽度
- ✅ Portfolio weight百分比 (w%)
- ✅ 启动参数支持 (--position-preset, --quote-preset)

### 基础设施修复
- ✅ Bash 3.2兼容性修复
- ✅ Git配置优化 (保护敏感文件)
- ✅ 多账户启动脚本修复

---

## 📊 代码质量

### 优点
- ✅ 清晰的插件架构 (命令自动发现)
- ✅ 异步设计良好 (asyncio)
- ✅ 丰富的功能集 (72个命令)
- ✅ 详细的文档注释
- ✅ 类型注解完善

### 改进空间
- ⚠️ `cli.py` 文件过大 (5,950行) - 考虑拆分
- ⚠️ `buy.py` 命令复杂 (1,106行) - 可模块化
- ⚠️ 部分缓存逻辑可优化

---

## 🎯 核心特性

### 1. 快速交易
```bash
buy AAPL 100 AF                # 基础买入
buy AAPL 100 AF @ 233.33 ± 10  # 带止盈止损
expand buy {META,MSFT} $15k MID # 批量买入
```

### 2. 实时数据
- 颜色渐变显示 (红↔绿)
- 期权希腊值
- 市场深度 (DOM)

### 3. 自动化
```bash
if AAPL last > 300: buy AAPL 100 AF
```

### 4. 计算器
```bash
(/ :BP3 AAPL)     # 可买股数
(grow :AF 300)    # 资金增长
```

---

**最后更新**: 2025-11-14
**Git Commit**: 87a82ed
**总代码量**: ~15,000+ 行
**总命令数**: 72 个
