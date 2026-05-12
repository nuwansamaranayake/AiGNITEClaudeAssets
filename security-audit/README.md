# security-audit

Part of the AiGNITE Mobile Development Skills Suite.

## What it does

Runs the three-pass AiGNITE security audit on any mobile or backend project. Identifies vulnerabilities (Critical/High/Medium/Low with CWE codes), applies fixes for Critical and High by default, then re-audits to confirm no new issues were introduced by the fixes. Produces `SECURITY_AUDIT.md` at the project root.

## When it triggers

Phrases like "security audit", "pre-deploy check", "is this safe to ship", "vulnerability check", "security review".

## Hard rule

Refuses to mark an audit complete if any Critical or High finding remains open. Refuses if pass 3 introduced a new Critical or High.

## Install manually

```powershell
Copy-Item -Recurse "E:\AiGNITE\projects\custom-skills\security-audit" `
  -Destination "$env:USERPROFILE\.claude\skills\security-audit" -Force
```

## Composes with

Runs before `app-store-submission`. The submission skill checks for a SECURITY_AUDIT.md dated within seven days.

## License

See LICENSE at the repo root.
