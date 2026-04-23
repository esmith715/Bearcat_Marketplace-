WITH users_cte AS (
  SELECT id, email, username
  FROM users
  WHERE email IN (
    'seller1@mail.uc.edu',
    'seller2@mail.uc.edu',
    'bookseller@mail.uc.edu',
    'cheapfinder@mail.uc.edu'
  )
),
seller1 AS (
  SELECT id FROM users_cte WHERE email = 'seller1@mail.uc.edu'
),
seller2 AS (
  SELECT id FROM users_cte WHERE email = 'seller2@mail.uc.edu'
),
bookworm AS (
  SELECT id FROM users_cte WHERE email = 'bookseller@mail.uc.edu'
),
dealhunter AS (
  SELECT id FROM users_cte WHERE email = 'cheapfinder@mail.uc.edu'
),
inserted_listings AS (
  INSERT INTO listings (
    title,
    description,
    price_cents,
    type,
    item_condition,
    created_by,
    status,
    sold_at
  )
  VALUES
    ('Gaming Mouse', 'High-precision gaming mouse with RGB lighting.', 4999, 'misc', 'Like New', (SELECT id FROM seller1), 'active', NULL),
    ('Mechanical Keyboard', 'Blue switches, very clicky.', 7999, 'misc', 'Good', (SELECT id FROM seller1), 'active', NULL),
    ('Gaming Headset', 'Surround sound, noise cancelling mic.', 5999, 'misc', 'Good', (SELECT id FROM seller1), 'sold', now()),
    ('Office Chair', 'Ergonomic chair, adjustable height.', 12000, 'furniture', 'Good', (SELECT id FROM seller2), 'active', NULL),
    ('Wood Desk', 'Solid wood desk, some scratches.', 20000, 'furniture', 'Fair', (SELECT id FROM seller2), 'active', NULL),
    ('Bed Frame', 'Queen size metal frame.', 15000, 'furniture', 'Like New', (SELECT id FROM seller2), 'inactive', NULL),
    ('Intro to Algorithms', 'CLRS textbook, 3rd edition.', 4500, 'book', 'Used - Good', (SELECT id FROM bookworm), 'active', NULL),
    ('Database Systems', 'Covers SQL, indexing, transactions.', 3500, 'book', 'Used - Fair', (SELECT id FROM bookworm), 'active', NULL),
    ('Operating Systems', 'Includes notes and highlights.', 3000, 'book', 'Used - Acceptable', (SELECT id FROM bookworm), 'pending', NULL),
    ('Mini Fridge', 'Works perfectly, small dent on side.', 8000, 'misc', 'Good', (SELECT id FROM dealhunter), 'active', NULL),
    ('Lamp', 'Desk lamp with adjustable brightness.', 1500, 'misc', 'Like New', (SELECT id FROM dealhunter), 'active', NULL),
    ('Backpack', 'Used for one semester.', 2500, 'misc', 'Good', (SELECT id FROM dealhunter), 'sold', now()),
    ('Free Chair', 'You pick up. First come first serve.', 0, 'furniture', 'Fair', (SELECT id FROM seller2), 'active', NULL),
    ('Broken Monitor', 'For parts only.', 1000, 'misc', 'Poor', (SELECT id FROM seller1), 'active', NULL),
    ('Brand New iPad', 'Still sealed in box.', 45000, 'misc', 'New', (SELECT id FROM seller1), 'active', NULL)
  RETURNING id, title
)
INSERT INTO listing_images (listing_id, image_path, is_primary, sort_order)
SELECT id, '/mock/gaming-mouse.jpg', true, 0
FROM inserted_listings
WHERE title = 'Gaming Mouse'

UNION ALL
SELECT id, '/mock/mechanical-keyboard.jpg', true, 0
FROM inserted_listings
WHERE title = 'Mechanical Keyboard'

UNION ALL
SELECT id, '/mock/gaming-headset.jpg', true, 0
FROM inserted_listings
WHERE title = 'Gaming Headset'

UNION ALL
SELECT id, '/mock/office-chair.jpg', true, 0
FROM inserted_listings
WHERE title = 'Office Chair'

UNION ALL
SELECT id, '/mock/wood-desk.jpg', true, 0
FROM inserted_listings
WHERE title = 'Wood Desk'

UNION ALL
SELECT id, '/mock/bed-frame.jpg', true, 0
FROM inserted_listings
WHERE title = 'Bed Frame'

UNION ALL
SELECT id, '/mock/intro-to-algorithms.jpg', true, 0
FROM inserted_listings
WHERE title = 'Intro to Algorithms'

UNION ALL
SELECT id, '/mock/database-systems.jpg', true, 0
FROM inserted_listings
WHERE title = 'Database Systems'

UNION ALL
SELECT id, '/mock/operating-systems.jpg', true, 0
FROM inserted_listings
WHERE title = 'Operating Systems'

UNION ALL
SELECT id, '/mock/mini-fridge.jpg', true, 0
FROM inserted_listings
WHERE title = 'Mini Fridge'

UNION ALL
SELECT id, '/mock/lamp.jpg', true, 0
FROM inserted_listings
WHERE title = 'Lamp'

UNION ALL
SELECT id, '/mock/backpack.jpg', true, 0
FROM inserted_listings
WHERE title = 'Backpack'

UNION ALL
SELECT id, '/mock/free-chair.jpg', true, 0
FROM inserted_listings
WHERE title = 'Free Chair'

UNION ALL
SELECT id, '/mock/broken-monitor.jpg', true, 0
FROM inserted_listings
WHERE title = 'Broken Monitor'

UNION ALL
SELECT id, '/mock/brand-new-ipad.jpg', true, 0
FROM inserted_listings
WHERE title = 'Brand New iPad';