#!/bin/bash
# hacer chmod +x apagar.sh

echo "Apagando Altezza sin Docker..."

BACKEND_PORT=5000
FRONTEND_PORT=5001

if command -v lsof >/dev/null 2>&1; then
    kill -9 $(lsof -ti tcp:$BACKEND_PORT) 2>/dev/null || true
    kill -9 $(lsof -ti tcp:$FRONTEND_PORT) 2>/dev/null || true
else
    echo "ERROR: No se encontró lsof. Cerrá los procesos manualmente."
    exit 1
fi

echo "Backend apagado: puerto $BACKEND_PORT"
echo "Frontend apagado: puerto $FRONTEND_PORT"
echo "Proyecto apagado."