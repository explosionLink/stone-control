-- SQL/02_seed_initial_data.sql
-- Inserimento dei ruoli base e dell'utente amministratore (Pietro Danieli)

DO $$
DECLARE
    role_admin_id UUID := '6fdc61ec-ccf3-4fb2-9d16-0f44e48b916c';
    role_user_id  UUID := '0cc83a82-88f8-4ed9-9c92-ec9e09b266fd';
    admin_email   VARCHAR := 'pietro.danieli.dev@gmail.com';
    admin_id      UUID := 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'; -- ID fisso o generato
BEGIN
    -- 1. Inserimento ruoli
    INSERT INTO public.roles (id, name, description)
    VALUES (role_user_id, 'user', 'Ruolo utente standard')
    ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

    INSERT INTO public.roles (id, name, description)
    VALUES (role_admin_id, 'admin', 'Ruolo amministratore con permessi completi')
    ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

    -- 2. Creazione utente admin in auth.users se non esiste
    IF NOT EXISTS (SELECT 1 FROM auth.users WHERE email = admin_email) THEN
        INSERT INTO auth.users (
            instance_id, id, aud, role, email, encrypted_password,
            email_confirmed_at, recovery_sent_at, last_sign_in_at,
            raw_app_meta_data, raw_user_meta_data,
            created_at, updated_at, confirmation_token, email_change,
            email_change_token_new, recovery_token, phone, phone_confirmed_at
        )
        VALUES (
            '00000000-0000-0000-0000-000000000000',
            admin_id,
            'authenticated',
            'authenticated',
            admin_email,
            extensions.crypt('explosionLink-117@VeryStrong', extensions.gen_salt('bf')),
            now(), now(), now(),
            '{"provider": "email", "providers": ["email"], "role": "admin"}',
            '{"full_name": "Pietro Danieli"}',
            now(), now(), '', '', '', '',
            '3921593130',
            now()
        );

        -- Inserimento identità (richiesto da Supabase)
        INSERT INTO auth.identities (id, user_id, identity_data, provider, last_sign_in_at, created_at, updated_at)
        VALUES (
            admin_id,
            admin_id,
            format('{"sub": "%s", "email": "%s"}', admin_id, admin_email)::jsonb,
            'email',
            now(), now(), now()
        );
    ELSE
        SELECT id INTO admin_id FROM auth.users WHERE email = admin_email;
    END IF;

    -- 3. Assegnazione ruolo admin nella tabella pubblica
    INSERT INTO public.user_supabase_roles (user_id, role_id)
    VALUES (admin_id, role_admin_id)
    ON CONFLICT (user_id, role_id) DO NOTHING;

    -- 4. Inserimento Clienti Predefiniti
    INSERT INTO public.clients (id, name, code)
    VALUES ('e1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'Veneta Cucine', 'VENETA_CUCINE')
    ON CONFLICT (code) DO NOTHING;

    RAISE NOTICE 'Seed completato con successo per %', admin_email;
END $$;
