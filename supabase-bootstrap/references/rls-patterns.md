# Row Level Security Patterns

One-line summary: Common RLS policies for AiGNITE mobile apps and the rules behind each one.

## Default posture

Every table starts with RLS enabled and zero policies. With no policies, no rows are visible. This is the safe default.

```sql
ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;
```

Now add policies one at a time, granting the minimum access needed.

## Pattern 1: User owns row

The most common AiGNITE pattern. Each row has a `user_id` column referencing `auth.users(id)`. The authenticated user sees and edits only their own rows.

```sql
CREATE POLICY "owner_select" ON my_table
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "owner_insert" ON my_table
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "owner_update" ON my_table
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "owner_delete" ON my_table
  FOR DELETE
  USING (auth.uid() = user_id);
```

## Pattern 2: Public read, owner write

For data the entire user base reads but only the creator edits. Example: a public alerts feed.

```sql
CREATE POLICY "public_read" ON alerts
  FOR SELECT
  USING (true);

CREATE POLICY "owner_write" ON alerts
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "owner_update" ON alerts
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "owner_delete" ON alerts
  FOR DELETE
  USING (auth.uid() = user_id);
```

## Pattern 3: Team membership

Rows belong to a team, not a single user. The user sees rows for teams they belong to.

```sql
CREATE POLICY "team_member_read" ON projects
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM team_members tm
      WHERE tm.team_id = projects.team_id
        AND tm.user_id = auth.uid()
    )
  );
```

## Pattern 4: Service role bypass

Server-side jobs run with the service role key, which bypasses RLS by design. Never expose this key to the client.

If a client-side function needs admin access (rare), wrap it in a `SECURITY DEFINER` function and grant execute carefully.

## Pattern 5: Read-only public surface

For tables exposed via REST to unauthenticated visitors (e.g. a marketing site reading a public feed).

```sql
CREATE POLICY "anon_read" ON public_feed
  FOR SELECT
  TO anon
  USING (published_at IS NOT NULL);
```

`TO anon` restricts the policy to the anon role. Authenticated users still need their own policy.

## Common mistakes

### Forgetting to enable RLS

`ALTER TABLE ... ENABLE ROW LEVEL SECURITY` is separate from creating policies. Without the alter, policies are advisory only and the table is fully open.

### Granting `USING (true)` to authenticated

This makes every row visible to every logged-in user. Use only when intended.

### Missing WITH CHECK on UPDATE

`USING` on update controls which rows are selectable for update. `WITH CHECK` controls what the new row can look like. Without the check, a user might be able to flip the `user_id` of a row they own to another user's id, transferring ownership.

### Recursive policies

A policy on table A that joins back to table A via a function call can cause infinite recursion. Test policies with `EXPLAIN ANALYZE` before shipping.

## How to test RLS

For every policy:

1. Curl the table as the anon role. Expect rows visible only via public policies.
2. Curl as a real user JWT. Expect only that user's rows.
3. Curl as a second user JWT. Expect zero overlap with the first.
4. Try to update another user's row. Expect rejection.

These four checks belong in `scripts/smoke-test.sh`.
