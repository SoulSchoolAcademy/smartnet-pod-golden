-- repo: smartnet-pod-golden
-- path: 30-services/smartmail-api/sql/001_init.sql
create extension if not exists pg_trgm;
create extension if not exists "uuid-ossp";

create table if not exists users (
  id uuid primary key default uuid_generate_v4(),
  username text unique not null,
  email text unique,
  created_at timestamptz not null default now()
);

create table if not exists user_profile (
  user_id uuid primary key references users(id) on delete cascade,
  location text,
  tags text[],
  search_tsv tsvector generated always as (
    to_tsvector('english',
      coalesce(location,'') || ' ' || array_to_string(coalesce(tags,'{}')::text[], ' ')
    )
  ) stored
);
create index if not exists idx_user_profile_tsv on user_profile using gin(search_tsv);

create type smartmail_folder as enum ('inbox','sent','trash');

create table if not exists smartmail_thread (
  id uuid primary key,
  created_at timestamptz not null default now(),
  created_by uuid not null references users(id)
);

create table if not exists smartmail_message (
  id uuid primary key,
  thread_id uuid not null references smartmail_thread(id) on delete cascade,
  sender_id uuid not null references users(id),
  subject text not null default '',
  body text not null,
  created_at timestamptz not null default now(),
  search_tsv tsvector generated always as (
    to_tsvector('english', coalesce(subject,'') || ' ' || coalesce(body,''))
  ) stored
);
create index if not exists idx_smartmail_message_tsv on smartmail_message using gin(search_tsv);

create table if not exists smartmail_recipient (
  message_id uuid not null references smartmail_message(id) on delete cascade,
  user_id uuid not null references users(id),
  folder smartmail_folder not null default 'inbox',
  is_read boolean not null default false,
  created_at timestamptz not null default now(),
  primary key (message_id, user_id)
);
