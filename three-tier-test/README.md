# three-tier-test

Part of the AiGNITE Mobile Development Skills Suite.

## What it does

Enforces the Chrome to mirror to phone testing sequence with hard checkpoints. Each tier writes its result to `TEST_RESULTS.md`. The skill refuses to mark a build ready until all three pass within seventy-two hours.

## When it triggers

Phrases like "test my app", "verify the build", "is this ready to ship", "QA the mobile app".

## Install manually

```powershell
Copy-Item -Recurse "E:\AiGNITE\projects\custom-skills\three-tier-test" `
  -Destination "$env:USERPROFILE\.claude\skills\three-tier-test" -Force
```

## Composes with

Reads the endpoint list from `scripts/smoke-test.sh` produced by `mobile-app-scaffold`. Runs after `security-audit`. Required upstream of `app-store-submission`.

## License

See LICENSE at the repo root.
