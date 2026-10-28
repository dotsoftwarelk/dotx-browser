# Existing DOTX Supabase project: security audit

A connected, already-existing project named `dotx-browser` was inspected read-only before a targeted security hardening migration. It is not yet used by this browser prototype; cloud sign-in and sync remain unimplemented. No user rows or provider credentials were read.

The existing project had six public tables: profiles, reading_list, user_bookmarks, user_devices, user_history_optin and user_settings. All six had RLS enabled and forced, with authenticated-role owner checks on SELECT, INSERT, UPDATE and DELETE. This is metadata inspection, not a live two-user isolation test; it is not a complete security audit.

**Issue fixed:** each of the six tables granted `TRUNCATE`, `TRIGGER` and `REFERENCES` to the authenticated role. PostgreSQL row-level security does not apply to TRUNCATE. Migration `20261028024417_dotx_restrict_authenticated_table_privileges` revoked those three privileges on the six tables without deleting data. A post-migration privilege query confirmed all three are false and SELECT remains granted; RLS remained enabled. Typical owner-scoped CRUD permissions were not intentionally changed. Existing applications that used the revoked non-CRUD privileges would be affected.

**Remaining:** the history and open-tabs tables can store sensitive browsing data. Owner policies inspect `auth.uid()` but do not themselves prove that a user's explicit history or tab-sync consent has been obtained. Do not connect this app to them until opt-in UX, server-side policy enforcement, retention, deletion, cross-user tests and a privacy/security review are complete. Auth redirect allowlist and external providers also need review before enabling account sign-in.

The checked-in migration is a hardening delta, not a complete fresh schema: it depends on the pre-existing migrations `dotx_cloud_schema`, `dotx_cloud_sync_v2`, and `dotx_cloud_sync_v3_device_tabs`, whose SQL was not available in this repository. Do not assume this file alone can recreate the project. No secrets or project keys are required by this prototype.
