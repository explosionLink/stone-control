-- SQL/01_schema_supabase.sql
-- Questo script definisce la struttura delle tabelle nel schema public

-- Abilita l'estensione pgcrypto se non presente
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Tabella per i ruoli applicativi
CREATE TABLE IF NOT EXISTS public.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_public_roles_name ON public.roles (name);

-- 2. Tabella ponte per associare gli utenti ai ruoli
CREATE TABLE IF NOT EXISTS public.user_supabase_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES public.roles (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_user_supabase_role UNIQUE (user_id, role_id)
);

CREATE INDEX IF NOT EXISTS ix_public_user_supabase_roles_role_id ON public.user_supabase_roles (role_id);

-- 3. Tabella Clienti
CREATE TABLE IF NOT EXISTS public.clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Tabella Ordini
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(64) NOT NULL UNIQUE,
    user_id UUID REFERENCES auth.users (id) ON DELETE CASCADE,
    client_id UUID REFERENCES public.clients (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Tabella Poligoni (Pezzi dell'ordine)
CREATE TABLE IF NOT EXISTS public.polygons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES public.orders (id) ON DELETE CASCADE,
    label VARCHAR(255),
    width_mm FLOAT NOT NULL,
    height_mm FLOAT NOT NULL,
    material VARCHAR(255),
    thickness_mm FLOAT,
    is_mirrored BOOLEAN DEFAULT FALSE,
    preview_path VARCHAR(512),
    technical_preview_path VARCHAR(512),
    dxf_path VARCHAR(512),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Tabella Fori (Lavorazioni)
CREATE TABLE IF NOT EXISTS public.holes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    polygon_id UUID NOT NULL REFERENCES public.polygons (id) ON DELETE CASCADE,
    type VARCHAR(64),
    x_mm FLOAT NOT NULL,
    y_mm FLOAT NOT NULL,
    width_mm FLOAT,
    height_mm FLOAT,
    diameter_mm FLOAT,
    depth_mm FLOAT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 7. Libreria Fori
CREATE TABLE IF NOT EXISTS public.hole_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(64),
    width_mm FLOAT,
    height_mm FLOAT,
    diameter_mm FLOAT,
    depth_mm FLOAT,
    created_at TIMESTAMPTZ DEFAULT now()
);
