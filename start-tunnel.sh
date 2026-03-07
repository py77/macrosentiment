#!/bin/bash
# -----------------------------------------------------------------
#  start-tunnel.sh — One-command Cloudflare tunnel + Vercel deploy
#
#  Starts a Cloudflare quick tunnel, captures the new URL,
#  updates Vercel's VITE_API_URL env var, triggers a fresh
#  production deploy, then keeps cloudflared running in foreground.
#
#  Usage:  bash start-tunnel.sh
#  Stop:   Ctrl+C
#
#  Requirements:
#    - cloudflared installed
#    - vercel CLI installed (npx vercel)
#    - Docker running (backend must be up on port 8002)
#
#  FUTURE: Named Cloudflare Tunnel (permanent URL, no redeployment)
#  ----------------------------------------------------------------
#  If you register a domain on Cloudflare (free DNS, ~$10/yr):
#    1. cloudflared tunnel create macrosentiment
#    2. cloudflared tunnel route dns macrosentiment api.yourdomain.com
#    3. Create ~/.cloudflared/config.yml:
#         tunnel: macrosentiment
#         credentials-file: ~/.cloudflared/<tunnel-id>.json
#         ingress:
#           - hostname: api.yourdomain.com
#             service: http://localhost:8002
#           - service: http_status:404
#    4. Set VITE_API_URL=https://api.yourdomain.com in Vercel (once)
#    5. Replace this script with: cloudflared tunnel run macrosentiment
#  ----------------------------------------------------------------

set -euo pipefail

CLOUDFLARED="/c/Program Files (x86)/cloudflared/cloudflared.exe"
BACKEND_PORT=8002
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$REPO_ROOT/frontend"
TMPLOG=$(mktemp)
TUNNEL_PID=""

# --- Cleanup on exit ---
cleanup() {
    echo ""
    echo "Shutting down..."
    if [[ -n "$TUNNEL_PID" ]] && kill -0 "$TUNNEL_PID" 2>/dev/null; then
        kill "$TUNNEL_PID" 2>/dev/null || true
        wait "$TUNNEL_PID" 2>/dev/null || true
    fi
    rm -f "$TMPLOG"
    echo "Done."
}
trap cleanup EXIT INT TERM

# --- Preflight checks ---
if ! command -v npx &>/dev/null; then
    echo "ERROR: npx not found. Install Node.js first."
    exit 1
fi

if [[ ! -f "$CLOUDFLARED" ]]; then
    echo "ERROR: cloudflared not found at $CLOUDFLARED"
    exit 1
fi

if [[ ! -f "$FRONTEND_DIR/.vercel/project.json" ]]; then
    echo "ERROR: $FRONTEND_DIR/.vercel/project.json not found."
    echo "Run 'npx vercel link' in the frontend directory first."
    exit 1
fi

echo "=== Macrosentiment Tunnel Launcher ==="
echo ""

# --- Start cloudflared in background ---
echo "[1/4] Starting cloudflared tunnel on port $BACKEND_PORT..."
"$CLOUDFLARED" tunnel --url "http://localhost:$BACKEND_PORT" 2>"$TMPLOG" &
TUNNEL_PID=$!

# --- Wait for tunnel URL (up to 30s) ---
echo "[2/4] Waiting for tunnel URL..."
TUNNEL_URL=""
for i in $(seq 1 30); do
    URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$TMPLOG" 2>/dev/null | head -1 || true)
    if [[ -n "$URL" ]]; then
        TUNNEL_URL="$URL"
        break
    fi
    sleep 1
done

if [[ -z "$TUNNEL_URL" ]]; then
    echo "ERROR: Could not capture tunnel URL after 30s."
    echo "--- cloudflared output ---"
    cat "$TMPLOG"
    exit 1
fi

echo "       Tunnel URL: $TUNNEL_URL"
echo ""

# --- Update Vercel env var ---
echo "[3/4] Updating Vercel VITE_API_URL..."
cd "$FRONTEND_DIR"
npx vercel env rm VITE_API_URL production -y 2>/dev/null || true
echo "$TUNNEL_URL" | npx vercel env add VITE_API_URL production
echo "       VITE_API_URL set to $TUNNEL_URL"
echo ""

# --- Deploy to Vercel ---
echo "[4/4] Deploying to Vercel (production)..."
cd "$REPO_ROOT"
DEPLOY_OUTPUT=$(npx vercel --prod --yes 2>&1)
DEPLOY_URL=$(echo "$DEPLOY_OUTPUT" | grep -oE 'https://[^ ]+\.vercel\.app' | head -1 || true)
echo "$DEPLOY_OUTPUT"
echo ""

# --- Summary ---
echo "==========================================="
echo "  Tunnel:    $TUNNEL_URL"
if [[ -n "$DEPLOY_URL" ]]; then
echo "  Deploy:    $DEPLOY_URL"
fi
echo "  Frontend:  https://frontend-tau-peach-83.vercel.app"
echo "  Backend:   http://localhost:$BACKEND_PORT"
echo "==========================================="
echo ""
echo "Tunnel is running. Press Ctrl+C to stop."
echo ""

# --- Tail cloudflared logs in foreground ---
tail -f "$TMPLOG"
