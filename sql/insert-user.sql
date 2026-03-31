INSERT INTO users (email, username, password_hash, role, is_email_verified, admin_approved)
VALUES
-- Primary seller (your original)
('seller1@mail.uc.edu', 'seller1', 'dev-only-hash', 'student', true, true),

-- More sellers
('seller2@mail.uc.edu', 'seller2', 'dev-only-hash', 'student', true, true),
('bookseller@mail.uc.edu', 'bookworm', 'dev-only-hash', 'student', true, true),

-- Buyer-style users
('buyer1@mail.uc.edu', 'buyer1', 'dev-only-hash', 'student', true, true),
('cheapfinder@mail.uc.edu', 'dealhunter', 'dev-only-hash', 'student', true, true),

-- Unverified email (should be blocked in app logic)
('newuser@mail.uc.edu', 'newuser', 'dev-only-hash', 'student', false, false),

-- Verified but NOT admin approved
('pending@mail.uc.edu', 'pendinguser', 'dev-only-hash', 'student', true, false),

-- Admin user
('admin@uc.edu', 'admin1', 'dev-only-hash', 'admin', true, true),

-- Another admin
('moderator@uc.edu', 'mod1', 'dev-only-hash', 'admin', true, true)

RETURNING id, username, email, role, is_email_verified, admin_approved;