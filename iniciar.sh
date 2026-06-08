#!/bin/bash


# hacer chmod +x iniciar.sh


set -e

echo "Levantando Altezza sin Docker"

cd "$(dirname "$0")"

BACKEND_PORT=5000
FRONTEND_PORT=5001

mkdir -p logs

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: No se encontró python3"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "ERROR: No existe requirements.txt"
    exit 1
fi

if [ ! -f "Backend/appBack.py" ]; then
    echo "ERROR: No existe Backend/appBack.py"
    exit 1
fi

if [ ! -f "Frontend/app.py" ]; then
    echo "ERROR: No existe Frontend/app.py"
    exit 1
fi

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

export DB_HOST="${DB_HOST:-127.0.0.1}"
export DB_PORT="${DB_PORT:-3306}"
export DB_USER="${DB_USER:-root}"
export DB_PASSWORD="${DB_PASSWORD:-Root123!}"
export DB_NAME="${DB_NAME:-altezza}"

export BACKEND_URL="http://127.0.0.1:$BACKEND_PORT"

python - <<PY
from pathlib import Path

archivos = [
    Path("Frontend/routes/auth.py"),
    Path("Frontend/routes/mis_rutas.py"),
    Path("Frontend/routes/routes.py"),
]

for archivo in archivos:
    if archivo.exists():
        texto = archivo.read_text()
        texto = texto.replace("http://backend:5000", "http://127.0.0.1:$BACKEND_PORT")
        texto = texto.replace("http://127.0.0.1:5000", "http://127.0.0.1:$BACKEND_PORT")
        texto = texto.replace("http://localhost:5000", "http://127.0.0.1:$BACKEND_PORT")
        archivo.write_text(texto)
PY

if command -v lsof >/dev/null 2>&1; then
    kill -9 $(lsof -ti tcp:$BACKEND_PORT) 2>/dev/null || true
    kill -9 $(lsof -ti tcp:$FRONTEND_PORT) 2>/dev/null || true
fi

echo "Levantando backend en http://127.0.0.1:$BACKEND_PORT"

cd Backend

nohup ../.venv/bin/python -u -c "from appBack import app; app.run(host='127.0.0.1', port=$BACKEND_PORT, debug=False)" > ../logs/backend.log 2>&1 &

cd ..

sleep 3

if ! lsof -i tcp:$BACKEND_PORT >/dev/null 2>&1; then
    echo "ERROR: El backend no levantó"
    echo ""
    echo "LOG DEL BACKEND:"
    cat logs/backend.log
    exit 1
fi

echo "Backend OK"

echo "Levantando frontend en http://127.0.0.1:$FRONTEND_PORT"

cd Frontend

nohup ../.venv/bin/python -u app.py > ../logs/frontend.log 2>&1 &

cd ..

sleep 3

if ! lsof -i tcp:$FRONTEND_PORT >/dev/null 2>&1; then
    echo "ERROR: El frontend no levantó"
    echo ""
    echo "LOG DEL FRONTEND:"
    cat logs/frontend.log
    exit 1
fi

echo ""
echo "Proyecto levantado"
echo "Frontend: http://127.0.0.1:$FRONTEND_PORT"
echo "Backend:  http://127.0.0.1:$BACKEND_PORT"
