#!/bin/bash
# ICLI Multi-Account Tmux Setup - Two Sessions Approach
#
# This script creates two tmux sessions:
# - Session 1 (icli-accounts): Each window runs one ICLI account
# - Session 2 (icli-monitor): One window with multiple panes, each pane attaches to Session 1's windows
#
# Usage: ./test_tmux_two_sessions.sh

# ========== Configuration ==========
SESSION1="icli-accounts"
SESSION2="icli-monitor"
WORK_DIR="$HOME/Downloads/muibcli"

# Account configurations
ACCOUNT1_NAME="53"
ACCOUNT1_PORT="4001"
ACCOUNT1_ID="U9619867"  
ACCOUNT1_CLIENT_ID="1"

ACCOUNT2_NAME="fut"
ACCOUNT2_PORT="4002"
ACCOUNT2_ID="U6808250"
ACCOUNT2_CLIENT_ID="2"

ACCOUNT3_NAME="768"
ACCOUNT3_PORT="4003"
ACCOUNT3_ID="U6810786"
ACCOUNT3_CLIENT_ID="3"

# ========== Cleanup existing sessions ==========
echo "🧹 Cleaning up existing sessions..."
tmux kill-session -t $SESSION1 2>/dev/null
tmux kill-session -t $SESSION2 2>/dev/null
tmux kill-session -t view-$ACCOUNT1_NAME 2>/dev/null
tmux kill-session -t view-$ACCOUNT2_NAME 2>/dev/null

# ========== Session 1: Account Operations ==========
echo ""
echo "📦 Creating Session 1: $SESSION1"
echo "   This session contains individual account windows for direct operation"
echo ""

# Window 0: logs
echo "   Creating Window 0: logs"
tmux new-session -d -s $SESSION1 -n logs
# tmux new-window -t $SESSION1:1 -n logs
tmux send-keys -t $SESSION1:1 "cd $WORK_DIR && tail -f icli-*.log" C-m

# Window 1: account1
echo "   Creating Window 2: $ACCOUNT1_NAME"
tmux new-window -t $SESSION1:2 -n $ACCOUNT1_NAME
tmux send-keys -t $SESSION1:$ACCOUNT1_NAME "cd $WORK_DIR" C-m
tmux send-keys -t $SESSION1:$ACCOUNT1_NAME "ICLI_CLIENT_ID=$ACCOUNT1_CLIENT_ID ICLI_IBKR_PORT=$ACCOUNT1_PORT ICLI_IBKR_ACCOUNT_ID=$ACCOUNT1_ID poetry run icli" C-m

# Window 2: account2
echo "   Creating Window 3: $ACCOUNT2_NAME"
tmux new-window -t $SESSION1:3 -n $ACCOUNT2_NAME
tmux send-keys -t $SESSION1:$ACCOUNT2_NAME "cd $WORK_DIR" C-m
tmux send-keys -t $SESSION1:$ACCOUNT2_NAME "ICLI_CLIENT_ID=$ACCOUNT2_CLIENT_ID ICLI_IBKR_PORT=$ACCOUNT2_PORT ICLI_IBKR_ACCOUNT_ID=$ACCOUNT2_ID poetry run icli" C-m

# Window 3: account3
echo "   Creating Window 4: $ACCOUNT3_NAME"
tmux new-window -t $SESSION1:4 -n $ACCOUNT3_NAME
tmux send-keys -t $SESSION1:$ACCOUNT3_NAME "cd $WORK_DIR" C-m
tmux send-keys -t $SESSION1:$ACCOUNT3_NAME "ICLI_CLIENT_ID=$ACCOUNT3_CLIENT_ID ICLI_IBKR_PORT=$ACCOUNT3_PORT ICLI_IBKR_ACCOUNT_ID=$ACCOUNT3_ID poetry run icli" C-m

# Wait for ICLI to start
echo ""
echo "⏳ Waiting 3 seconds for ICLI instances to start..."
sleep 3

# ========== Session 2: Monitor Session ==========
# echo ""
# echo "🖥️  Creating Session 2: $SESSION2"
# echo "   This session provides a split-pane view of all accounts"
# echo ""

# # Create monitor session with one window
# echo "   Creating monitor window with split panes"
# tmux new-session -d -s $SESSION2 -n monitor

# # Split horizontally into 2 panes
# tmux split-window -t $SESSION2:monitor -h

# # Use even-horizontal layout (equal width panes)
# tmux select-layout -t $SESSION2:monitor even-horizontal

# # Create independent grouped sessions for each pane
# # These sessions share the same windows but have independent active window selection
# echo "   Creating grouped session for $ACCOUNT1_NAME"
# tmux new-session -d -t $SESSION1 -s view-$ACCOUNT1_NAME
# tmux send-keys -t view-$ACCOUNT1_NAME ":" C-m
# tmux send-keys -t view-$ACCOUNT1_NAME "selectw -t $ACCOUNT1_NAME" C-m

