DROP DATABASE IF EXISTS altezza;
CREATE DATABASE IF NOT EXISTS altezza;
USE altezza;

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    celular INTEGER UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS resenas (
    id_resena INTEGER AUTO_INCREMENT PRIMARY KEY,
    id_cliente INTEGER,
    mensaje VARCHAR(500),
    puntuacion INTEGER,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS menu (
    id_menu INTEGER AUTO_INCREMENT PRIMARY KEY,
    nombre_plato VARCHAR(50) NOT NULL,
    desc_plato VARCHAR(200) NOT NULL,
    precio INTEGER NOT NULL,
    seccion VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS estadisticas (
    id_cliente INTEGER PRIMARY KEY,
    cant_reservas INTEGER,
    reservas_asistidas INTEGER,
    reservas_canceladas INTEGER,
    cant_resenas INTEGER,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reservas