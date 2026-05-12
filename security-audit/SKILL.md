---
name: security-audit
description: Runs the three-pass AiGNITE security audit on any mobile or backend project before deployment. Identifies vulnerabilities, applies fixes, and re-audits to catch regressions introduced by the fixes. Produces a tier-classified SECURITY_AUDIT.md with CWE references. Use this skill whenever the user mentions a security audit, pre-deploy check, asking whether code is safe to ship, vulnerability check, security review, or auditing an app, even if they do not name the skill by name.
---

# security-audit

## Purpose

Find the security gaps that block a clean TestFlight or Play Store submission. Fix the Critical and High issues. Confirm the fixes did not introduce new gaps. Hand back a signed audit document.

## When to trigger

Trigger on these user phrases. Match loosely.

- "security audit"
- "pre-deploy check"
- "is this safe to ship"
- "check for vulnerabilities"
- "security review"
- "audit my app"
- "OWASP check"
- "ready for App Store"

## Behavior: three passes

### Pass 1: identify

Scan the entire project. Produce findings tagged Critical, High, Medium, Low with CWE references. Write to `SECURITY_AUDIT.md`.

Checks the skill runs:

- Hard-coded secrets in source (CWE-798)
- Exposed environment variables in client bundles (CWE-200)
- Missing server-side validation on API routes (CWE-20)
- Default-open database policies (CWE-732)
- Missing or inconsistent auth middleware (CWE-287)
- Hallucinated package imports (CWE-829)
- Console logs leaking request bodies or tokens (CWE-532)
- Missing rate limiting on expensive operations (CWE-770)
- CORS misconfigurations (CWE-942)
- SQL injection patterns in raw queries (CWE-89)
- XSS in user-supplied content paths (CWE-79)
- Insecure deep linking handlers (CWE-925)
- Hard-coded API URLs pointing at staging (CWE-1188)

### Pass 2: fix

Implement fixes for every Critical and High finding. Apply Medium and Low fixes if the user opts in. After each fix, update `SECURITY_AUDIT.md` with the resolution and the diff link.

### Pass 3: re-audit

Run the full scan again from a fresh context. Compare to pass 1. Flag any new finding introduced by a pass-2 fix. The most common new findings: a fix that broadens an auth check, a fix that adds a console log, a fix that imports a new package without validating it.

If pass 3 surfaces new findings, fix them, run a fourth pass. Stop when a pass introduces zero new Critical or High findings.

## Output: SECURITY_AUDIT.md

The skill writes `SECURITY_AUDIT.md` at the project root using the template in `assets/templates/SECURITY_AUDIT.md.template`. The document includes:

- Project name and audit date
- Pass-1 findings table
- Pass-2 resolution log
- Pass-3 regression check
- Final tier counts
- Sign-off block

The audit fails (returns non-zero) until every Critical and High finding has a resolution.

## Refusals

Refuse to mark an audit complete if:

- Any Critical finding remains unresolved.
- Any High finding remains unresolved without explicit user override.
- Pass 3 surfaced a Critical or High introduced by a pass-2 fix.

## Composes with

- Runs after `supabase-bootstrap` to verify the schema and policies.
- Runs before `app-store-submission`. The submission skill refuses if no recent audit exists.
- The `mcp-to-mobile` skill invokes this skill in step 9.

## References

- [references/vulnerability-patterns.md](references/vulnerability-patterns.md) - the full taxonomy with examples.
- [references/aignite-security-baseline.md](references/aignite-security-baseline.md) - what AiGNITE products must meet before launch.
- [references/cwe-reference.md](references/cwe-reference.md) - the CWE codes cited.
