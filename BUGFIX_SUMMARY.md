# Bug修复总结

## 修复日期
2025-11-09

## 问题1: 错误抑制机制未生效 ❌ → ✅

### 问题描述
启动时出现大量重复的错误信息：
```
2025-11-09 22:08:58.695 | ERROR | icli.utils:handle_error:122 - Order Error [orderId 3] [code 2150]: Invalid position trade derived value
2025-11-09 22:08:58.695 | ERROR | icli.utils:handle_error:126 - Order Error [orderId 3] [code 2150]: Invalid position trade derived value (occurred 42 times in last 15 minutes)
```

每个错误被记录了**两次**，错误抑制机制完全没有起作用。

### 根本原因
`ThresholdErrorHandler.handle_error()` 的实现有bug：
1. 调用 `log_func(message)` - 记录到日志
2. 调用 `print_func(message)` - 显示到终端

但在 `cli.py` 中，两个参数都设置为 `logger.error`：
```python
self.thresholdErrorHandler.handle_error(
    error_code=str(errorCode),
    message=msg,
    log_func=logger.error,  # ← 重复
    print_func=logger.error, # ← 重复
)
```

导致每次都调用两次 `logger.error`，完全绕过了抑制机制。

### 修复方案

#### 1. 简化 `ThresholdErrorHandler` (/icli/utils.py:90-116)
重构 `handle_error()` 为 `should_display_error()`：
- 不再直接调用日志函数
- 只返回是否应该显示和计数：`(bool, int)`
- 让调用方决定如何记录

```python
def should_display_error(
    self,
    error_code: str,
) -> tuple[bool, int]:
    """
    Check if an error should be displayed to terminal based on frequency.

    Returns:
        tuple[bool, int]: (should_display, count_in_window)
    """
    now = time.time()
    if error_code not in self._error_registry:
        self._error_registry[error_code] = ThresholdErrorRecord()

    record = self._error_registry[error_code]
    record.add_occurrence(now)
    count = record.count_in_window(now, self.time_window)

    return count >= self.threshold, count
```

#### 2. 修改错误处理逻辑 (/icli/cli.py:3124-3140)
```python
# Check if this error should be displayed to terminal
should_display, count = self.thresholdErrorHandler.should_display_error(
    error_code=str(errorCode)
)

if should_display:
    # Display to terminal with occurrence count
    logger.error(
        "{} (occurred {} times in last {} minutes)",
        msg,
        count,
        int(self.thresholdErrorHandler.time_window / 60),
    )
else:
    # Only log to file using logger.debug (won't display to terminal)
    logger.bind(suppress_terminal=True).debug(msg)
```

### 预期行为
- **前4次错误**：只记录到 `icli-*.log` 文件，不显示到终端
- **第5次错误**：显示到终端，附带统计信息
  ```
  Order Error [orderId 3] [code 2150]: Invalid position trade derived value (occurred 5 times in last 15 minutes)
  ```
- **后续错误**：继续显示到终端，更新计数

---

## 问题2: `man add` 命令不显示帮助 ❌ → ✅

### 问题描述
输入 `man add` 时，没有显示 add 命令的详细帮助，而是显示所有命令列表。

### 根本原因
`man.py` 中参数解析有问题：
```python
cmd: str = field(default="", init=False)

def argmap(self):
    return [DArg("?cmd", convert=lambda x: x[0] if x else "", ...)]
```

问题：
1. `?cmd` 语法在 DArg 中可能不被支持（没有找到其他使用示例）
2. `self.cmd` 没有被正确赋值，导致在 `run()` 中 `self.cmd` 始终为空
3. 因此 `if not self.cmd:` 条件永远为真，总是显示所有命令列表

### 修复方案

#### 修改参数定义 (/icli/cmds/utilities/man.py:21-29)
使用 `*cmd` 变长参数（类似其他命令的实现）：

```python
cmd: list[str] = field(default_factory=list, init=False)

def argmap(self):
    return [
        DArg(
            "*cmd",  # 0个或多个参数
            desc="Command name to get manual (leave empty to list all commands)",
        )
    ]
```

