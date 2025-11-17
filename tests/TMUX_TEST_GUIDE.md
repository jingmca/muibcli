# TMUX集成测试指南

**按照 CLAUDE.md 阶段4：CLI环境集成测试**

---

## 📋 测试前准备清单

- [x] 阶段1：代码审查 ✅
- [x] 阶段2：单元测试 ✅ (所有测试通过)
- [x] 阶段3：清理Python缓存 ✅
- [ ] 阶段4：CLI环境集成测试 ⏳ (进行中)
- [ ] 阶段5：功能验证检查清单 ⏳

---

## 🖥️ 步骤1: 创建Tmux测试环境

```bash
# 1. 创建新的tmux会话
tmux new -s icli-test

# 2. 分割窗格（垂直分割用于查看日志）
Ctrl+b %

# 3. 在右侧窗格查看实时日志
tail -f runlogs/2025/11/icli-*.log

# 4. 回到左侧窗格（按 Ctrl+b o 切换）
Ctrl+b o

# 5. 在左侧窗格启动icli（连接到4001正式环境）
ICLI_IBKR_PORT=4001 poetry run icli
```

---

## 🧪 步骤2: 基础功能验证

### A. 命令基础测试

```bash
# 验证命令识别
positions
positions?
man positions

# 验证帮助系统
?
```

**预期结果**:
- [ ] positions命令正常执行
- [ ] 帮助信息正确显示
- [ ] 无错误信息

---

## 🎯 步骤3: 功能验证测试

### 测试1: 报价区持仓信息显示

**前置条件**: 需要有至少一个持仓

```bash
# 1. 查看当前持仓，记录持仓标的
positions

# 2. 添加有持仓的标的到报价区
# 例如：如果你有AAPL持仓
add AAPL

# 3. 观察报价显示
# 期待：在行尾看到 [Pos:±数量@成本]
```

**验证点**:
- [ ] 持仓数量正确（多头为正，空头为负）
- [ ] 成本价格正确
- [ ] 格式为 `[Pos:+100@150.50]` 或 `[Pos:-50@145.25]`
- [ ] 加粗显示（如果终端支持）
- [ ] 没有持仓的标的不显示持仓信息

**切换preset测试**:
```bash
# 测试不同的quote preset模式
display quote.preset minimal
# 观察：持仓信息应该显示

display quote.preset compact
# 观察：持仓信息应该显示

display quote.preset trading
# 观察：持仓信息应该显示

display quote.preset options
# 观察：持仓信息应该显示

# 恢复默认
display quote.preset compact
```

**验证点**:
- [ ] minimal模式显示持仓信息
- [ ] compact模式显示持仓信息
- [ ] trading模式显示持仓信息
- [ ] options模式显示持仓信息
- [ ] 所有模式格式一致

---

### 测试2: 价内期权ITM提示

**前置条件**: 需要添加期权行情

```bash
# 1. 添加期权（替换为实际可用的期权）
add AAPL251121C00265000

# 2. 观察ITM标记
# 如果AAPL当前价格 > 265，应该显示绿色ITM标记
# 如果AAPL当前价格 < 265，不应该显示ITM

# 3. 添加Put期权测试
add AAPL251121P00250000
# 如果AAPL当前价格 < 250，应该显示绿色ITM标记
```

**验证点**:
- [ ] Call期权：underlying >= strike 时显示ITM
- [ ] Put期权：underlying <= strike 时显示ITM
- [ ] ITM标记为绿色背景
- [ ] OTM期权不显示ITM（显示三个空格）
- [ ] 在compact/trading/options模式下都正确显示

**观察点**:
```
期待看到类似：
AAPL251121C00265000: [u 270.50 ITM] [d +0.65] ...  # ITM (绿色)
AAPL251121P00250000: [u 270.50    ] [d -0.35] ...  # OTM (无标记)
```

---

### 测试3: 持仓区PNL颜色显示

**前置条件**: 需要有持仓（最好有盈利和亏损的）

```bash
# 1. 查看持仓
positions

# 2. 观察unrealizedPNL和dailyPNL列的颜色
```

**验证点**:
- [ ] 盈利金额显示绿色
- [ ] 亏损金额显示红色
- [ ] 零值显示灰色
- [ ] Total行的PNL也显示颜色

**颜色强度验证**:
- [ ] 小额盈利 ($0-$1,000): 绿字
- [ ] 中等盈利 ($1,000-$10,000): 绿背景
- [ ] 大额盈利 (>$10,000): 亮绿背景
- [ ] 小额亏损 ($0-$1,000): 红字
- [ ] 中等亏损 ($1,000-$10,000): 红背景
- [ ] 大额亏损 (>$10,000): 亮红背景

**切换preset测试**:
```bash
# 测试不同的position preset模式
display position.preset minimal
display position.preset compact
display position.preset trading
display position.preset analysis

# 观察：所有模式下PNL颜色都应该正确显示
```

