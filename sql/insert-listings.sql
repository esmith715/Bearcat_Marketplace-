-- Insert listings using user id
WITH u AS (
  SELECT id
  FROM users
  WHERE email = 'seller1@mail.uc.edu'
)
INSERT INTO listings (title, description, price_cents, type, created_by)
VALUES
  ('Gaming Mouse', 'High-precision gaming mouse with RGB lighting.', 4999, 'misc', (SELECT id FROM u)),
  ('Mechanical Keyboard', 'Durable mechanical keyboard with blue switches.', 7999, 'misc', (SELECT id FROM u)),
  ('Gaming Headset', 'Surround sound gaming headset with noise cancellation.', 5999, 'misc', (SELECT id FROM u));