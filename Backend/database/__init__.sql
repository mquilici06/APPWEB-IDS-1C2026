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
    restricciones VARCHAR(50), 
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

CREATE TABLE IF NOT EXISTS reservas(
    id_reserva INTEGER AUTO_INCREMENT PRIMARY KEY
);

INSERT INTO menu (nombre_plato, desc_plato, precio, seccion) VALUES

-- ENTRADAS
('Burrata con tomates', 'Burrata cremosa con tomates cherry asados, albahaca fresca y aceite de oliva extra virgen', 1800, 'entradas'),
('Croquetas de jamón', 'Croquetas caseras de jamón serrano con salsa de mostaza antigua', 1200, 'entradas'),
('Carpaccio de res', 'Finas láminas de lomo con rúcula, parmesano y reducción de balsámico', 1600, 'entradas'),

-- PRINCIPALES
('Risotto de hongos', 'Risotto cremoso con mix de hongos silvestres, parmesano y trufa negra', 3200, 'principales'),
('Lomo al malbec', 'Medallón de lomo con reducción de malbec, puré rústico y vegetales grillados', 4500, 'principales'),
('Salmón a la plancha', 'Filete de salmón con salsa de limón y alcaparras, acompañado de quinoa salteada', 3800, 'principales'),
('Pasta fresca al ragú', 'Tagliatelle artesanal con ragú de res cocinado 6 horas y parmesano rallado', 2900, 'principales'),

-- POSTRES
('Tiramisú clásico', 'Receta tradicional con mascarpone, café espresso y cacao amargo', 1100, 'postres'),
('Fondant de chocolate', 'Coulant tibio de chocolate negro 70% con helado de vainilla de Madagascar', 1300, 'postres'),
('Panna cotta de frutos rojos', 'Panna cotta de vainilla con coulis de frutos rojos y menta fresca', 950, 'postres'),

-- BEBIDAS
('Agua mineral', 'Agua sin gas o con gas 500ml', 400, 'bebidas'),
('Limonada de jengibre', 'Limonada artesanal con jengibre fresco y menta', 700, 'bebidas'),
('Copa de vino', 'Selección del sommelier, tinto o blanco', 1200, 'bebidas'),
('Café espresso', 'Espresso doble de origen único', 500, 'bebidas');