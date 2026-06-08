#!/bin/bash

set -e

echo "=== iniciando entorno de Altezza ==="


fuser -k 5000/tcp 2>/dev/null || true

fuser -k 5001/tcp 2>/dev/null || true


if ! command -v python3 &> /dev/null; then
    echo "Python3 no está instalado. Instalando..."
    sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-full python3-venv
else
    echo "Python3 ya está instalado."
fi


echo "Levantando Base de Datos..."

docker-compose up -d db


if [ ! -d ".venv" ]; then
    echo "Creando ambiente virtual..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Instalando dependencias..."

.venv/bin/pip install -r requirements.txt


echo "Iniciando Backend..."


python3 Backend/appBack.py &


echo "Iniciando Frontend"
echo "corriendo en http://localhost:5001"


python3 Frontend/app.py