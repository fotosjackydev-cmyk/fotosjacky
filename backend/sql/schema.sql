-- =============================================================================
-- Fotos Jacky — Esquema de Base de Datos
-- Ejecutar este SQL en Supabase Dashboard → SQL Editor
-- =============================================================================

-- Habilitar extensión para UUIDs (si no está habilitada)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- =============================================================================
-- CATEGORÍAS
-- =============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    image_url   TEXT,
    position    INT DEFAULT 0,
    active      BOOLEAN DEFAULT true,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_categories_active ON categories(active);

-- Datos iniciales (las 4 categorías de Fotos Jacky)
INSERT INTO categories (name, slug, description, position) VALUES
    ('Cuadros',      'cuadros',      'Cuadros en canvas, madera y más',       1),
    ('Fotolibros',   'fotolibros',   'Fotolibros personalizados',             2),
    ('Impresiones',  'impresiones',  'Impresiones fotográficas de alta calidad', 3),
    ('Regalos',      'regalos',      'Regalos personalizados con tus fotos',  4)
ON CONFLICT (slug) DO NOTHING;


-- =============================================================================
-- PRODUCTOS
-- =============================================================================
CREATE TABLE IF NOT EXISTS products (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id    UUID REFERENCES categories(id) ON DELETE SET NULL,
    name           VARCHAR(200) NOT NULL,
    slug           VARCHAR(200) UNIQUE NOT NULL,
    description    TEXT,
    base_price     DECIMAL(10,2) NOT NULL CHECK (base_price > 0),
    sku            VARCHAR(100),
    weight_grams   INT DEFAULT 500,
    dimensions_cm  JSONB,
    active         BOOLEAN DEFAULT true,
    featured       BOOLEAN DEFAULT false,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(active);
CREATE INDEX IF NOT EXISTS idx_products_featured ON products(featured);
CREATE INDEX IF NOT EXISTS idx_products_name ON products USING gin(to_tsvector('spanish', name));


-- =============================================================================
-- VARIANTES DE PRODUCTO
-- =============================================================================
CREATE TABLE IF NOT EXISTS product_variants (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id      UUID REFERENCES products(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    sku             VARCHAR(100),
    price_modifier  DECIMAL(10,2) DEFAULT 0,
    stock           INT DEFAULT 0 CHECK (stock >= 0),
    active          BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_variants_product ON product_variants(product_id);


-- =============================================================================
-- IMÁGENES DE PRODUCTO
-- =============================================================================
CREATE TABLE IF NOT EXISTS product_images (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id  UUID REFERENCES products(id) ON DELETE CASCADE,
    url         TEXT NOT NULL,
    alt         TEXT,
    position    INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_images_product ON product_images(product_id);


-- =============================================================================
-- CLIENTES (para fase 2 — checkout)
-- =============================================================================
CREATE TABLE IF NOT EXISTS customers (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email       VARCHAR(200) UNIQUE NOT NULL,
    first_name  VARCHAR(100),
    last_name   VARCHAR(100),
    phone       VARCHAR(50),
    dni         VARCHAR(20),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);


-- =============================================================================
-- DIRECCIONES (para fase 2 — envíos)
-- =============================================================================
CREATE TABLE IF NOT EXISTS addresses (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id    UUID REFERENCES customers(id) ON DELETE CASCADE,
    street         VARCHAR(200),
    street_number  VARCHAR(20),
    floor_apt      VARCHAR(50),
    city           VARCHAR(100),
    province       VARCHAR(100),
    postal_code    VARCHAR(10),
    is_default     BOOLEAN DEFAULT false
);


-- =============================================================================
-- ÓRDENES (para fase 2 — checkout)
-- =============================================================================
CREATE TABLE IF NOT EXISTS orders (
    id                 UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number       SERIAL,
    customer_id        UUID REFERENCES customers(id),
    status             VARCHAR(50) DEFAULT 'pending_payment',
    subtotal           DECIMAL(10,2),
    shipping_cost      DECIMAL(10,2),
    total              DECIMAL(10,2),
    shipping_address   JSONB,
    shipping_method    VARCHAR(100),
    shipping_tracking  VARCHAR(200),
    mp_preference_id   VARCHAR(200),
    mp_payment_id      VARCHAR(200),
    mp_status          VARCHAR(50),
    notes              TEXT,
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_number ON orders(order_number);


-- =============================================================================
-- ITEMS DE ÓRDENES (para fase 2)
-- =============================================================================
CREATE TABLE IF NOT EXISTS order_items (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id      UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id    UUID REFERENCES products(id),
    variant_id    UUID REFERENCES product_variants(id),
    product_name  VARCHAR(200),
    variant_name  VARCHAR(100),
    quantity      INT NOT NULL CHECK (quantity > 0),
    unit_price    DECIMAL(10,2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);


-- =============================================================================
-- HISTORIAL DE ESTADOS DE ÓRDENES (para fase 2)
-- =============================================================================
CREATE TABLE IF NOT EXISTS order_status_history (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id    UUID REFERENCES orders(id) ON DELETE CASCADE,
    status      VARCHAR(50),
    note        TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);


-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Habilitar RLS en todas las tablas
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_status_history ENABLE ROW LEVEL SECURITY;

-- Políticas de lectura pública (solo datos activos)
CREATE POLICY "Categorías visibles públicamente"
    ON categories FOR SELECT
    USING (active = true);

CREATE POLICY "Productos visibles públicamente"
    ON products FOR SELECT
    USING (active = true);

CREATE POLICY "Variantes visibles públicamente"
    ON product_variants FOR SELECT
    USING (active = true);

CREATE POLICY "Imágenes visibles públicamente"
    ON product_images FOR SELECT
    USING (true);

-- Políticas de acceso total para service_role (backend)
-- El service_role key bypasea RLS por defecto en Supabase,
-- así que no necesitamos políticas adicionales para el backend.


-- =============================================================================
-- STORAGE BUCKET
-- =============================================================================
-- NOTA: Esto se debe crear manualmente en Supabase Dashboard → Storage
-- Nombre del bucket: product-images
-- Acceso: Público (para que las imágenes se sirvan sin autenticación)
-- Tamaño máximo: 5MB por archivo


-- =============================================================================
-- ✅ Esquema listo. Tablas principales para Fase 1:
--    - categories ✓
--    - products ✓
--    - product_variants ✓
--    - product_images ✓
--
-- Tablas preparadas para Fase 2 (sin usar aún):
--    - customers
--    - addresses
--    - orders
--    - order_items
--    - order_status_history
-- =============================================================================
