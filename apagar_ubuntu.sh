#!/bin/bash

# hacer chmod +x apagarub.sh
# Equivalente a apagar.sh (pensado para Mac) pero para Ubuntu/Debian.
# La logica es identica: busca con lsof que proceso esta usando cada puerto
# y lo mata. lsof funciona igual en Ubuntu, asi que no hace falta adaptar
# nada mas que el mensaje y, por las dudas, ofrecer instalar lsof con apt
# si no estuviera (en Ubuntu minimal a veces no viene preinstalado).

echo "Apagando Altezza sin Docker (Ubuntu)"

cd "$(dirname "$0")"

BACKEND_PORT=5000
FRONTEND_PORT=5001

if ! command -v lsof >/dev/null 2>&1; then
    echo "No se encontró lsof. Instalando..."
    sudo apt-get update -y
    sudo apt-get install -y lsof
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