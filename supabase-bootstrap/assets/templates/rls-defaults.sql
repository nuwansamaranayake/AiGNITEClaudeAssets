-- AiGNITE RLS default policy block.
-- Apply per user-owned table by replacing {{TABLE_NAME}} with the actual name.
-- The table must have a user_id column referencing auth.users(id).

alter table {{TABLE_NAME}} enable row level security;

create policy "{{TABLE_NAME}}_owner_select" on {{TABLE_NAME}}
  for select using (auth.uid() = user_id);

create policy "{{TABLE_NAME}}_owner_insert" on {{TABLE_NAME}}
  for insert with check (auth.uid() = user_id);

create policy "{{TABLE_NAME}}_owner_update" on {{TABLE_NAME}}
  for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "{{TABLE_NAME}}_owner_delete" on {{TABLE_NAME}}
  for delete using (auth.uid() = user_id);
