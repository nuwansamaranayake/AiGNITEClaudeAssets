# MCP Client Patterns

One-line summary: How the React Native client talks to an AiGNITE MCP server, with the JSON-RPC shape, auth, and error handling.

## Transport

AiGNITE MCP servers speak Streamable HTTP. The mobile client posts JSON-RPC envelopes to `<base>/mcp` and reads the response.

## Auth

Each request includes:

```
Content-Type: application/json
Accept: application/json, text/event-stream
X-User-Hash: <sha256 of supabase user id, truncated to 16 hex chars>
X-Client-Version: <app version>
```

No bearer token. The MCP servers rate-limit by hashed user id. The hash leaks no PII to the MCP server.

## Tool discovery

```typescript
const tools = await mcpClient.listTools();
// tools = [{ name: 'public_get_flood_alerts', description: '...', inputSchema: {...} }, ...]
```

## Tool call

```typescript
const result = await mcpClient.callTool('public_get_flood_alerts', {
  region: 'Harris County',
  hours_back: 24,
});

// result.content is an array. Each item is { type: 'text', text: '...' } or { type: 'image', data: '...' }.
```

## Error handling

The MCP server returns JSON-RPC errors with codes:

- -32601 method not found (tool name does not exist or is blocked)
- -32602 invalid params (input schema violation)
- -32603 internal error (server-side)
- -32000 to -32099 server-defined (rate limit, auth, quota)

The mobile client translates each to a user-facing error message via `lib/mcp-errors.ts`. Rate limit errors trigger the paywall on the free tier.

## Schema-driven forms

Each tool exposes an `inputSchema` (JSON Schema). The mobile client renders a form from the schema:

- `string` -> TextInput
- `number` -> TextInput with numeric keyboard
- `enum` -> Picker
- `boolean` -> Switch
- `object` -> grouped section
- `array` -> repeatable rows

The `assets/templates/mcp-tool-form.tsx.template` is the renderer.

## Caching

The client caches read-tool responses in `expo-secure-store` for thirty seconds. Same input plus same tool returns the cached response. The cache is per-user and cleared on logout.

## Rate limiting

Before each call, the client increments a counter in the `query_log` Supabase table. The counter is reset daily. The free tier allows three calls per twenty-four hours. The paid tier disables the check.

The check runs client-side for UX (instant feedback) and server-side via RLS (cannot be bypassed by tampering with the client). The Supabase RLS policy on `query_log` enforces the daily limit.

## Streaming results

Long-running tools (Cosmic Nexus readings, FloodPulse historical analysis) return Server-Sent Events. The client subscribes via `EventSource` and renders incremental updates:

```typescript
const stream = mcpClient.callToolStream('full_life_reading', { birth_data });
stream.on('chunk', (chunk) => updateUI(chunk));
stream.on('done', () => finalizeUI());
stream.on('error', (e) => showError(e));
```

## Versioning

The mobile client sends `X-Client-Version`. The MCP server matches against a min-version list. Below the minimum, the server returns a 426 Upgrade Required. The mobile app catches and shows a forced-update screen.

## What the client must never do

- Call any tool not in the whitelist for the chosen MCP server.
- Cache write or mutation responses.
- Log request bodies that contain PII.
- Retry indefinitely on 4xx errors.
- Send unhashed user identifiers to the MCP server.
