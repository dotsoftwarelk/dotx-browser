# Troubleshooting

- Qt import failure: install `requirements.txt` and the OS libraries required by Qt/WebEngine. On Linux missing native libraries can prevent startup.
- No website response: verify connectivity, DNS and certificate validity; the app does not intentionally bypass certificate checks.
- Provider access: workspace shortcuts open websites; public GitHub search uses the REST API without sign-in. Authenticated provider connections are not available.
- Restoring tabs: opt in under Settings. URLs, including query strings, are saved locally; disabling the setting clears the saved list. Private windows are excluded.
- Site data: Settings can request cookie and HTTP-cache deletion, but other website storage may remain.
- History deletion: History → Clear history removes the app's history entries only; it does not clear WebEngine cookies or cache.
- A temporary unsigned development installer is available from the documented Windows CI run; there is no stable installer or automatic update system.
- If persistent state is corrupt, the prototype falls back to empty data; back up local data before troubleshooting. Application paths are chosen by Qt's `AppDataLocation`.
