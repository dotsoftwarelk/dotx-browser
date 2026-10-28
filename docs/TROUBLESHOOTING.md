# Troubleshooting

- Qt import failure: install `requirements.txt` and the OS libraries required by Qt/WebEngine. On Linux missing native libraries can prevent startup.
- No website response: verify connectivity, DNS and certificate validity; the app does not intentionally bypass certificate checks.
- Provider access: workspace shortcuts open websites only. Native connections are not available.
- History deletion: History → Clear history removes the app's history entries only; it does not clear WebEngine cookies or cache.
- Installer/updates: not yet available.
- If persistent state is corrupt, the prototype falls back to empty data; back up local data before troubleshooting. Application paths are chosen by Qt's `AppDataLocation`.
