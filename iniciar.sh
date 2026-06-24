#!/bin/bash

# hacer chmod +x iniciar.sh

set -e

echo "Levantando Altezza sin Docker"

cd "$(dirname "$0")" # cd $0 para entrar a la direccion del script

BACKEND_PORT=5000
FRONTEND_PORT=5001

mkdir -p logs

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: No se encontró python3"
    exit 1
fi

if ! command -v lsof >/dev/null 2>&1; then
    echo "ERROR: No se encontró lsof"
    exit 1
fi

if ! command -v mysql >/dev/null 2>&1; then
    echo "ERROR: No se encontró mysql"
    echo "Instalá MySQL o agregalo al PATH"
    exit 1
fi

if ! command -v mysqladmin >/dev/null 2>&1; then
    echo "ERROR: No se encontró mysqladmin"
    echo "Instalá MySQL o agregalo al PATH"
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
    echo "Creando entorno virtual..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Instalando dependencias..."
python -m pip install --upgrade pip
pip install -r requirements.txt

export DB_HOST="${DB_HOST:-127.0.0.1}"
export DB_PORT="${DB_PORT:-3306}"
export DB_USER="${DB_USER:-}" # cambiar usuario
export DB_PASSWORD="${DB_PASSWORD:-!}" # ver contraseña
export DB_NAME="${DB_NAME:-altezza}"

export BACKEND_URL="http://127.0.0.1:$BACKEND_PORT"

#Verificar / iniciar MySQL local

echo "Verificando MySQL local"

if ! mysqladmin -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" ping --silent >/dev/null 2>&1; then
    echo "MySQL no responde. Intentando iniciarlo con Homebrew..."

    if command -v brew >/dev/null 2>&1; then
        brew services start mysql >/dev/null 2>&1 || true
        brew services start mysql@8.0 >/dev/null 2>&1 || true
        brew services start mysql@9.0 >/dev/null 2>&1 || true
        sleep 3
    fi
fi

if ! mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
    echo "ERROR: No se pudo conectar a MySQL local"
    echo ""
    echo "Datos usados:"
    echo "DB_HOST=$DB_HOST"
    echo "DB_PORT=$DB_PORT"
    echo "DB_USER=$DB_USER"
    echo "DB_PASSWORD=$DB_PASSWORD"
    echo "DB_NAME=$DB_NAME"
    echo ""
    echo "Probá iniciar MySQL manualmente:"
    echo "brew services start mysql"
    exit 1
fi

echo "MySQL conectado correctamente"

#Crear base si no existe

mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" \
    -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Importar SQL inicial solo si la base está vacia

TABLE_COUNT=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -N -B \
    -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$DB_NAME';")

INIT_SQL="Backend/database/__init__.sql"

if [ "$TABLE_COUNT" -eq 0 ]; then
    if [ -f "$INIT_SQL" ]; then
        echo "La base está vacía. Importando SQL inicial desde $INIT_SQL..."
        mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$INIT_SQL"
        echo "Base importada correctamente"
    else
        echo "ADVERTENCIA: La base está vacía, pero no se encontró $INIT_SQL"
    fi
else
    echo "La base ya tiene tablas. No se importa SQL inicial"
fi

echo "Apagando procesos anteriores si existen..."

# List Open Files(lsof), para listar los archivos abiertos y asi poder cerrar los procesos para liberar puertos

kill -9 $(lsof -ti tcp:$BACKEND_PORT) 2>/dev/null || true
kill -9 $(lsof -ti tcp:$FRONTEND_PORT) 2>/dev/null || true

echo "Levantando backend en http://127.0.0.1:$BACKEND_PORT"

cd Backend

# nohup (no hang up), para que cuando cierre la terminal no mate todos los procesos hijos.

nohup ../.venv/bin/python -u -c "from appBack import app; app.run(host='127.0.0.1', port=$BACKEND_PORT, debug=False)" > ../logs/backend.log 2>&1 & # arranca el servidor del back

cd ..

sleep 3

if ! lsof -i tcp:$BACKEND_PORT >/dev/null 2>&1; then
    echo "ERROR: El backend no levantó"
    echo ""
    echo "LOG DEL BACKEND:"
    cat logs/backend.log
    exit 1
fi

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
echo "Proyecto levantado correctamente"
echo ""
echo "Frontend: http://127.0.0.1:$FRONTEND_PORT"
echo "Backend:  http://127.0.0.1:$BACKEND_PORT"
echo "MySQL:    $DB_HOST:$DB_PORT"