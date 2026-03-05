-- SQL/03_test_data.sql
-- Inserimento di dati di test per lo sviluppo

DO $$
DECLARE
    order_id UUID := gen_random_uuid();
    client_id UUID := 'e1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33';
    poly_id UUID := gen_random_uuid();
BEGIN
    -- 1. Creazione di un ordine di test
    INSERT INTO public.orders (id, code, client_id)
    VALUES (order_id, 'TEST-ORDER-001', client_id)
    ON CONFLICT (code) DO NOTHING;

    -- 2. Creazione di un pezzo (poligono) di test
    INSERT INTO public.polygons (id, order_id, label, width_mm, height_mm, material, thickness_mm)
    VALUES (poly_id, order_id, 'TOP_PIANO_COTTURA', 1200, 600, 'Quarzo Nero', 20)
    ON CONFLICT (id) DO NOTHING;

    -- 3. Creazione di fori (lavorazioni) di test
    INSERT INTO public.holes (polygon_id, type, x_mm, y_mm, width_mm, height_mm)
    VALUES (poly_id, 'RETTANGOLARE', 300, 150, 560, 490);

    INSERT INTO public.holes (polygon_id, type, x_mm, y_mm, diameter_mm, depth_mm)
    VALUES (poly_id, 'CIRCOLARE', 100, 50, 35, 12);

    -- 4. Inserimento in libreria fori
    INSERT INTO public.hole_library (name, type, diameter_mm, depth_mm)
    VALUES ('BUSSOLA_12', 'CIRCOLARE', 12, 10)
    ON CONFLICT (name) DO NOTHING;

    RAISE NOTICE 'Dati di test inseriti con successo.';
END $$;
