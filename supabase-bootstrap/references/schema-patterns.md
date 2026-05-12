# Schema Patterns for AiGNITE Mobile Apps

One-line summary: Reusable Postgres schemas for the AiGNITE app shapes, including the three-tier intelligence pattern.

## Pattern 1: Habit tracker

```sql
create table profiles (
  id uuid primary key references auth.users(id),
  display_name text not null,
  created_at timestamptz default now()
);
alter table profiles enable row level security;
create policy "own_profile" on profiles for all using (auth.uid() = id) with check (auth.uid() = id);

create table habits (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  cadence text not null check (cadence in ('daily', 'weekly')),
  created_at timestamptz default now()
);
alter table habits enable row level security;
create policy "owner_habits" on habits for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table completions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  habit_id uuid not null references habits(id) on delete cascade,
  completed_on date not null,
  created_at timestamptz default now(),
  unique (user_id, habit_id, completed_on)
);
alter table completions enable row level security;
create policy "owner_completions" on completions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table streak_freezes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  earned_on date not null,
  used_on date,
  created_at timestamptz default now()
);
alter table streak_freezes enable row level security;
create policy "owner_freezes" on streak_freezes for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
```

Expected table count: 4.

## Pattern 2: Alert subscriber (FloodPulse-shape)

```sql
create table profiles (
  id uuid primary key references auth.users(id),
  display_name text,
  device_token text,
  created_at timestamptz default now()
);
alter table profiles enable row level security;
create policy "own_profile" on profiles for all using (auth.uid() = id) with check (auth.uid() = id);

create table subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  topic text not null,
  created_at timestamptz default now(),
  unique (user_id, topic)
);
alter table subscriptions enable row level security;
create policy "owner_subs" on subscriptions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create table preferences (
  user_id uuid primary key references auth.users(id) on delete cascade,
  quiet_hours_start time,
  quiet_hours_end time,
  channel text not null default 'push' check (channel in ('push', 'sms', 'email'))
);
alter table preferences enable row level security;
create policy "owner_prefs" on preferences for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
```

Expected table count: 3.

## Pattern 3: Three-tier intelligence (the AiGNITE shape)

The full three-tier MCP architecture. Each AiGNITE product fits this shape.

```sql
-- Tier 1: data ingestion. Raw rows pulled from external sources.
create table raw_events (
  id uuid primary key default gen_random_uuid(),
  source text not null,
  payload jsonb not null,
  ingested_at timestamptz default now()
);
-- service role only; no client policies.

-- Tier 2: intelligence layer. Processed rows ready for the API.
create table insights (
  id uuid primary key default gen_random_uuid(),
  source_event_id uuid references raw_events(id),
  topic text not null,
  body text not null,
  confidence float not null check (confidence >= 0 and confidence <= 1),
  published_at timestamptz default now()
);
alter table insights enable row level security;
create policy "public_read_insights" on insights
  for select using (published_at is not null);

-- Tier 3: per-user state. What the user has seen, bookmarked, dismissed.
create table user_insight_state (
  user_id uuid not null references auth.users(id) on delete cascade,
  insight_id uuid not null references insights(id) on delete cascade,
  seen_at timestamptz,
  bookmarked boolean default false,
  dismissed boolean default false,
  primary key (user_id, insight_id)
);
alter table user_insight_state enable row level security;
create policy "owner_state" on user_insight_state for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Stripe-side subscription tracking.
create table subscriptions (
  user_id uuid primary key references auth.users(id) on delete cascade,
  tier text not null default 'free' check (tier in ('free', 'paid')),
  stripe_customer_id text,
  stripe_subscription_id text,
  current_period_end timestamptz,
  updated_at timestamptz default now()
);
alter table subscriptions enable row level security;
create policy "own_subscription" on subscriptions for select using (auth.uid() = user_id);
```

Expected table count: 4.

This pattern composes with the `mcp-to-mobile` skill. The MCP server reads `insights`. The mobile app reads `insights` plus the user's `user_insight_state`. Stripe webhooks write `subscriptions` via the service role.

## How to pick a pattern

- One-user, one-feature loop: pattern 1.
- Alert subscriber with push delivery: pattern 2.
- MCP-fed product with paid tier: pattern 3.

If the app does not fit any pattern, start from pattern 3 and remove tables you do not need.
