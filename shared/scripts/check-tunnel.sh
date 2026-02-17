#!/bin/bash
# check-tunnel.sh — Verify Lambda Tunnel is running
# Usage: bash check-tunnel.sh [tunnel_name]

TUNNEL_NAME="${1:-}"

echo "🔍 Checking Lambda Tunnel status..."

# Check if LT binary is available
if ! command -v ./LT &> /dev/null && ! command -v LT &> /dev/null; then
    echo "❌ Lambda Tunnel binary not found."
    echo "   Download from: https://www.lambdatest.com/support/docs/testing-locally-hosted-pages/"
    exit 2
fi

# Check if tunnel process is running
if pgrep -f "LT.*--tunnelName" > /dev/null 2>&1; then
    RUNNING_TUNNEL=$(ps aux | grep "LT.*--tunnelName" | grep -v grep | head -1)
    echo "✅ Lambda Tunnel is running"
    echo "   Process: $RUNNING_TUNNEL"
    
    if [ -n "$TUNNEL_NAME" ]; then
        if echo "$RUNNING_TUNNEL" | grep -q "$TUNNEL_NAME"; then
            echo "✅ Tunnel name '$TUNNEL_NAME' matches"
        else
            echo "⚠️  Running tunnel name does NOT match '$TUNNEL_NAME'"
            echo "   Your capabilities use tunnelName: '$TUNNEL_NAME' but the running tunnel has a different name"
            exit 1
        fi
    fi
    exit 0
else
    echo "❌ Lambda Tunnel is NOT running"
    echo ""
    echo "   Start it with:"
    echo "   ./LT --user \$LT_USERNAME --key \$LT_ACCESS_KEY --tunnelName ${TUNNEL_NAME:-myTunnel}"
    exit 1
fi
