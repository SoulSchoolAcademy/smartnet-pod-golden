-- Create table used by the register/verify endpoints
create table if not exists truths (
  id bigserial primary key,
  content_id text unique not null,
  content jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
