# CWE Reference

One-line summary: The CWE codes the AiGNITE security audit cites, with a one-paragraph plain-English description per code.

## CWE-20: Improper Input Validation

The product receives input but does not validate or incorrectly validates it. Inputs from outside the system are untrusted by definition.

## CWE-79: Cross-Site Scripting

The application takes user input and reflects it into a page without escaping. An attacker injects script that runs in another user's browser.

## CWE-89: SQL Injection

User input gets concatenated into a SQL string. The attacker submits SQL fragments that change the query.

## CWE-200: Information Exposure

The application sends a response that reveals sensitive information to a client that should not see it.

## CWE-287: Improper Authentication

The application does not verify the identity of the actor claiming to be the user.

## CWE-532: Insertion of Sensitive Information into Log File

The application writes tokens, passwords, or PII into log files, where logs leak via a separate channel.

## CWE-732: Incorrect Permission Assignment for Critical Resource

A resource is created with permissions broader than necessary. In a Supabase context this maps to default-open RLS policies.

## CWE-770: Allocation of Resources Without Limits

An operation allocates a costly resource without any rate or quota limit, enabling denial-of-service or runaway billing.

## CWE-798: Use of Hard-coded Credentials

The application contains hard-coded credentials in source.

## CWE-829: Inclusion of Functionality from Untrusted Control Sphere

The application includes code from a source outside its trust boundary. For mobile apps this maps to importing packages that do not exist on npm (typosquats) or packages with no maintainer.

## CWE-925: Improper Verification of Intent by Broadcast Receiver

A mobile component acts on an intent or deep link without verifying the caller's intent matches what the app expects.

## CWE-942: Permissive Cross-domain Policy with Untrusted Domains

CORS is configured to allow origins that should not have access.

## CWE-1188: Initialization of a Resource with an Insecure Default

A resource ships with a default that is insecure for production. Hard-coded staging URLs in a production bundle fit here.

## How the audit uses these codes

Every finding in `SECURITY_AUDIT.md` includes a CWE code, a severity tier, a file and line reference, and a recommended fix. The codes give the team a shared vocabulary and link to the upstream MITRE page for deeper reading.
