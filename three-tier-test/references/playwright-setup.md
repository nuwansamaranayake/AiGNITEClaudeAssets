# Playwright Setup for Expo Web

One-line summary: How to wire Playwright into an Expo project so tier one runs over the running web build.

## Install

In the project root:

```
npm install --save-dev @playwright/test
npx playwright install chromium
```

Add to `package.json` scripts:

```json
"scripts": {
  "test:e2e": "playwright test"
}
```

## Config

Write `playwright.config.ts`:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8081',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: 'npx expo start --web --no-dev --minify',
    url: 'http://localhost:8081',
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
```

## Test pattern

Each top-level screen gets one test. The test asserts:

1. The screen renders without throwing.
2. Every API call during the render returns a 2xx.
3. No `console.error` fires.

Example `e2e/home.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';

test('home screen renders without console errors', async ({ page }) => {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  const apiCalls: { url: string; status: number }[] = [];
  page.on('response', (response) => {
    if (response.url().includes('/rest/v1/')) {
      apiCalls.push({ url: response.url(), status: response.status() });
    }
  });

  await page.goto('/');
  await page.waitForLoadState('networkidle');

  expect(errors).toEqual([]);
  for (const call of apiCalls) {
    expect(call.status, `API call to ${call.url}`).toBeGreaterThanOrEqual(200);
    expect(call.status, `API call to ${call.url}`).toBeLessThan(300);
  }
});
```

## Reusing the smoke test list

The skill reads `scripts/smoke-test.sh` and generates one Playwright test per endpoint listed there. New endpoint added to the smoke test means new Playwright test next run.

## CI integration

The audit and submission skills do not run tier one against a fresh CI container. Tier one runs locally on the developer's machine before they submit. The result lives in `TEST_RESULTS.md` and the timestamp is checked by downstream skills.

## Common pitfalls

### Bundler not ready

Expo's bundler can take thirty seconds on cold start. The Playwright config sets webServer.timeout to 120 seconds. If your machine needs longer, increase.

### Stale dist

`npx expo start --web --no-dev --minify` produces a minified bundle. The minifier sometimes drops a recent change if you do not rebuild. Run `npx expo export --platform web` between Playwright runs if changes do not appear.

### CORS in dev

Expo proxies API calls in dev. In production, the calls go direct. Tier one runs against the dev proxy, so a CORS bug in production might not surface. Tier three covers this.
