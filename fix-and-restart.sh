#!/bin/bash
# Cortex 一键修复重启脚本
# 执行：bash fix-and-restart.sh

echo "=== Cortex 修复重启脚本 ==="
echo ""

# 1. 杀掉所有残留进程
echo "[1/5] 清理残留进程..."
pkill -9 -f "node.*Cortex|python.*backend|Electron.*Cortex" 2>/dev/null
pkill -9 -f "python3.*backend.api.server" 2>/dev/null
sleep 2
echo "    进程已清理"

# 2. 删除旧数据库（让新的 schema 生效）
echo "[2/5] 删除旧数据库..."
rm -f ~/.cortex/app.db 2>/dev/null
rm -f ~/Library/Application\ Support/Cortex/cortex.db 2>/dev/null
find /Users/imnoty/work/4.project/Cortex -name "*.db" -delete 2>/dev/null
echo "    数据库已重置"

# 3. 确保依赖最新
echo "[3/5] 安装依赖..."
cd /Users/imnoty/work/4.project/Cortex
npm install 2>/dev/null || echo "    npm install 跳过（可能已安装）"
pip install -q -r backend/requirements.txt 2>/dev/null || echo "    pip install 跳过"
echo "    依赖已检查"

# 4. 端口检查
echo "[4/5] 检查端口占用..."
PORT_18791=$(lsof -i:18791 2>/dev/null | grep -v COMMAND)
PORT_18793=$(lsof -i:18793 2>/dev/null | grep -v COMMAND)
if [ ! -z "$PORT_18791" ]; then
    echo "    警告: 18791 仍被占用，强制释放中..."
    lsof -i:18791 | awk 'NR>1 {print $2}' | xargs kill -9 2>/dev/null
fi
if [ ! -z "$PORT_18793" ]; then
    echo "    警告: 18793 仍被占用，强制释放中..."
    lsof -i:18793 | awk 'NR>1 {print $2}' | xargs kill -9 2>/dev/null
fi
echo "    端口已清理"

# 5. 启动
echo "[5/5] 启动 Cortex..."
echo ""
echo "    正在启动，请等待窗口弹出..."
echo "    启动成功后检查 Console 是否有红字报错"
echo ""
npm run dev