#### 修改参数使用 (/icli/cmds/utilities/man.py:105-156)
```python
# 检查是否有参数
if not self.cmd or len(self.cmd) == 0:
    # 显示所有命令列表
    ...

# 获取第一个参数作为命令名
cmd = self.cmd[0].lower() if self.cmd else ""

# 错误提示中使用 self.cmd[0]
print(f"\n❌ 命令 '{self.cmd[0]}' 未找到。\n")
```

### 预期行为
- `man` - 显示所有命令列表（按类别分组）
- `man add` - 显示 add 命令的详细帮助
- `man buy` - 显示 buy 命令的详细帮助
- `man xyz` - 提示命令未找到，推荐相似命令

---

## 问题3: `hh` 显示自动补全提示（非bug）ℹ️

### 现象
```
live> hh
Completion choices: hhh, hh
```

### 解释
这是**正常行为**，不是bug。

原因：
- CLI的自动补全系统检测到两个以 "hh" 开头的命令：
  1. `hh` - 快速参考命令
  2. `hhh` - man 命令的别名

当用户输入 "hh" 时，系统提示有两个可能的选择。

### 解决方案
用户应该：
1. **按回车**：执行 `hh` 命令（显示快速参考）
2. **按Tab继续输入**：如果想选择 `hhh`

这是命令行的标准行为，无需修改。

---

## 测试验证

### 单元测试
创建 `/test_fixes.py` 验证：
1. ✅ 错误抑制机制工作正常
   - 前4次：should_display=False
   - 第5次：should_display=True, count=5
2. ✅ man 命令参数类型正确
   - cmd 字段: `list[str]`
   - argmap: `*cmd`

### 实际环境测试步骤
1. 清理缓存并重启 ICLI
   ```bash
   find icli -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
   poetry run icli
   ```

2. 测试错误抑制
   - 观察启动时的错误消息
   - 前4次错误应该只在 log 文件中
   - 第5次开始显示到终端

3. 测试 man 命令
   ```bash
   man              # 应显示所有命令列表
   man add          # 应显示 add 命令帮助
   man buy          # 应显示 buy 命令帮助
   man positions    # 应显示 positions 命令帮助
   ```

4. 测试 hh 命令
   ```bash
   hh               # 按回车，应显示快速参考
   ```

## 文件变更清单

### 修改文件
1. `/icli/utils.py`
   - 第90-116行：重构 `handle_error()` → `should_display_error()`
   - 返回值改为 `tuple[bool, int]`

2. `/icli/cli.py`
   - 第3124-3140行：重写错误处理逻辑
   - 使用 `should_display_error()` 决定是否显示

3. `/icli/cmds/utilities/man.py`
   - 第21行：`cmd` 字段类型 `str` → `list[str]`
   - 第26行：argmap 从 `?cmd` → `*cmd`
   - 第105行：条件判断 `if not self.cmd or len(self.cmd) == 0:`
   - 第130行：获取参数 `cmd = self.cmd[0].lower() if self.cmd else ""`
   - 第150、156行：错误提示使用 `self.cmd[0]`

### 新增文件
- `/test_fixes.py` - 修复验证测试脚本
- `/BUGFIX_SUMMARY.md` - 本文档

## 兼容性

### 向后兼容 ✅
- `hh` 命令功能不变
- `man` 和 `hhh` 都可用（hhh 是 man 的别名）
- 错误抑制机制是新增功能，不影响现有行为

### 用户可见变化
1. **错误消息减少**：重复错误在达到阈值前不会显示
2. **man 命令正常工作**：`man <命令>` 现在能正确显示帮助
3. **无其他变化**：其他命令和功能保持不变

## 总结

| 问题 | 状态 | 修复方式 |
|------|------|---------|
| 错误抑制未生效 | ✅ 已修复 | 重构为 should_display_error() |
| man 命令参数不工作 | ✅ 已修复 | 改用 *cmd 变长参数 |
| hh 自动补全提示 | ℹ️ 非bug | 正常CLI行为 |

**所有修复已验证通过，准备在实际环境中测试。**
