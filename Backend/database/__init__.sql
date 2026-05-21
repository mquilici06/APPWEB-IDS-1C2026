DROP DATABASE IF EXISTS altezza;
CREATE DATABASE IF NOT EXISTS altezza;
USE altezza;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    celular VARCHAR(20) UNIQUE NOT NULL,
    rol VARCHAR(10) NOT NULL
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
    id_reserva INTEGER AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha_hora DATETIME NOT NULL,  
    cantidad_personas INT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mensajes_contacto (
    id_mensaje INTEGER AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    mensaje VARCHAR(500) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO menu (nombre_plato, desc_plato, precio, restricciones, seccion) VALUES

-- PRINCIPALES
('Gnocchi de Calabaza', 'Ñoquis artesanales con crema de gorgonzola y semillas de calabaza tostadas.', 13500, 'Vegetariano', 'Platos Principales'),
('Spaghetti Frutti di Mare', 'Pasta larga con calamares, langostinos y mejillones en salsa de vino blanco y tomate.', 17000, 'Mariscos', 'Platos Principales'),
('Rigatoni al Pesto Genovés', 'Pasta corta con salsa de albahaca fresca, piñones, ajo y queso parmesano.', 12000, 'Contiene Frutos Secos / Vegetariano', 'Platos Principales'),
('Pappardelle con Ragú de Cordero', 'Pasta ancha con estofado de cordero cocinado a fuego lento durante 8 horas.', 16500, 'Ninguna', 'Platos Principales'),
('Fusilli Sin Gluten Primavera', 'Pasta de maíz con vegetales de temporada salteados en aceite de oliva y ajo.', 14000, 'Sin Gluten / Vegano', 'Platos Principales');

-- POSTRES
('Tiramisú Clásico', 'Bizcochos de soletilla empapados en café espresso, crema de mascarpone y cacao.', 7.50, 'Vegetariano / Contiene Cafeína', 'Postres'),
('Panna Cotta de Frutos Rojos', 'Crema cocida con vainilla natural y coulis de frambuesas frescas.', 6.50, 'Sin Gluten', 'Postres'),
('Cannoli Siciliani', 'Tubos de masa crujiente rellenos de crema de ricotta dulce y chispas de chocolate.', 5.00, 'Vegetariano', 'Postres'),
('Gelato Artesanal (3 bolas)', 'Selección de helados italianos: Vainilla, Chocolate amargo o Pistacho.', 6.00, 'Sin Gluten / Vegetariano', 'Postres'),
('Affogato al Caffè', 'Una bola de helado de vainilla "ahogada" en un shot de espresso caliente.', 5.50, 'Sin Gluten / Vegetariano', 'Postres');

-- BEBIDAS
('Vino Chianti Classico (Copa)', 'Vino tinto italiano de la región de Toscana, ideal para carnes rojas y pastas.', 8.00, 'Contiene Sulfitos', 'Bebidas'),
('Limonata San Pellegrino', 'Bebida gaseosa tradicional italiana de limón natural.', 3.50, 'Vegano / Sin Gluten', 'Bebidas'),
('Cerveza Peroni Nastro Azzurro', 'Cerveza lager italiana premium, ligera y refrescante.', 4.50, 'Contiene Gluten', 'Bebidas'),
('Agua Mineral Acqua Panna', 'Agua mineral sin gas proveniente de los manantiales de la Toscana (500ml).', 3.00, 'Ninguna', 'Bebidas'),
('Aperol Spritz', 'Cóctel refrescante con Aperol, Prosecco, soda y una rodaja de naranja.', 9.00, 'Vegano', 'Bebidas');


INSERT INTO clientes (id, nombre, email, celular) VALUES 
(1, 'Juan Pérez', 'juan@email.com', '1152307414'),
(2, 'María López', 'maria@email.com', '1197487796'),
(3, 'Carlos Gómez', 'carlos@email.com', '1138245976'),
(4, 'Luis Fernández', 'luis@email.com', '1158067048'),
(5, 'Sofía Benítez', 'sofia@email.com', '1164178239'),
(6, 'Ana Rodríguez', 'ana@email.com', '1146756807');


INSERT INTO reservas (cantidad_personas, fecha_hora, id_cliente) VALUES 
(3, '2026-05-17 12:30:00', 1),
(5, '2026-05-17 12:30:00', 4),
(10, '2026-05-18 22:00:00', 5);