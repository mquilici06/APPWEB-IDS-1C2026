DROP DATABASE IF EXISTS altezza;
CREATE DATABASE IF NOT EXISTS altezza;
USE altezza;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    celular VARCHAR(20) UNIQUE NOT NULL,
    rol VARCHAR(10) NOT NULL,
    contrasena varchar(255)
);

CREATE TABLE IF NOT EXISTS resenas (
    id_resena INTEGER AUTO_INCREMENT PRIMARY KEY,
    id_cliente INTEGER,
    mensaje VARCHAR(500),
    puntuacion INTEGER,
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id) ON DELETE CASCADE
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
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reservas (
    id_reserva INTEGER AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    cantidad_personas INT NOT NULL,
    estado VARCHAR(20) DEFAULT 'confirmada',
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id) ON DELETE CASCADE
);

INSERT INTO menu (nombre_plato, desc_plato, precio, restricciones, seccion) VALUES
('Gnocchi de Calabaza', 'Ñoquis artesanales con crema de gorgonzola y semillas de calabaza tostadas.', 13500, 'Vegetariano', 'Platos Principales'),
('Spaghetti Frutti di Mare', 'Pasta larga con calamares, langostinos y mejillones en salsa de vino blanco y tomate.', 17000, 'Mariscos', 'Platos Principales'),
('Rigatoni al Pesto Genoves', 'Pasta corta con salsa de albahaca fresca, pinones, ajo y queso parmesano.', 12000, 'Contiene Frutos Secos / Vegetariano', 'Platos Principales'),
('Pappardelle con Ragu de Cordero', 'Pasta ancha con estofado de cordero cocinado a fuego lento durante 8 horas.', 16500, 'Ninguna', 'Platos Principales'),
('Fusilli Sin Gluten Primavera', 'Pasta de maiz con vegetales de temporada salteados en aceite de oliva y ajo.', 14000, 'Sin Gluten / Vegano', 'Platos Principales'),
('Tiramisu Clasico', 'Bizcochos de soletilla empapados en cafe espresso, crema de mascarpone y cacao.', 7500, 'Vegetariano', 'Postres'),
('Panna Cotta de Frutos Rojos', 'Crema cocida con vainilla natural y coulis de frambuesas frescas.', 6500, 'Sin Gluten', 'Postres'),
('Cannoli Siciliani', 'Tubos de masa crujiente rellenos de crema de ricotta dulce y chispas de chocolate.', 5000, 'Vegetariano', 'Postres'),
('Gelato Artesanal (3 bolas)', 'Seleccion de helados italianos: Vainilla, Chocolate amargo o Pistacho.', 6000, 'Sin Gluten / Vegetariano', 'Postres'),
('Affogato al Caffe', 'Una bola de helado de vainilla ahogada en un shot de espresso caliente.', 5500, 'Sin Gluten / Vegetariano', 'Postres'),
('Vino Chianti Classico (Copa)', 'Vino tinto italiano de la region de Toscana, ideal para carnes rojas y pastas.', 8000, 'Contiene Sulfitos', 'Bebidas'),
('Limonata San Pellegrino', 'Bebida gaseosa tradicional italiana de limon natural.', 3500, 'Vegano / Sin Gluten', 'Bebidas'),
('Cerveza Peroni Nastro Azzurro', 'Cerveza lager italiana premium, ligera y refrescante.', 4500, 'Contiene Gluten', 'Bebidas'),
('Agua Mineral Acqua Panna', 'Agua mineral sin gas proveniente de los manantiales de la Toscana (500ml).', 3000, 'Ninguna', 'Bebidas'),
('Aperol Spritz', 'Coctel refrescante con Aperol, Prosecco, soda y una rodaja de naranja.', 9000, 'Vegano', 'Bebidas');

INSERT INTO usuarios (id, nombre, email, celular, rol, contrasena) VALUES /*contraseña de los ususarios 123456*/
(1, 'Juan Pérez', 'juan@email.com', '1152307414', 'cliente', '$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(2, 'María López', 'maria@email.com', '1197487796', 'cliente','$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(3, 'Carlos Gómez', 'carlos@email.com', '1138245976', 'cliente','$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(4, 'Luis Fernández', 'luis@email.com', '1158067048', 'cliente','$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(5, 'Sofía Benítez', 'sofia@email.com', '1164178239', 'cliente','$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(6, 'Ana Rodríguez', 'ana@email.com', '1146756807', 'cliente','$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC');

INSERT INTO reservas (id_reserva, id_cliente, fecha, hora, cantidad_personas, estado) VALUES
(1, 1, '2026-05-25', '12:30', 2, 'confirmada'),
(2, 2, '2026-05-28', '21:00', 4, 'confirmada'),
(3, 3, '2026-06-05', '13:15', 6, 'pendiente'),
(4, 4, '2026-06-07', '20:45', 2, 'confirmada'),
(5, 5, '2026-06-12', '22:00', 5, 'cancelada');