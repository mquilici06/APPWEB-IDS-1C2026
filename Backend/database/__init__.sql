DROP DATABASE IF EXISTS altezza;
CREATE DATABASE IF NOT EXISTS altezza;
USE altezza;
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    celular VARCHAR(20) UNIQUE NOT NULL,
    rol VARCHAR(10) NOT NULL,
    contrasena VARCHAR(255)
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
    seccion VARCHAR(20),
    imagen LONGTEXT  
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
    notas VARCHAR(300),
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS servicios_extras (
    id_servicio INTEGER AUTO_INCREMENT PRIMARY KEY,
    nombre_servicio VARCHAR(100) NOT NULL UNIQUE,
    descripcion_servicio VARCHAR(255) NOT NULL,
    imagen VARCHAR(100)
);


INSERT INTO menu (nombre_plato, desc_plato, precio, restricciones, seccion, imagen) VALUES
('Spaghetti alla carbonara', 'Queso pecorino, crema, panceta y yema de huevo', '32000', '', 'Platos Principales', 'carbonara.png'),
('Bucatini con polpette di vitello', 'Pasta seca italiana, pomodoro, morrones, cebolla, ajo, albahaca y albóndigas de ternera', '32000', '', 'Platos Principales','bucatini.png'),
('Trofie al pesto genovese', 'Receta original del pesto genovés', '32000', 'Vegetariano', 'Platos Principales','trofie.png'),
('Tagliolini nere panna e gamberi', 'Crema y langostinos', '34500', '', 'Platos Principales','tagliolini.png'),
('Spaghetti cacio e pepe', 'Queso pecorino estacionado y pimienta negra', '32000', 'Vegetariano', 'Platos Principales', 'cacio-e-pepe.png'),
('Spaghetti alla napoletana', 'Pesto de pomodoro secos con pesto di basilico e burrata', '32000', 'Vegetariano', 'Platos Principales', 'spaghetti-napoletana.png'),
('Spaghetti DE CECCO ai frutti di mare', 'Spaghetti seco italiano, pomodoro, langostinos, calamar, vieiras, chipirones, almejas y mejillones', '39000', '', 'Platos Principales', 'spaghetti-de-cecco.png'),
('Cuerdas de guitarra pomodoro e basilico', 'Pomodoro y albahaca', '32000', 'Vegetariano', 'Platos Principales', 'cuerdas.png'),
('Rigatoni DE CECCO all'' arrabbiata', 'Pomodoro, ajo, peperoncino, tomate concasse, oliva y perejil', '32000', 'Vegetariano/Vegano', 'Platos Principales','rigatoni.png'),
('Malfatti di spinaci', 'Espinaca y ricota gratinado con crema, pomodoro y parmesano', '32000', 'Vegetariano', 'Platos Principales','malfatti.png'),
('Fettuccine funghi e oleo di trufa', 'Crema di funghi e óleo de trufa', '32000', '', 'Platos Principales','fettuccine.png'),
('Fettuccine Alfredo', 'Crema, parmesano y yema de huevo', '32000', '', 'Platos Principales','falfredo.png'),
('Fusilli al fierrito don corleone', 'Pomodoro, oliva, ajo, aceitunas negras y alcaparras', '32000', 'Vegetariano', 'Platos Principales','fusilli.png'),
('Penne Rigate pomodoro e basilico - sin tacc', 'Pomodoro y albahaca', '32000', 'Sin TACC', 'Platos Principales','penne.png'),
('Flan de claras', 'Flan de claras con confitura de naranja, yogurt de vainilla, almendras y pasas de uva', '14500', 'Sin TACC', 'Postres','flan.png'),
('Tiramisú al mascarpone', 'Clásico tiramisú con Mascarpone', '14500', '', 'Postres','tiramisu.png'),
('Seduzione di cioccolato', 'Volcán de chocolate con helado de crema', '14500', '', 'Postres','volcan.png'),
('Crepe de dulce de leche', 'Crepé de dulce de leche con helado de crema', '14500', '', 'Postres','crepe.png'),
('Tatén di mela con gelato', 'Tarta tibia de manzana con helado de crema y crocante de nuez', '14500', '', 'Postres','taten.png'),
('Merengatta', 'Merengue italiano, helado de crema y frutillas', '14500', '', 'Postres','merengata.png'),
('Mousse di cioccolato - Sin tacc', 'Soufflé de chocolate con crema chantilly y prelinee de almendras', '14500', 'Sin TACC', 'Postres','mousse.png'),
('Piccola torta di limone', 'Pequeña torta de limón con salsa de frutos del bosque', '14500', '', 'Postres','torta.png'),
('Gelato', 'Helado de la casa', '14500', 'Vegetariano', 'Postres','helado.png'),
('Gaseosas - (Linea pepsi)', '', '5000', '', 'Bebidas',NULL),
('Agua Mineral', '', '5000', '', 'Bebidas',NULL),
('We by Ser (Citrus - Lemon)', '', '5000', '', 'Bebidas',NULL),
('Limonada', '', '6200', '', 'Bebidas',NULL),
('Villa del Sur Levité', '', '5000', '', 'Bebidas',NULL),
('Jugo Exprimido de Naranja', '', '6200', '', 'Bebidas',NULL),
('Heineken (330 cc)', '', '6300', '', 'Bebidas',NULL),
('Warsteiner (330 cc)', '', '6500', '', 'Bebidas',NULL),
('Blue Moon (355 cc)', '', '6500', '', 'Bebidas',NULL),
('Miller (355 cc)', '', '6250', '', 'Bebidas',NULL),
('Heineken 0.0 - sin alcohol (355 cc)', '', '6300', '', 'Bebidas',NULL),
('Ramazzotti Spritz', 'Aperitivo Ramazzotti rosato, Espumante y Rodaja de Limón', '10500', '', 'Bebidas',NULL),
('Ramazzotti Tonic', 'Aperitivo Ramazzotti rosato, Agua tónica y Rodaja de Limón', '10500', '', 'Bebidas',NULL);


