-- =============================================================================
-- FOTOS JACKY — MIGRACIÓN INICIAL (PostgreSQL / Supabase)
-- =============================================================================
-- Script completo para crear la base de datos desde cero en un proyecto nuevo.
--
-- CÓMO USARLO:
--   1. Entrá a tu proyecto de Supabase → SQL Editor → New query
--   2. Pegá TODO este archivo
--   3. Apretá "Run"
--   4. Listo: tablas, índices, triggers y categorías base quedan creadas.
--
-- Es idempotente: lo podés correr más de una vez sin romper nada.
-- =============================================================================


-- =============================================================================
-- 0. EXTENSIONES
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- =============================================================================
-- 1. CATEGORÍAS
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


-- =============================================================================
-- 2. PRODUCTOS
-- =============================================================================
CREATE TABLE IF NOT EXISTS products (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id   UUID REFERENCES categories(id) ON DELETE SET NULL,
    name          VARCHAR(200) NOT NULL,
    slug          VARCHAR(200) UNIQUE NOT NULL,
    description   TEXT,
    base_price    DECIMAL(10,2) NOT NULL,
    sku           VARCHAR(100),
    weight_grams  INT DEFAULT 500,
    dimensions_cm JSONB,
    active        BOOLEAN DEFAULT true,
    featured      BOOLEAN DEFAULT false,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);


-- =============================================================================
-- 3. VARIANTES DE PRODUCTO (tamaños, acabados)
-- =============================================================================
CREATE TABLE IF NOT EXISTS product_variants (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id     UUID REFERENCES products(id) ON DELETE CASCADE,
    name           VARCHAR(100) NOT NULL,
    sku            VARCHAR(100),
    price_modifier DECIMAL(10,2) DEFAULT 0,
    stock          INT DEFAULT 0,
    active         BOOLEAN DEFAULT true
);


-- =============================================================================
-- 4. IMÁGENES DE PRODUCTO
-- =============================================================================
CREATE TABLE IF NOT EXISTS product_images (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    url        TEXT NOT NULL,
    alt        TEXT,
    position   INT DEFAULT 0
);


-- =============================================================================
-- 5. CLIENTES
-- =============================================================================
CREATE TABLE IF NOT EXISTS customers (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email      VARCHAR(200) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name  VARCHAR(100),
    phone      VARCHAR(50),
    dni        VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- =============================================================================
-- 6. DIRECCIONES
-- =============================================================================
CREATE TABLE IF NOT EXISTS addresses (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id   UUID REFERENCES customers(id) ON DELETE CASCADE,
    street        VARCHAR(200),
    street_number VARCHAR(20),
    floor_apt     VARCHAR(50),
    city          VARCHAR(100),
    province      VARCHAR(100),
    postal_code   VARCHAR(10),
    is_default    BOOLEAN DEFAULT false
);


-- =============================================================================
-- 7. ÓRDENES
-- =============================================================================
CREATE TABLE IF NOT EXISTS orders (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number      SERIAL UNIQUE,
    customer_id       UUID REFERENCES customers(id) ON DELETE SET NULL,
    status            VARCHAR(50) DEFAULT 'pending_payment',
    subtotal          DECIMAL(10,2),
    shipping_cost     DECIMAL(10,2) DEFAULT 0,
    total             DECIMAL(10,2),
    shipping_address  JSONB,
    shipping_method   VARCHAR(100),
    shipping_tracking VARCHAR(200),
    mp_preference_id  VARCHAR(200),
    mp_payment_id     VARCHAR(200),
    mp_status         VARCHAR(50),
    notes             TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);


-- =============================================================================
-- 8. ITEMS DE ÓRDENES
-- =============================================================================
CREATE TABLE IF NOT EXISTS order_items (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id     UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id   UUID REFERENCES products(id) ON DELETE SET NULL,
    variant_id   UUID REFERENCES product_variants(id) ON DELETE SET NULL,
    product_name VARCHAR(200),
    variant_name VARCHAR(100),
    quantity     INT NOT NULL,
    unit_price   DECIMAL(10,2) NOT NULL
);


-- =============================================================================
-- 9. HISTORIAL DE ESTADOS DE ÓRDENES
-- =============================================================================
CREATE TABLE IF NOT EXISTS order_status_history (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id   UUID REFERENCES orders(id) ON DELETE CASCADE,
    status     VARCHAR(50),
    note       TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- =============================================================================
-- 10. ÍNDICES (rendimiento)
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_products_category     ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_slug         ON products(slug);
CREATE INDEX IF NOT EXISTS idx_products_active       ON products(active);
CREATE INDEX IF NOT EXISTS idx_products_featured     ON products(featured);
CREATE INDEX IF NOT EXISTS idx_variants_product      ON product_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_images_product        ON product_images(product_id);
CREATE INDEX IF NOT EXISTS idx_customers_email       ON customers(email);
CREATE INDEX IF NOT EXISTS idx_addresses_customer    ON addresses(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer       ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status         ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order     ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_status_history_order  ON order_status_history(order_id);


-- =============================================================================
-- 11. TRIGGER: actualizar updated_at automáticamente en órdenes
-- =============================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_orders_updated_at ON orders;
CREATE TRIGGER trg_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();


-- =============================================================================
-- 12. SEGURIDAD (Row Level Security)
-- =============================================================================
-- El backend usa la SERVICE_ROLE key, que ignora RLS (acceso total).
-- Activamos RLS SIN crear políticas públicas => la ANON key queda bloqueada
-- y nadie puede leer/escribir la base directamente desde el navegador.
-- Todo pasa obligatoriamente por la API de FastAPI. Es lo más seguro.
ALTER TABLE categories            ENABLE ROW LEVEL SECURITY;
ALTER TABLE products              ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_variants      ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_images        ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers             ENABLE ROW LEVEL SECURITY;
ALTER TABLE addresses             ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders                ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items           ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_status_history  ENABLE ROW LEVEL SECURITY;


-- =============================================================================
-- 13. DATOS INICIALES — Categorías base de Fotos Jacky
-- =============================================================================
INSERT INTO categories (name, slug, description, position) VALUES
    ('Fotolibros',  'fotolibros',  'Fotolibros premium para tus recuerdos',          1),
    ('Cuadros',     'cuadros',     'Cuadros en lienzo, gigantografías y bastidores', 2),
    ('Impresiones', 'impresiones', 'Impresiones fotográficas en todos los tamaños',  3),
    ('Regalos',     'regalos',     'Regalos fotográficos personalizados',            4)
ON CONFLICT (slug) DO NOTHING;


-- =============================================================================
-- FIN — Base de datos lista para usar
-- =============================================================================
