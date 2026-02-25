-- SQL Setup per Supabase
-- Questo script crea le tabelle necessarie per la gestione dei ruoli nel public schema.

-- 1. Tabella per i ruoli applicativi
CREATE TABLE IF NOT EXISTS public.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indice per velocizzare la ricerca per nome
CREATE INDEX IF NOT EXISTS ix_public_roles_name ON public.roles (name);

-- 2. Tabella ponte per associare gli utenti (schema auth.users) ai ruoli
CREATE TABLE IF NOT EXISTS public.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES public.roles (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_user_role UNIQUE (user_id, role_id)
);

-- Indice per ottimizzare i join sui ruoli
CREATE INDEX IF NOT EXISTS ix_public_user_roles_role_id ON public.user_roles (role_id);

-- 3. Inserimento dei ruoli di sistema predefiniti
-- Ruolo 'user' con UUID fisso utilizzato dall'applicazione nel SupabaseAuthService
INSERT INTO public.roles (id, name, description)
VALUES ('0cc83a82-88f8-4ed9-9c92-ec9e09b266fd', 'user', 'Ruolo utente standard predefinito')
ON CONFLICT (id) DO NOTHING;

-- Ruolo 'admin'
INSERT INTO public.roles (name, description)
VALUES ('admin', 'Ruolo amministratore con accesso completo')
ON CONFLICT (name) DO NOTHING;