INSERT INTO usuarios (id, nombre, email, celular, rol, contrasena) VALUES /*contraseña de los ususarios 123456*/
(1, 'Juan Pérez', 'juan@email.com', '1152307414', 'cliente', '$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(2, 'María López', 'maria@email.com', '1197487796', 'cliente','$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(3, 'Carlos Gómez', 'carlos@email.com', '1138245976', 'cliente','$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(4, 'Luis Fernández', 'luis@email.com', '1158067048', 'cliente','$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(5, 'Sofía Benítez', 'sofia@email.com', '1164178239', 'cliente','$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(6, 'Ana Rodríguez', 'ana@email.com', '1146756807', 'cliente','$2b$12$FlVTkmP6BkjRtN7./D/gR.lhY6w1gPJiywd9vfHs8adIhH4dqYGZC'),
(7, 'Admin', 'admin@altezza.com', '1111111111', 'admin', '$2b$12$QLqWGYxA94vIYOiBYZqmkOTzsIgs.G8/gWOJZbDBgM9m9nXCVfG/6');


INSERT INTO reservas (id_reserva, id_cliente, fecha, hora, cantidad_personas, estado) VALUES
(1, 1, '2026-05-25', '12:30', 2, 'confirmada'),
(2, 2, '2026-05-28', '21:00', 4, 'confirmada'),
(3, 3, '2026-06-05', '13:15', 6, 'pendiente'),
(4, 4, '2026-06-07', '20:45', 2, 'confirmada'),
(5, 5, '2026-06-12', '22:00', 5, 'cancelada');


INSERT INTO resenas (id_resena, id_cliente, mensaje, puntuacion) VALUES
(1, 1, 'Excelente servicio, muy buena atención.', 5),
(2, 2, 'La comida llegó fría, podría mejorar.', 3),
(3, 3, 'Muy buena experiencia, volvería sin dudas.', 4),
(4, 1, 'El lugar estaba limpio y el personal fue amable.', 5),
(5, 4, 'Demoraron mucho en atender.', 2);

 
INSERT INTO servicios_extras (nombre_servicio, descripcion_servicio, imagen) VALUES
('Playa de Estacionamiento', 'Estacionamiento exclusivo y gratuito para clientes durante su estadía en el local.', 'estacionamiento.png'),
('Acceso para Discapacitados', 'Rampas de acceso, pasillos amplios y baños totalmente adaptados para movilidad reducida.', 'acceso_discapacitados.png'),
('Conectividad Wi-Fi de Alta Velocidad', 'Red de internet simétrica de uso libre para clientes en todo el establecimiento.', 'wifi.png'),
('Mesas al Aire Libre / Terraza', 'Opción de reserva de mesas en sectores exteriores climatizados (patio o terraza).', 'terraza.png'),
('Menú Digital QR en Mesa', 'Acceso al menú completo con filtros interactivos para alérgenos y restricciones desde el celular.', 'qr.png');
 