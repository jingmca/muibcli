"""Command: hh

Category: Utilities
"""

from dataclasses import dataclass

from icli.cmds.base import IOp, command


@command(names=["hh"])
@dataclass
class IOpQuickHelp(IOp):
    """Display quick reference guide for common trading commands."""

    def argmap(self):
        return []

    async def run(self):
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ICLI - 常用交易命令快速参考                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 查看信息命令:
  positions              查看当前持仓
  cash                   查看现金余额
  balance                查看账户总览
  orders                 查看活跃订单
  executions             查看执行记录

📈 股票交易 - 基础买卖:
  buy AAPL 100 MID       买入100股AAPL，使用中间价
  buy AAPL 100 MKT       买入100股AAPL，市价单
  buy AAPL 100 AF        买入100股AAPL，自适应算法单（推荐）
  buy AAPL $10000 MID    买入价值$10000的AAPL
  buy AAPL -100 MID      卖出100股AAPL

📈 股票交易 - 限价单:
  buy AAPL 100 AF @ 233.33           限价$233.33买入100股
  buy AAPL 100 AF @ 233.33 + 10      带止盈：高出$10自动卖出
  buy AAPL 100 AF @ 233.33 - 10      带止损：低于$10自动卖出
  buy AAPL 100 AF @ 233.33 ± 10      同时带止盈止损（OCO订单）

📈 订单类型 (代替MID/MKT/AF):
  MID          中间价（推荐）
  MKT          市价单
  AF           自适应快速算法
  REL          相对价格
  LIMIT        限价单

📈 订单时效 (在命令末尾添加):
  GTC          Good Till Cancel - 直到取消
  RTH          Regular Trading Hours - 仅常规交易时段

  示例: buy AAPL 100 MID GTC
       buy MSFT 100 AF RTH

💼 平仓命令:
  evict AAPL -1 0 MID    清空AAPL所有持仓
  evict * -1 0 MID       清空所有持仓（危险！）

🎯 期权交易:
  buy AAPL 251121P00257500 1 MID        买入1张期权（OCC格式）
  buy AAPL 251121P00257500 -1 MID       卖出1张期权

📊 行情管理:
  add SPY QQQ AAPL       添加实时行情
  remove SPY             移除行情
  qpos                   添加所有持仓到行情

🔔 条件单 (ifthen):
  if QQQ last < 500: buy AAPL 100 MID
    当QQQ价格跌到500以下时，买入AAPL 100股

  if AAPL last > 300: buy AAPL -100 MID
    当AAPL价格涨到300以上时，卖出AAPL 100股

  iflist                 查看所有条件
  ifclear                清除所有条件

🧮 计算器:
  (/ :BP3 AAPL)          计算可买多少股AAPL（33%保证金）
  (* AAPL 100)           计算100股AAPL的总价

⚠️  重要提醒:
  - 所有命令立即执行，无二次确认
  - preview参数可预览订单不执行：buy AAPL 100 AF preview
  - 输入 ? 查看所有命令
  - 输入 man <命令> 查看具体命令详细帮助
  - 输入 <命令>? 也可以查看帮助（如 buy?）

═══════════════════════════════════════════════════════════════════════════════
"""
        print(help_text)
        return True
