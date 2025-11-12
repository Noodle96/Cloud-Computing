INSERT INTO tasks (title, description, status, tags)
VALUES
    ('Comprar fruta', 'Manzanas y naranjas', 'pending', ARRAY['super', 'cocina']),
    ('Estudiar FastAPI', 'CRUD y validaciones', 'in_progress', ARRAY['dev','python']);
