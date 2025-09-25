-- 1) Types
create type movement_dir as enum ('north','south','east','west','stationary');
create type user_role as enum ('admin','viewer');

-- 2) Profiles (mirrors auth.users)
create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text unique,
  role user_role not null default 'viewer',
  created_at timestamptz not null default now()
);
alter table public.profiles enable row level security;

-- Auto-populate profiles on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.profiles (user_id, email)
  values (new.id, new.email);
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();

-- 3) Detections (historical events)
create table if not exists public.detections (
  id bigserial primary key,
  ts timestamptz not null default now(),
  count int not null check (count >= 0),
  movement movement_dir not null,
  fps numeric(5,2) not null,
  source text not null check (source in ('rtsp','sample','mock')),
  raw jsonb,                 -- optional: extra payload per tick
  created_by uuid,           -- optional: service user id if you set one
  created_at timestamptz not null default now()
);
create index if not exists idx_detections_ts on public.detections (ts desc);
alter table public.detections enable row level security;

-- 4) Settings (admin-only)
create table if not exists public.settings (
  id smallint primary key default 1,  -- single-row settings
  rtsp_url text,
  sample_video_path text,
  interval_ms int default 1000,
  max_cache_minutes int default 30,
  updated_at timestamptz not null default now()
);
alter table public.settings enable row level security;

-- RLS POLICIES

-- PROFILES
-- Users can read their own profile
create policy "profiles: users read own"
on public.profiles for select
to authenticated
using (user_id = auth.uid());

-- Admins can read all profiles
create policy "profiles: admin read all"
on public.profiles for select
to authenticated
using (
  exists (select 1 from public.profiles p
          where p.user_id = auth.uid() and p.role = 'admin')
);

-- Only admins can update roles/emails
create policy "profiles: admin update"
on public.profiles for update
to authenticated
using (
  exists (select 1 from public.profiles p
          where p.user_id = auth.uid() and p.role = 'admin')
);

-- DETECTIONS
-- Insert: only service role (your backend) can write events
create policy "detections: service insert"
on public.detections for insert
to public
with check (auth.role() = 'service_role');

-- Read: authenticated users can read; anon cannot
create policy "detections: auth select"
on public.detections for select
to authenticated
using (true);

-- Optional: delete retention window (admin only)
create policy "detections: admin delete"
on public.detections for delete
to authenticated
using (
  exists (select 1 from public.profiles p
          where p.user_id = auth.uid() and p.role = 'admin')
);

-- SETTINGS
-- Admins can read/update settings
create policy "settings: admin read"
on public.settings for select
to authenticated
using (
  exists (select 1 from public.profiles p
          where p.user_id = auth.uid() and p.role = 'admin')
);

create policy "settings: admin upsert"
on public.settings for insert
to authenticated
with check (
  exists (select 1 from public.profiles p
          where p.user_id = auth.uid() and p.role = 'admin')
);

create policy "settings: admin update"
on public.settings for update
to authenticated
using (
  exists (select 1 from public.profiles p
          where p.user_id = auth.uid() and p.role = 'admin')
);

-- Optional: read-optimized view for aggregations
create or replace view public.detections_last_15m as
select *
from public.detections
where ts >= now() - interval '15 minutes';

-- Optional: function for admins to purge old data
create or replace function public.purge_detections_older_than(days int)
returns int language sql security definer as $$
  delete from public.detections
  where ts < now() - (days || ' days')::interval;
  select count(*)::int;
$$;