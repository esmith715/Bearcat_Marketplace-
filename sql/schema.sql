--============--
-- Extensions --
--============--
create extension if not exists pgcrypto;
create extension if not exists pg_trgm;


--=======--
-- Enums --
--=======--
do $$ begin
    create type user_role as enum ('student', 'admin');
exception when duplicate_object then null;
end $$;

do $$ begin
    create type token_type as enum ('refresh', 'email_verification', 'password_reset');
exception when duplicate_object then null;
end $$;

do $$ begin
    create type listing_type as enum ('book', 'furniture', 'misc');
exception when duplicate_object then null;
end $$;

do $$ begin
    create type listing_status as enum ('active', 'pending', 'sold', 'inactive');
exception when duplicate_object then null;
end $$;

do $$ begin
    create type report_status as enum ('open', 'reviewing', 'resolved', 'dismissed');
exception when duplicate_object then null;
end $$;


--========--
-- Tables --
--========--
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  username text not null unique,
  password_hash text not null,
  role user_role not null default 'student',
  is_email_verified boolean not null default false,
  admin_approved boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()

  -- UC email only should be enforced in the backend, but I think it's fine to also enforce
  -- it in the database just to be more safe
  -- constraint uc_email_only check (
  --   lower(email) like '%@uc.edu' OR lower(email) like '%@mail.uc.edu'
  -- )
);

create table if not exists tokens (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    token text not null,
    type token_type not null,
    expires_at timestamptz not null,
    created_at timestamptz not null default now(),
    used_at timestamptz
);

-- Postgres uses B-tree indexing by default
create index if not exists idx_users_role on users(role);

create table if not exists departments (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null
);

create table if not exists courses (
  id uuid primary key default gen_random_uuid(),
  department_id uuid not null references departments(id) on delete restrict,
  course_number text not null,
  title text not null,
  created_at timestamptz not null default now(),
  unique(department_id, course_number)
);

create table if not exists course_sections (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references courses(id) on delete cascade,
  term text not null,      -- "Spring 2026"
  section text,            -- "001"
  professor text,
  unique(course_id, term, section)
);

create table if not exists books (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  author text,
  isbn10 text unique,
  isbn13 text unique,
  created_at timestamptz not null default now()
);

create table if not exists course_required_books (
  course_id uuid not null references courses(id) on delete cascade,
  book_id uuid not null references books(id) on delete cascade,
  primary key(course_id, book_id)
);

create index if not exists idx_course_sections_prof on course_sections(professor);
create index if not exists idx_books_title on books(title);

create table if not exists listings (
  id uuid primary key default gen_random_uuid(),

  type listing_type not null,
  status listing_status not null default 'active',

  title text not null,
  description text,
  price_cents int not null check (price_cents >= 0),
  item_condition text,      -- allow "Other: ..." free text

  created_by uuid not null references users(id) on delete restrict,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  -- book-ish
  book_id uuid references books(id) on delete set null,
  course_id uuid references courses(id) on delete set null,
  isbn text,                 -- optional user-entered (even if no books row)

  -- furniture-ish
  measurements text,

  -- mark as purchased/sold
  sold_at timestamptz,
  sold_to uuid references users(id) on delete set null
);

create index if not exists idx_listings_feed on listings(status, created_at desc);
create index if not exists idx_listings_type_status on listings(type, status);
create index if not exists idx_listings_course on listings(course_id) where course_id is not null;
create index if not exists idx_listings_book on listings(book_id) where book_id is not null;
create index if not exists idx_listings_created_by on listings(created_by);

create table if not exists listing_owners (
  listing_id uuid not null references listings(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  owner_role text not null default 'owner',
  primary key(listing_id, user_id)
);

create table if not exists listing_images (
  id uuid primary key default gen_random_uuid(),
  listing_id uuid not null references listings(id) on delete cascade,
  image_path text not null,  -- e.g. "listing-images/<listing_id>/1.jpg"
  is_primary boolean not null default false,
  sort_order int not null default 0,
  created_at timestamptz not null default now()
);

create index if not exists idx_listing_images_listing on listing_images(listing_id, sort_order);
create unique index if not exists uq_listing_primary_image
  on listing_images(listing_id)
  where is_primary = true;

create table if not exists listing_reports (
  id uuid primary key default gen_random_uuid(),
  listing_id uuid not null references listings(id) on delete cascade,
  reporter_id uuid not null references users(id) on delete restrict,
  reason text not null,
  status report_status not null default 'open',
  created_at timestamptz not null default now(),
  reviewed_at timestamptz,
  reviewed_by uuid references users(id) on delete set null,
  resolution_notes text
);

create index if not exists idx_reports_queue on listing_reports(status, created_at desc);
create index if not exists idx_reports_listing on listing_reports(listing_id);

create table if not exists admin_action_log (
  id uuid primary key default gen_random_uuid(),
  admin_id uuid not null references users(id) on delete restrict,
  action text not null, -- 'listing_inactivated', 'book_added', etc.
  listing_id uuid references listings(id) on delete set null,
  report_id uuid references listing_reports(id) on delete set null,
  details jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_admin_log_created on admin_action_log(created_at desc);

create table if not exists notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  type text not null,
  payload jsonb not null,
  read_at timestamptz,
  created_at timestamptz not null default now()
);

create index if not exists idx_notifications_user on notifications(user_id, created_at desc);

--=============--
-- Messages    --
--=============--
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  from_user_id uuid not null references users(id) on delete restrict,
  to_user_id uuid not null references users(id) on delete restrict,
  content text not null,
  is_read boolean not null default false,
  created_at timestamptz not null default now(),
  read_at timestamptz
);

create index if not exists idx_messages_conversation
  on messages(from_user_id, to_user_id, created_at desc);

create index if not exists idx_messages_to_user_unread
  on messages(to_user_id, is_read) where is_read = false;

create index if not exists idx_messages_from_user
  on messages(from_user_id);

--- fuzzy search indexes ---
create index if not exists idx_listings_title_trgm
  on listings using gin (title gin_trgm_ops);

create index if not exists idx_listings_desc_trgm
  on listings using gin (description gin_trgm_ops);
