-- SQL Setup per Supabase
-- Questo script crea le tabelle per i ruoli e inserisce l'utente amministratore iniziale.

-- Abilita l'estensione pgcrypto se non presente (necessaria per crypt)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Tabella per i ruoli applicativi nel schema public
CREATE TABLE IF NOT EXISTS public.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_public_roles_name ON public.roles (name);

-- 2. Tabella ponte per associare gli utenti ai ruoli
CREATE TABLE IF NOT EXISTS public.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users (id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES public.roles (id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT uq_user_role UNIQUE (user_id, role_id)
);

CREATE INDEX IF NOT EXISTS ix_public_user_roles_role_id ON public.user_roles (role_id);

-- 3. Inserimento dei ruoli di sistema predefiniti con UUID fissi
INSERT INTO public.roles (id, name, description)
VALUES
    ('0cc83a82-88f8-4ed9-9c92-ec9e09b266fd', 'user', 'Ruolo utente standard predefinito'),
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'admin', 'Ruolo amministratore con accesso completo')
ON CONFLICT (id) DO UPDATE SET description = EXCLUDED.description;

-- 4. Creazione dell'utente amministratore iniziale in auth.users
-- Nota: Usiamo l'estensione pgcrypto per cifrare la password in formato bcrypt
DO $$
DECLARE
    new_user_id UUID := 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22';
    admin_role_id UUID := 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';
BEGIN
    -- Inserimento dell'utente se non esiste
    IF NOT EXISTS (SELECT 1 FROM auth.users WHERE email = 'pietro.danieli.dev@gmail.com') THEN
        INSERT INTO auth.users (
            instance_id, id, aud, role, email, encrypted_password,
            email_confirmed_at, recovery_sent_at, last_sign_in_at,
            raw_app_meta_data, raw_user_meta_data,
            created_at, updated_at, confirmation_token, email_change,
            email_change_token_new, recovery_token, phone, phone_confirmed_at
        )
        VALUES (
            '00000000-0000-0000-0000-000000000000',
            new_user_id,
            'authenticated',
            'authenticated',
            'pietro.danieli.dev@gmail.com',
            extensions.crypt('explosionLink-117Test', extensions.gen_salt('bf')),
            now(), now(), now(),
            '{"provider": "email", "providers": ["email"]}',
            '{"display_name": "Pietro Danieli"}',
            now(), now(), '', '', '', '',
            '3921593130',
            now()
        );

        -- Inserimento dell'identità per l'utente (richiesto da Supabase Auth)
        INSERT INTO auth.identities (id, user_id, identity_data, provider, last_sign_in_at, created_at, updated_at)
        VALUES (
            new_user_id,
            new_user_id,
            format('{"sub": "%s", "email": "%s"}', new_user_id, 'pietro.danieli.dev@gmail.com')::jsonb,
            'email',
            now(), now(), now()
        );
    ELSE
        SELECT id INTO new_user_id FROM auth.users WHERE email = 'pietro.danieli.dev@gmail.com';
    END IF;

    -- Assegnazione del ruolo admin all'utente nel schema public
    INSERT INTO public.user_roles (user_id, role_id)
    VALUES (new_user_id, admin_role_id)
    ON CONFLICT (user_id, role_id) DO NOTHING;
END $$;

-- 5. Creazione Cliente Veneta Cucine
INSERT INTO public.clients (id, name, code)
VALUES ('e1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'Veneta Cucine', 'VENETA_CUCINE')
ON CONFLICT (code) DO NOTHING;

-- 6. Libreria Fori Standard
INSERT INTO public.hole_library (id, code, name, diameter_mm, depth_mm)
VALUES
    (gen_random_uuid(), 'RUBINETTO_35', 'Foro Rubinetto Ø35', 35, 20),
    (gen_random_uuid(), 'BUSSOLA_12', 'Bussola per Sottotop Ø12', 12, 15),
    (gen_random_uuid(), 'P_COTTURA', 'Foro Piano Cottura', NULL, 20),
    (gen_random_uuid(), 'LAVELLO_SOTTO', 'Foro Lavello Sottotop', NULL, 20)
ON CONFLICT (code) DO NOTHING;
