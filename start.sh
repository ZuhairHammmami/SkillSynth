#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Ensure npm-global bin is in PATH (for pnpm)
export PATH="$HOME/.npm-global/bin:$PATH"

echo "=============================================="
echo "  SkillSynth - Smart Learning Path Generator  "
echo "=============================================="

# --- Phase 1: Python virtual environment ---
VENV_DIR="$PROJECT_DIR/.venv"
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "[1/6] Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

if [ ! -f "$VENV_DIR/bin/fastapi" ] && [ ! -f "$VENV_DIR/bin/uvicorn" ]; then
    echo "[1/6] Installing Python dependencies..."
    "$VENV_DIR/bin/pip" install -q --upgrade pip 2>/dev/null
    "$VENV_DIR/bin/pip" install -q -r requirements.txt 2>&1 | tail -1 || true
    # Install core deps individually if requirements.txt fails
    for pkg in fastapi uvicorn sqlalchemy python-dotenv python-multipart passlib bcrypt python-jose sendgrid email-validator psycopg2-binary; do
        "$VENV_DIR/bin/pip" install -q "$pkg" 2>/dev/null || true
    done
fi

export PATH="$VENV_DIR/bin:$PATH"

# --- Phase 2: Frontend dependencies (pnpm) ---
if ! command -v pnpm &> /dev/null; then
    echo "[ERROR] pnpm is not installed. Run: npm install -g corepack && corepack enable pnpm"
    exit 1
fi

if [ ! -d "src/frontend/node_modules" ]; then
    echo "[2/6] Installing frontend dependencies..."
    cd src/frontend && pnpm install --frozen-lockfile && cd "$PROJECT_DIR"
fi

# --- Phase 3: Admin app dependencies (pnpm) ---
if [ ! -d "src/admin-app/node_modules" ]; then
    echo "[3/6] Installing admin app dependencies..."
    cd src/admin-app && pnpm install --frozen-lockfile && cd "$PROJECT_DIR"
fi

# --- Phase 4: Kill existing processes ---
kill $(lsof -t -i:8000) 2>/dev/null || true
kill $(lsof -t -i:3000) 2>/dev/null || true
kill $(lsof -t -i:3001) 2>/dev/null || true

# --- Phase 5: Start backend ---
echo "[4/6] Starting backend on http://127.0.0.1:8000 ..."
MODE=dev "$VENV_DIR/bin/python" run.py &
BACKEND_PID=$!

for i in $(seq 1 30); do
    if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
        echo "  Backend ready!"
        break
    fi
    sleep 1
done

# --- Phase 6: Start frontend + admin ---
echo "[5/6] Starting frontend on http://localhost:3000 ..."
cd src/frontend && PORT=3000 pnpm dev &
FRONTEND_PID=$!
cd "$PROJECT_DIR"

echo "[6/6] Starting admin app on http://localhost:3001 ..."
cd src/admin-app && PORT=3001 pnpm dev &
ADMIN_PID=$!
cd "$PROJECT_DIR"

# --- Summary ---
echo ""
echo "=============================================="
echo "  SkillSynth is running!"
echo ""
echo "  Frontend:  http://localhost:3000"
echo "  Admin:     http://localhost:3001"
echo "  Backend:   http://127.0.0.1:8000"
echo "  API Docs:  http://127.0.0.1:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "=============================================="

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    kill $ADMIN_PID 2>/dev/null || true
    wait 2>/dev/null
    echo "Done."
}
trap cleanup INT TERM

wait
