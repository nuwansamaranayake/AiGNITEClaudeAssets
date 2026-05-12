# AiGNITE Standard Privacy Language

One-line summary: The base privacy policy AiGNITE products use, parameterized for app-specific data flows.

## Why this exists

Every AiGNITE mobile product collects some user data: email for account creation, push tokens for notifications, and per-product data (location for FloodPulse, birth chart for Cosmic Nexus, etc). The privacy policy must list each data type, the purpose, the retention period, and the user's deletion rights.

The skill renders this template with the project-specific fields filled. It then publishes the rendered HTML to `contact.aigniteconsulting.ai/privacy/<slug>.html`.

## Template structure

The template lives at `assets/templates/privacy-policy.md.template`. Sections:

1. Introduction (project name, controller, contact)
2. Data we collect (table with type, purpose, retention)
3. How we use the data
4. Who we share with (Supabase, Stripe, Resend, Expo Push)
5. Your rights (access, deletion, portability)
6. Children (under 13 statement)
7. Changes to this policy
8. Contact

## Required project-specific fields

When rendering, the skill needs:

- `{{PROJECT_NAME}}`
- `{{CONTROLLER_ENTITY}}` (AiGNITE Consulting LLC for US products, AiGNITE Software Pvt Ltd for Sri Lankan products)
- `{{CONTACT_EMAIL}}` (typically privacy@aigniteconsulting.ai)
- `{{DATA_COLLECTION_TABLE}}` (generated from `store/data-collection.yaml`)
- `{{LAST_UPDATED_DATE}}`

## Data collection YAML structure

```yaml
data_types:
  - name: "Email address"
    purpose: "Account creation and authentication"
    retention: "Until account deletion"
    shared_with: ["Supabase Auth"]
  - name: "Push notification token"
    purpose: "Deliver alert notifications"
    retention: "Until token rotation or unsubscribe"
    shared_with: ["Expo Push Service", "APNs", "FCM"]
  - name: "Approximate location"
    purpose: "Show flood alerts for your region"
    retention: "30 days"
    shared_with: ["FloodPulse internal backend"]
```

## What the policy does not promise

- Zero data collection (every app collects something, the policy is honest about it)
- No third-party processors (every app uses Supabase, Stripe, or Resend; the policy lists them)
- Indefinite retention (every data type has a retention period stated)

## Where the policy lives

- Source: `store/privacy-policy.md` (in the project repo)
- Rendered HTML: `contact.aigniteconsulting.ai/privacy/<slug>.html`
- The submit script verifies the URL resolves to 200 before submitting to the store.
