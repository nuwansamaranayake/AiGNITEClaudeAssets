# Expo Conventions for AiGNITE Mobile Apps

One-line summary: Expo Router file structure, naming rules, and navigation patterns AiGNITE mobile projects follow.

## Expo Router file structure

AiGNITE mobile apps use Expo Router with file-based routing. The `app/` directory drives navigation. One file per route.

```
app/
  _layout.tsx              # Root layout wrapping all screens
  (tabs)/                  # Tab group
    _layout.tsx            # Tab bar layout
    index.tsx              # Home tab
    alerts.tsx             # Alerts tab
    settings.tsx           # Settings tab
  (auth)/                  # Auth group
    _layout.tsx            # Auth flow layout
    sign-in.tsx
    sign-up.tsx
  [id].tsx                 # Dynamic detail screen
```

## Naming rules

- Route files: kebab-case (`sign-in.tsx`, not `SignIn.tsx`)
- Component files: PascalCase (`AlertCard.tsx`)
- Hook files: camelCase with `use` prefix (`useFloodData.ts`)
- Service files: kebab-case (`mcp-client.ts`)
- Style files: same base name as component, suffixed `.styles.ts`

## Navigation patterns

### Programmatic navigation

```typescript
import { router } from 'expo-router';

router.push('/(tabs)/alerts');
router.replace('/(auth)/sign-in');
router.back();
```

### Typed routes

Enable typed routes in `app.json`:

```json
{
  "expo": {
    "experiments": {
      "typedRoutes": true
    }
  }
}
```

### Auth-gated routes

Use a `_layout.tsx` at the group root to guard auth-required routes:

```typescript
import { Redirect, Stack } from 'expo-router';
import { useAuth } from '../../lib/auth';

export default function TabsLayout() {
  const { session } = useAuth();
  if (!session) return <Redirect href="/(auth)/sign-in" />;
  return <Stack />;
}
```

## Asset loading

Static assets live in `assets/`. Reference them via the `require()` syntax:

```typescript
<Image source={require('../../assets/logo.png')} />
```

Remote assets load via the standard React Native `Image` URI prop.

## Environment variables

Expo reads `EXPO_PUBLIC_*` variables at build time and bundles them into the client. Anything not prefixed stays server-only.

```
EXPO_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJxxx
SUPABASE_SERVICE_ROLE_KEY=eyJyyy
```

Never put service-role keys behind an `EXPO_PUBLIC_*` prefix. The audit skill flags this.

## Splash and icon

Both live in `assets/` with these required filenames:

- `icon.png` (1024x1024)
- `splash.png` (1284x2778, iPhone Pro Max baseline)
- `adaptive-icon.png` (1024x1024, Android)
- `favicon.png` (48x48, web)

EAS Build auto-generates the smaller sizes from these masters.

## Common pitfalls

- Forgetting `_layout.tsx` at the group root leaves screens unwrapped.
- Mixing kebab-case and PascalCase in `app/` breaks iOS case-sensitivity in production builds.
- Hardcoding the Supabase URL bypasses environment switching between dev and prod.
