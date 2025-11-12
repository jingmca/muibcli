#!/bin/bash
# ICLI Multi-Account Tmux Setup with Config File Support
#
# This script reads account configurations from a config file and creates:
# - Session 1 (icli-accounts): Individual windows for each account
# - Session 2 (icli-monitor): Multi-pane view of all accounts
#
# Usage: ./start_icli_multi.sh [config_file]
# Default config: ./icli_accounts.conf

# ========== Configuration ==========
SESSION1="icli-accounts"
SESSION2="icli-monitor"
WORK_DIR="$HOME/Downloads/muibcli"
CONFIG_FILE="${1:-$WORK_DIR/icli_accounts.conf}"

# Locale settings to fix currency formatting issues
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# ========== Functions ==========

# Parse config file and load accounts
load_accounts() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        echo "❌ Config file not found: $CONFIG_FILE"
        echo ""
        echo "📝 Please create a config file with format:"
        echo "   name|port|account_id|client_id"
        echo ""
        echo "Example:"
        echo "   53|4001|U9619867|1"
        echo "   fut|4002|U6808250|2"
        exit 1
    fi

    # Arrays to store account info
    # Note: Using simple array declaration for bash 3.2 compatibility
    # (bash 3.2 doesn't support -g flag, but arrays are global by default)
    ACCOUNT_NAMES=()
    ACCOUNT_PORTS=()
    ACCOUNT_IDS=()
    ACCOUNT_CLIENT_IDS=()

    echo "📖 Reading config from: $CONFIG_FILE"
    echo ""

    local line_num=0
    while IFS='|' read -r name port account_id client_id || [[ -n "$name" ]]; do
        ((line_num++))

        # Skip comments and empty lines
        [[ "$name" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$name" ]] && continue

        # Trim whitespace
        name=$(echo "$name" | xargs)
        port=$(echo "$port" | xargs)
        account_id=$(echo "$account_id" | xargs)
        client_id=$(echo "$client_id" | xargs)

        # Validate
        if [[ -z "$name" || -z "$port" || -z "$account_id" || -z "$client_id" ]]; then
            echo "⚠️  Warning: Invalid line $line_num, skipping: $name|$port|$account_id|$client_id"
            continue
        fi

        # Add to arrays
        ACCOUNT_NAMES+=("$name")
        ACCOUNT_PORTS+=("$port")
        ACCOUNT_IDS+=("$account_id")
        ACCOUNT_CLIENT_IDS+=("$client_id")

        echo "   ✓ Loaded: $name (Port: $port, ID: $account_id, ClientID: $client_id)"
    done < "$CONFIG_FILE"

    echo ""
    echo "📊 Total accounts loaded: ${#ACCOUNT_NAMES[@]}"

    if [[ ${#ACCOUNT_NAMES[@]} -eq 0 ]]; then
        echo "❌ No valid accounts found in config file"
        exit 1
    fi
}

# ========== Main Script ==========

# Load accounts from config
load_accounts

# ========== Cleanup existing sessions ==========
echo ""
echo "🧹 Cleaning up existing sessions..."
tmux kill-session -t $SESSION1 2>/dev/null
tmux kill-session -t $SESSION2 2>/dev/null

# Kill all view- sessions
for name in "${ACCOUNT_NAMES[@]}"; do
    tmux kill-session -t "view-$name" 2>/dev/null
done

# ========== Session 1: Account Operations ==========
echo ""
echo "📦 Creating Session 1: $SESSION1"
echo "   This session contains individual account windows for direct operation"
echo ""

# Window 0: logs
echo "   Creating Window 0: logs"
tmux new-session -d -s $SESSION1 -n logs
tmux send-keys -t $SESSION1:logs "cd $WORK_DIR && tail -f runlogs/2025/11/icli-*.log" C-m

# Create window for each account
window_index=1
for i in "${!ACCOUNT_NAMES[@]}"; do
    name="${ACCOUNT_NAMES[$i]}"
    port="${ACCOUNT_PORTS[$i]}"
    account_id="${ACCOUNT_IDS[$i]}"
    client_id="${ACCOUNT_CLIENT_IDS[$i]}"

    ((window_index++))
    echo "   Creating Window $window_index: $name"

    tmux new-window -t "$SESSION1:$window_index" -n "$name"
    tmux send-keys -t "$SESSION1:$name" "cd $WORK_DIR" C-m
    tmux send-keys -t "$SESSION1:$name" "export LANG=en_US.UTF-8" C-m
    tmux send-keys -t "$SESSION1:$name" "export LC_ALL=en_US.UTF-8" C-m
    tmux send-keys -t "$SESSION1:$name" "ICLI_CLIENT_ID=$client_id ICLI_IBKR_PORT=$port ICLI_IBKR_ACCOUNT_ID=$account_id poetry run icli" C-m
done

# Wait for ICLI to start
echo ""
echo "⏳ Waiting 5 seconds for ICLI instances to start..."
sleep 5

# ========== Session 2: Monitor Session ==========
echo ""
echo "🖥️  Creating Session 2: $SESSION2"
echo "   This session provides a split-pane view of all accounts"
echo ""

num_accounts=${#ACCOUNT_NAMES[@]}

# Create monitor session with one window
echo "   Creating monitor window with $num_accounts split panes"
tmux new-session -d -s $SESSION2 -n monitor

# Create panes for all accounts (first pane already exists)
for ((i=1; i<num_accounts; i++)); do
    if [[ $i -eq 1 ]]; then
        # First split: horizontal
        tmux split-window -t $SESSION2:monitor -h
    elif [[ $((i % 2)) -eq 0 ]]; then
        # Even splits: vertical
        tmux split-window -t $SESSION2:monitor -v
    else
        # Odd splits: horizontal
        tmux split-window -t $SESSION2:monitor -h
    fi
done

# Use tiled layout for even distribution
tmux select-layout -t $SESSION2:monitor tiled

# Create grouped sessions and attach each pane
for i in "${!ACCOUNT_NAMES[@]}"; do
    name="${ACCOUNT_NAMES[$i]}"
    pane_index=$((i + 1))

    echo "   Creating grouped session for $name"
    tmux new-session -d -t $SESSION1 -s "view-$name"
    tmux send-keys -t "view-$name" ":" C-m
    tmux send-keys -t "view-$name" "selectw -t $name" C-m

    sleep 0.5

    echo "   Linking pane $pane_index → view-$name"
    tmux send-keys -t "$SESSION2:monitor.$pane_index" "unset TMUX && tmux attach-session -t view-$name" C-m
done

# ========== Success Message ==========
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Multi-account setup complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 Session 1: $SESSION1 (账户操作 - Account Operations)"
echo "   ├─ Window 0 (logs)  : 日志显示"

for i in "${!ACCOUNT_NAMES[@]}"; do
    name="${ACCOUNT_NAMES[$i]}"
    port="${ACCOUNT_PORTS[$i]}"
    window_index=$((i + 1))
    if [[ $i -eq $((${#ACCOUNT_NAMES[@]} - 1)) ]]; then
        echo "   └─ Window $window_index ($name) : Port $port"
    else
        echo "   ├─ Window $window_index ($name) : Port $port"
    fi
done

echo ""
echo "📋 Session 2: $SESSION2 (多窗格监控 - Multi-Pane Monitor)"
echo "   └─ Window 0 (monitor) : ${num_accounts}个pane，每个连接到对应账户"

for i in "${!ACCOUNT_NAMES[@]}"; do
    name="${ACCOUNT_NAMES[$i]}"
    pane_index=$((i + 1))
    echo "                           pane $pane_index → view-$name"
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🔗 使用方法 (Usage):"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "   方式1 - 连接到监控session（推荐 - Recommended）："
echo "   ┌────────────────────────────────────────────────────────┐"
echo "   │  tmux attach-session -t $SESSION2               │"
echo "   └────────────────────────────────────────────────────────┘"
echo "   → 可以在${num_accounts}个pane中同时看到和操作所有账户"
echo "   → View and operate all accounts simultaneously"
echo ""
echo "   方式2 - 连接到账户session（直接操作单个账户）："
echo "   ┌────────────────────────────────────────────────────────┐"
echo "   │  tmux attach-session -t $SESSION1             │"
echo "   └────────────────────────────────────────────────────────┘"
echo "   → 单独操作某个账户，使用 Ctrl+b 0/1/2/... 切换window"
echo "   → Operate individual accounts, use Ctrl+b <number> to switch"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "⌨️  在monitor session中导航 (Navigation in monitor session):"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "   Ctrl+b o          在pane之间切换 (Switch between panes)"
echo "   Ctrl+b ←/→/↑/↓    方向键切换pane (Arrow keys to switch)"
echo "   Ctrl+b q [数字]   快速跳转到指定pane (Jump to pane by number)"
echo "   Ctrl+b z          最大化/还原当前pane (Maximize/restore pane)"
echo "   Ctrl+b d          退出session (Detach from session)"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🛠️  管理命令 (Management commands):"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "   列出所有session:"
echo "   tmux list-sessions"
echo ""
echo "   杀死所有session:"
echo "   tmux kill-session -t $SESSION1"
echo "   tmux kill-session -t $SESSION2"
echo ""
echo "   重新运行此脚本:"
echo "   ./start_icli_multi.sh [$CONFIG_FILE]"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
