#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=============================================="
echo "  SkillSynth - Smart Learning Path Generator  "
echo "=============================================="

# --- Phase 1: Python virtual environment ---
VENV_DIR="$PROJECT_DIR/.venv"
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "[1/4] Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR" --without-pip
    curl -sS https://bootstrap.pypa.io/get-pip.py | "$VENV_DIR/bin/python3" > /dev/null 2>&1
fi

if [ ! -f "$VENV_DIR/bin/fastapi" ] && [ ! -f "$VENV_DIR/bin/uvicorn" ]; then
    echo "[1/4] Installing Python dependencies..."
    "$VENV_DIR/bin/pip" install -q -r requirements.txt 2>&1 | tail -1 || true
    # Install core deps individually if requirements.txt fails
    for pkg in fastapi uvicorn sqlalchemy python-dotenv python-multipart passlib bcrypt python-jose sendgrid email-validator psycopg2-binary; do
        "$VENV_DIR/bin/pip" install -q "$pkg" 2>/dev/null || true
    done
fi

export PATH="$VENV_DIR/bin:$PATH"

# --- Phase 2: Frontend dependencies ---
if [ ! -d "src/frontend/node_modules" ]; then
    echo "[2/4] Installing frontend dependencies..."
    cd src/frontend && npm install --silent && cd "$PROJECT_DIR"
fi

# --- Phase 3: Kill existing processes ---
kill $(lsof -t -i:8000) 2>/dev/null || true
kill $(lsof -t -i:3000) 2>/dev/null || true

# --- Phase 4: Start backend ---
echo "[3/4] Starting backend on http://127.0.0.1:8000 ..."
MODE=dev "$VENV_DIR/bin/python" run.py &
BACKEND_PID=$!

for i in $(seq 1 30); do
    if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
        echo "  Backend ready!"
        break
    fi
    sleep 1
done

# --- Phase 5: Start frontend ---
echo "[4/4] Starting frontend on http://localhost:3000 ..."
cd src/frontend && PORT=3000 npm run dev &
FRONTEND_PID=$!
cd "$PROJECT_DIR"

# --- Summary ---
echo ""
echo "=============================================="
echo "  SkillSynth is running!"
echo ""
echo "  Frontend:  http://localhost:3000"
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
    wait 2>/dev/null
    echo "Done."
}
trap cleanup INT TERM

wait
