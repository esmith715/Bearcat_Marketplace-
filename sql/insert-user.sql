-- Create a sample user
INSERT INTO users (email, password_hash, role, is_email_verified, admin_approved)
VALUES ('seller1@mail.uc.edu', 'dev-only-hash', 'student', true, true)
RETURNING id;