# AiGNITE MCP Catalog

One-line summary: Every AiGNITE MCP server in production with its public URL, full tool list, and the public-safe subset the mobile skill is allowed to expose.

## Beacon GoM

Type: alert-style (oil and gas operator incidents in the Gulf of Mexico).
Public URL: `https://beacon.aigniteconsulting.ai/mcp`
Region: Houston VPS.
Default tier: free (3 queries/day), paid ($9.99/mo).
Shortcut keyword: `beacon-gom`.

Public-safe tools:

- `public_get_operator_summary` - summary of operator-level incident history.
- `public_list_recent_incidents` - recent incidents in a region.
- `public_search_incidents` - search by operator, region, or date range.

Not exposed:

- Any tool starting with `admin_`, `internal_`, `write_`.

## RegScope

Type: alert-style (federal regulatory changes).
Public URL: `https://regscope.aigniteconsulting.ai/mcp`
Region: Houston VPS.
Default tier: free (3 queries/day), paid ($14.99/mo).
Shortcut keyword: `regscope`.

Public-safe tools:

- `public_get_rule_details` - details on a specific Federal Register rule.
- `public_list_recent_rules` - recent rules by agency or topic.
- `public_search_federal_register` - keyword search.

## RecallWatch

Type: alert-style (product recalls).
Public URL: `https://recallwatch.aigniteconsulting.ai/mcp`
Region: Houston VPS.
Default tier: free (3 queries/day), paid ($7.99/mo).
Shortcut keyword: `recallwatch`.

Public-safe tools:

- `public_list_recalls`
- `public_search_recalls`
- `public_get_recall_details`

## FloodPulse

Type: alert-style (flood and water-level monitoring).
Public URL: `https://floodpulse.aigniteconsulting.ai/mcp`
Region: Houston VPS.
Default tier: free (3 queries/day), paid ($4.99/mo).
Shortcut keyword: `floodpulse`.

Public-safe tools:

- `public_check_flood_zone` - flood zone status for a coordinate.
- `public_get_flood_alerts` - active flood alerts by region.
- `public_get_water_levels` - current gauge readings.

## AirShield

Type: alert-style (air quality plus facility compliance).
Public URL: `https://airshield.aigniteconsulting.ai/mcp`
Region: Houston VPS.
Default tier: free (3 queries/day), paid ($4.99/mo).
Shortcut keyword: `airshield`.

Public-safe tools:

- `public_get_air_quality`
- `public_get_aqi_forecast`
- `public_get_facility_compliance`

## Cosmic Nexus

Type: request-response (Vedic astrology readings).
Public URL: `https://beta.cosmicnexus.ai/mcp`
Region: Mumbai VPS.
Default tier: free (3 readings/day), paid ($19.99/mo).
Shortcut keyword: `cosmic-nexus`.

Public-safe tools:

- `general_reading`
- `full_life_reading`
- `compatibility_analysis`
- `analyze_career`
- `analyze_health`
- `analyze_marriage`
- `analyze_spirituality`
- `analyze_wealth`
- `longevity_analyze`
- `ask_astrology_question`
- `followup_question`

Not exposed:

- `alert_admin`, `evaluate_sensitivity`, `mark_order_failed`, `send_delivery_email`, `upload_reading`, `list_users`, `get_user_detail`, `list_issues`, `resolve_issue`, `get_analytics`, `longevity_get_methodology` (admin or back-office).

## How the whitelist is enforced

The mobile MCP client lists tools by calling `tools/list`. The skill then intersects the response with the whitelist above. Any tool not on the list is silently filtered out before rendering screens.

The whitelist is updated by the skill author, not by the runtime. A tool added to the MCP server does not automatically appear in the mobile app. This is intentional. New tools require a security review before public exposure.

## Audit table

Each MCP server in production has a `usage_audit` table that logs every call from the mobile app with: timestamp, user_id, tool_name, status_code, response_time_ms. The mobile app sends a hashed user_id with each request so the MCP server can rate-limit per user without storing PII.
