# mvp-design-framework

Part of the AiGNITE Mobile Development Skills Suite.

## What it does

Forces the five-step MVP discipline before any mobile app code gets written. Asks five sequential questions, validates each answer, and outputs a one-page MVP_SPEC.md the rest of the suite consumes.

The five questions:

1. Core function
2. Core loop
3. Accessory features (exactly three)
4. Surface area (seven screens or fewer)
5. Retention hook (a state, not a channel)

## When it triggers

Phrases like "design a new app", "MVP", "app idea", "scope a mobile app", "feature plan", "what should this app do".

## Hard constraints

- Refuses MVPs with more than seven screens
- Refuses "push notifications" as the retention hook answer
- Requires exactly three accessory features

## Install manually

```powershell
Copy-Item -Recurse "E:\AiGNITE\projects\custom-skills\mvp-design-framework" `
  -Destination "$env:USERPROFILE\.claude\skills\mvp-design-framework" -Force
```

## Composes with

Runs before `mobile-app-scaffold` and `mcp-to-mobile`.

## License

See LICENSE at the repo root.
