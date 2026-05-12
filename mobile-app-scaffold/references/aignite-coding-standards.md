# AiGNITE Engineering Standards

One-line summary: Non-negotiable engineering rules every AiGNITE mobile project enforces from day one.

## The five non-negotiable rules

### 1. Root-cause fixes only

Before any bug fix:

- Curl the failing endpoint with a real token.
- Query the database directly to see actual row state.
- Read the server logs for the request in question.
- Document what is broken versus what the user reported.

Never patch a frontend display issue while the backend is broken. The display is a symptom. The backend is the cause. Fix the cause.

### 2. Smoke tests verify real business endpoints

Health-check-only smoke tests pass while the product is broken. They give false confidence. AiGNITE smoke tests:

- Curl every public API route with a real authentication token.
- Verify the response body is non-empty and structurally correct.
- Confirm each database table the route depends on exists with expected row counts.

If a developer adds a new endpoint, the smoke test breaks until they add a probe for it.

### 3. No silent mock data fallbacks outside dev

Mock data fallbacks in staging or production hide system failures. The user sees fake data. The team sees green dashboards. Real failures stay invisible for days.

Rule: in any environment other than `NODE_ENV=development`, an API failure surfaces as an error to the user. Never substitute fake data silently.

### 4. Verify table count after every migration

Partial migration failures are silent killers. Twenty tables go in, ten get created, the migration reports success, the frontend falls back to mocks. The team finds out five days later.

Every migration script ends with:

```sql
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
```

Compare the count to the expected number from the migration plan. If the counts do not match, abort and dump the partial state.

### 5. Maintain an API contract document

Every project keeps an `API_CONTRACT.md` at the root. It lists:

- Every URL the frontend calls
- The HTTP method
- The backend route handler
- The expected request shape
- The expected response shape

Before any deploy, verify the contract matches the actual code on both sides. The `supabase-bootstrap` skill generates the initial contract. The `security-audit` skill enforces it.

## Writing style for user-facing output

The skills in this suite produce output the user reads. Follow these rules in any text the user sees:

- Clear, simple language. Short sentences. Active voice.
- No em dashes. No semicolons in prose.
- No metaphors or cliches.
- No markdown asterisks for emphasis inside running prose.

Avoid these words: can, may, just, very, really, actually, certainly, probably, basically, could, maybe, delve, embark, enlightening, esteemed, shed light, craft, crafting, imagine, realm, game-changer, unlock, discover, skyrocket, revolutionize, disruptive, utilize, utilizing, dive deep, tapestry, illuminate, unveil, pivotal, intricate, elucidate, hence, furthermore, however, harness, exciting, groundbreaking, cutting-edge, remarkable, powerful, ever-evolving.

Markdown in technical reference files like this one is fine. The avoid list applies to user-facing prose the skill prints.

## The GoviHub post-mortem

GoviHub lost five days of project time because:

1. A migration script reported success.
2. Ten of twenty tables silently failed to create.
3. The frontend had mock data fallbacks enabled.
4. Users saw plausible but fake data for five days.
5. A QA engineer noticed a stale timestamp.

This is the reason for rules 3 and 4 above. Every AiGNITE skill bakes the lesson in.
