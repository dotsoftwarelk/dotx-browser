# Privacy

This prototype locally stores up to 1,000 visited page records (title and URL), bookmarks, search selection, and a persistent Qt WebEngine profile (which can include cookies, site data and cache). Addresses may contain personal or sensitive information. History can be cleared in the History dialog, but this does not remove cookies, cache, bookmarks or all website data. There is no private mode, full erase control, encryption guarantee or cloud synchronization.

Browsing sends data directly to sites visited. Search queries are sent to the selected search provider. Workspace buttons open provider websites, whose own privacy and login practices apply. Sign out on those sites; DOTX does not manage their connections or revoke provider credentials. The prototype implements no analytics, telemetry or Supabase backend; third-party sites may have their own telemetry.