# echo "   Creating grouped session for $ACCOUNT2_NAME"
# tmux new-session -d -t $SESSION1 -s view-$ACCOUNT2_NAME
# tmux send-keys -t view-$ACCOUNT2_NAME ":" C-m
# tmux send-keys -t view-$ACCOUNT2_NAME "selectw -t $ACCOUNT2_NAME" C-m

# # Wait for grouped sessions to be created
# sleep 1

# # Pane 1: attach to the grouped session for account1
# echo "   Linking pane 1 → view-$ACCOUNT1_NAME"
# tmux send-keys -t $SESSION2:monitor.1 "unset TMUX && tmux attach-session -t view-$ACCOUNT1_NAME" C-m

# # Pane 2: attach to the grouped session for account2
# echo "   Linking pane 2 → view-$ACCOUNT2_NAME"
# tmux send-keys -t $SESSION2:monitor.2 "unset TMUX && tmux attach-session -t view-$ACCOUNT2_NAME" C-m

# ========== Success Message ==========
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Two-session setup complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 Session 1: $SESSION1 (账户操作 - Account Operations)"
echo "   ├─ Window 1 (logs)           : 日志显示"
echo "   ├─ Window 2 ($ACCOUNT1_NAME) : 账户1 - Port $ACCOUNT1_PORT"
echo "   └─ Window 3 ($ACCOUNT2_NAME) : 账户2 - Port $ACCOUNT2_PORT"
echo ""
echo "📋 Session 2: $SESSION2 (多窗格监控 - Multi-Pane Monitor)"
echo "   └─ Window 0 (monitor)        : 2个pane，每个连接到对应账户"
echo "                                  左pane → view-$ACCOUNT1_NAME"
echo "                                  右pane → view-$ACCOUNT2_NAME"
echo ""
echo "📋 Grouped Sessions (独立视图 - Independent Views):"
echo "   ├─ view-$ACCOUNT1_NAME        : 独立查看 $ACCOUNT1_NAME"
echo "   └─ view-$ACCOUNT2_NAME        : 独立查看 $ACCOUNT2_NAME"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🔗 使用方法 (Usage):"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "   方式1 - 连接到监控session（推荐 - Recommended）："
echo "   ┌────────────────────────────────────────────────────────┐"
echo "   │  tmux attach-session -t $SESSION2               │"
echo "   └────────────────────────────────────────────────────────┘"
echo "   → 可以在两个pane中同时看到和操作两个账户"
echo "   → View and operate both accounts simultaneously"
echo ""
echo "   方式2 - 连接到账户session（直接操作单个账户）："
echo "   ┌────────────────────────────────────────────────────────┐"
echo "   │  tmux attach-session -t $SESSION1             │"
echo "   └────────────────────────────────────────────────────────┘"
echo "   → 单独操作某个账户，使用 Ctrl+b 0/1/2 切换window"
echo "   → Operate individual accounts, use Ctrl+b 0/1/2 to switch"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "⌨️  在monitor session中导航 (Navigation in monitor session):"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "   Ctrl+b o          在pane之间切换 (Switch between panes)"
echo "   Ctrl+b ←/→        左右切换pane (Switch left/right)"
echo "   Ctrl+b ↑/↓        上下切换pane (Switch up/down)"
echo "   Ctrl+b z          最大化/还原当前pane (Maximize/restore current pane)"
echo "   Ctrl+b d          退出session (Detach from session)"
echo "   直接输入命令       在当前pane的账户中执行 (Execute in current account)"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "💡 提示 (Tips):"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "   • 在monitor session中，每个pane都是独立的ICLI会话"
echo "     Each pane is an independent ICLI session in monitor"
echo ""
echo "   • 如果遇到嵌套tmux键绑定冲突，按两次 Ctrl+b"
echo "     If nested tmux key conflict, press Ctrl+b twice"
echo ""
echo "   • 测试命令示例 (Test commands):"
echo "     - positions     查看持仓"
echo "     - cash          查看现金"
echo "     - orders        查看订单"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🛠️  管理命令 (Management commands):"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "   列出所有session:"
echo "   tmux list-sessions"
echo ""
echo "   杀死session:"
echo "   tmux kill-session -t $SESSION1"
echo "   tmux kill-session -t $SESSION2"
echo "   tmux kill-session -t view-$ACCOUNT1_NAME"
echo "   tmux kill-session -t view-$ACCOUNT2_NAME"
echo ""
echo "   重新运行此脚本:"
echo "   ./test_tmux_two_sessions.sh"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