---

### 测试4: 组合测试（同时验证多个功能）

**测试场景**: 有持仓的期权同时在quote区和position区显示

```bash
# 1. 查看持仓，找一个期权持仓
positions

# 2. 将该期权添加到quote区
# 例如：add AAPL251121C00265000

# 3. 同时观察两个区域
```

**验证点**:
- [ ] Quote区正确显示：
  - ITM标记（如果是价内）
  - 持仓信息 [Pos:±数量@成本]
- [ ] Position区正确显示：
  - PNL颜色（绿色或红色）
  - 其他信息完整

---

## 📊 步骤4: 边界条件测试

### C. 边界条件测试

```bash
# 1. 添加没有持仓的标的
add SPY
# 期待：不显示持仓信息

# 2. 添加多个标的
add AAPL SPY QQQ MSFT
# 期待：只有持仓标的显示持仓信息

# 3. 移除行情
remove AAPL
# 期待：正常移除，无错误
```

**验证点**:
- [ ] 无持仓标的不显示持仓信息
- [ ] 混合显示（有持仓和无持仓）正常
- [ ] 移除功能不受影响

---

## 🐛 步骤5: 错误处理测试

```bash
# D. 错误处理测试

# 1. 无效符号
add INVALIDXYZ123
# 期待：合理的错误消息

# 2. 空持仓查看
positions ""
# 期待：正常显示或合理错误

# 3. 无效preset
display quote.preset invalidpreset
# 期待：合理的错误消息
```

**验证点**:
- [ ] 错误消息清晰
- [ ] 不会崩溃
- [ ] 日志中记录错误

---

## 📝 步骤6: 回归测试

验证现有功能没有被破坏：

```bash
# 核心功能回归测试
positions          # 持仓显示
cash              # 现金余额
balance           # 账户总览
add SPY QQQ       # 行情管理
orders            # 订单查询
executions        # 执行记录

# 行情功能
remove SPY
qquote AAPL

# 计算器
(/ :BP3 AAPL)
```

**验证点**:
- [ ] positions命令正常
- [ ] cash命令正常
- [ ] balance命令正常
- [ ] add/remove正常
- [ ] orders命令正常
- [ ] executions命令正常
- [ ] 计算器正常

---

## 📋 步骤7: 日志分析

在另一个tmux窗格中查看日志：

```bash
# 查看最近的日志
tail -50 runlogs/2025/11/icli-*.log

# 搜索错误
grep "ERROR" runlogs/2025/11/icli-*.log
grep "WARNING" runlogs/2025/11/icli-*.log

# 搜索我们新功能相关的日志
grep -i "position" runlogs/2025/11/icli-*.log | tail -20
```

**验证点**:
- [ ] 无意外的ERROR
- [ ] 无意外的WARNING
- [ ] 功能相关日志正常

---

## ✅ 测试完成检查清单

### 功能测试
- [ ] 报价区持仓信息正确显示
- [ ] 所有quote preset模式都支持
- [ ] ITM期权正确标记
- [ ] PNL颜色正确显示
- [ ] 颜色强度正确

### 边界测试
- [ ] 无持仓标的处理正确
- [ ] 零值处理正确
- [ ] 边界数值处理正确

### 错误处理
- [ ] 错误消息清晰
- [ ] 不会崩溃
- [ ] 日志记录完整

### 回归测试
- [ ] 现有功能未破坏
- [ ] 命令正常工作
- [ ] 性能无明显下降

---

## 🎯 测试失败处理

如果测试失败：

1. **立即停止** - 不要继续其他测试
2. **记录现象** - 截屏、保存日志、记录错误消息
3. **检查日志** - 查看详细错误信息
4. **分析原因** - 使用调试日志追踪问题
5. **修复代码** - 针对性修改
6. **清理缓存** - 删除 `__pycache__` 重新测试
7. **重新测试** - 从阶段2开始完整重测

---

## 📊 测试报告模板

测试完成后，记录结果：

```markdown
## 测试报告

**测试日期**: 2025-11-14
**测试环境**: Port 4001 (正式环境)
**测试人员**: [你的名字]

### 测试结果

#### 报价区持仓信息
- [ ] PASS / [ ] FAIL
- 问题：

#### ITM提示
- [ ] PASS / [ ] FAIL
- 问题：

#### PNL颜色
- [ ] PASS / [ ] FAIL
- 问题：

#### 回归测试
- [ ] PASS / [ ] FAIL
- 问题：

### 发现的问题
1. [问题描述]

### 建议改进
1. [改进建议]
```

---

## 🚀 测试通过后的下一步

1. ✅ 标记阶段4为完成
2. ✅ 完成阶段5功能验证检查清单
3. ✅ 创建git commit
4. ✅ 更新文档

---

**开始测试吧！** 🎉

在tmux中执行这些测试，有任何问题随时反馈。
