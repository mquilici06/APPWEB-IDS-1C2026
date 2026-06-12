#!/bin/bash

# hacer chmod +x apagar.sh

echo "Apagando Altezza sin Docker"

cd "$(dirname "$0")"

BACKEND_PORT=5000
FRONTEND_PORT=5001

if ! command -v lsof >/dev/null 2>&1; then
    echo "ERROR: No se encontró lsof"
    exit 1
fi

BACKEND_PID=$(lsof -ti tcp:$BACKEND_PORT)
FRONTEND_PID=$(lsof -ti tcp:$FRONTEND_PORT)

if [ -n "$BACKEND_PID" ]; then
    echo "Apagando backend en puerto $BACKEND_PORT..."
    kill -9 $BACKEND_PID 2>/dev/null || true
else
    echo "No había backend corriendo en puerto $BACKEND_PORT"
fi

if [ -n "$FRONTEND_PID" ]; then
    echo "Apagando frontend en puerto $FRONTEND_PORT..."
    kill -9 $FRONTEND_PID 2>/dev/null || true
else
    echo "No había frontend corriendo en puerto $FRONTEND_PORT"
fi

echo ""
echo "Proyecto apagado"