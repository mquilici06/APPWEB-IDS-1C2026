#!/bin/bash

# hacer chmod +x iniciar_ubuntu.sh
# Equivalente a iniciar.sh (pensado para Mac/Homebrew) pero para Ubuntu/Debian (apt + systemctl).
# Lee credenciales de Backend/.env si existe; si no, las pide por consola.

set -e

echo "Levantando Altezza sin Docker (Ubuntu)"

cd "$(dirname "$0")" # cd a la carpeta donde esta el script

BACKEND_PORT=5000
FRONTEND_PORT=5001

mkdir -p logs

# -----------------------------------------------------------
# 1) Verificar / instalar dependencias del sistema
# -----------------------------------------------------------

NEEDS_APT_UPDATE=true

apt_update_once() {
    if [ "$NEEDS_APT_UPDATE" = true ]; then
        echo "Actualizando indices de apt (puede pedir contraseña de sudo)..."
        sudo apt-get update -y
        NEEDS_APT_UPDATE=false
    fi
}

if ! command -v python3 >/dev/null 2>&1; then
    echo "No se encontró python3. Instalando..."
    apt_update_once
    sudo apt-get install -y python3
fi

if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "No se encontró el modulo venv de python3. Instalando python3-venv..."
    apt_update_once
    sudo apt-get install -y python3-venv
fi

if ! command -v pip3 >/dev/null 2>&1; then
    echo "No se encontró pip3. Instalando python3-pip..."
    apt_update_once
    sudo apt-get install -y python3-pip
fi

if ! command -v lsof >/dev/null 2>&1; then
    echo "No se encontró lsof. Instalando..."
    apt_update_once
    sudo apt-get install -y lsof
fi

if ! command -v mysql >/dev/null 2>&1 || ! command -v mysqladmin >/dev/null 2>&1; then
    echo "No se encontró MySQL. Instalando mysql-server y mysql-client..."
    apt_update_once
    sudo apt-get install -y mysql-server mysql-client
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

# -----------------------------------------------------------
# 2) Entorno virtual e instalacion de dependencias de Python
# -----------------------------------------------------------

if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Instalando dependencias..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# -----------------------------------------------------------
# 3) Credenciales de la base de datos
#    Prioridad: variables ya exportadas > Backend/.env > input manual
# -----------------------------------------------------------

ENV_FILE="Backend/.env"

# Si Backend/.env existe, lo cargamos para tomar de ahi lo que tenga (sin pisar
# variables que el usuario ya haya exportado a mano antes de correr el script)
if [ -f "$ENV_FILE" ]; then
    echo "Encontrado $ENV_FILE, cargando variables desde ahi..."
    set -a
    # shellcheck disable=SC1090
    source <(grep -v '^\s*#' "$ENV_FILE" | grep -v '^\s*$')
    set +a
else
    echo "No se encontró $ENV_FILE. Las credenciales se pedirán por consola."
fi

# Defaults / fallback a input manual si algo falta
export DB_HOST="${DB_HOST:-127.0.0.1}"
export DB_PORT="${DB_PORT:-3306}"
export DB_NAME="${DB_NAME:-altezza}"

if [ -z "$DB_USER" ]; then
    read -rp "Usuario de MySQL (ej: root): " DB_USER
    export DB_USER
fi

if [ -z "$DB_PASSWORD" ]; then
    read -rsp "Contraseña de MySQL para $DB_USER: " DB_PASSWORD
    echo ""
    export DB_PASSWORD
fi

# Si Backend/.env no existia, lo creamos con lo que se ingreso + el resto de
# las variables que necesita la app (SECRET_KEY/JWT/MAIL), para no tener que
# pedirlas de nuevo la proxima vez.
if [ ! -f "$ENV_FILE" ]; then
    echo "Creando $ENV_FILE con los datos ingresados..."

    if [ -z "$SECRET_KEY" ]; then
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")
    fi
    if [ -z "$JWT_SECRET_KEY" ]; then
        JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")
    fi

    cat > "$ENV_FILE" <<EOF
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY

DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=$DB_NAME

MAIL_SERVER=${MAIL_SERVER:-smtp.gmail.com}
MAIL_PORT=${MAIL_PORT:-587}
MAIL_USE_TLS=${MAIL_USE_TLS:-True}
MAIL_USE_SSL=${MAIL_USE_SSL:-False}
MAIL_USERNAME=${MAIL_USERNAME:-}
MAIL_PASSWORD=${MAIL_PASSWORD:-}
MAIL_DEFAULT_SENDER=${MAIL_DEFAULT_SENDER:-}
EOF

    echo "Se creó $ENV_FILE. Si querés mandar mails reales, completá las variables MAIL_* a mano."
fi

# El Frontend tambien necesita su propio .env (SECRET_KEY + MAIL_*, no usa DB directo)
FRONTEND_ENV_FILE="Frontend/.env"
if [ ! -f "$FRONTEND_ENV_FILE" ]; then
    echo "Creando $FRONTEND_ENV_FILE..."
    cat > "$FRONTEND_ENV_FILE" <<EOF
SECRET_KEY=${SECRET_KEY}

MAIL_SERVER=${MAIL_SERVER:-smtp.gmail.com}
MAIL_PORT=${MAIL_PORT:-587}
MAIL_USE_TLS=${MAIL_USE_TLS:-True}
MAIL_USE_SSL=${MAIL_USE_SSL:-False}
MAIL_USERNAME=${MAIL_USERNAME:-}
MAIL_PASSWORD=${MAIL_PASSWORD:-}
MAIL_DEFAULT_SENDER=${MAIL_DEFAULT_SENDER:-}
EOF
fi

export BACKEND_URL="http://127.0.0.1:$BACKEND_PORT"

# -----------------------------------------------------------
# 4) Verificar / iniciar MySQL local (systemctl en vez de brew)
# -----------------------------------------------------------

echo "Verificando MySQL local"

if ! mysqladmin -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" ping --silent >/dev/null 2>&1; then
    echo "MySQL no responde. Intentando iniciarlo con systemctl..."

    if command -v systemctl >/dev/null 2>&1; then
        sudo systemctl start mysql >/dev/null 2>&1 || sudo systemctl start mysqld >/dev/null 2>&1 || true
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
    echo "sudo systemctl start mysql"
    echo ""
    echo "Si nunca configuraste una contraseña para root, en una instalación"
    echo "nueva de mysql-server en Ubuntu puede que necesites entrar primero con:"
    echo "sudo mysql"
    echo "y crear ahí un usuario con contraseña, por ejemplo:"
    echo "  ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'tu_password';"
    echo "  FLUSH PRIVILEGES;"
    exit 1
fi

echo "MySQL conectado correctamente"

# -----------------------------------------------------------
# 5) Crear base si no existe / importar SQL inicial si está vacía
# -----------------------------------------------------------

mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" \
    -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

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

# -----------------------------------------------------------
# 6) Liberar puertos y levantar backend + frontend
# -----------------------------------------------------------

echo "Apagando procesos anteriores si existen..."

kill -9 $(lsof -ti tcp:$BACKEND_PORT) 2>/dev/null || true
kill -9 $(lsof -ti tcp:$FRONTEND_PORT) 2>/dev/null || true

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